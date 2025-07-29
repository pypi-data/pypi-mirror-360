# -*- coding: utf-8 -*-
# Copyright (c) 2025 University Medical Center Göttingen, Germany.
# All rights reserved.
#
# Patent Pending: DE 10 2024 112 939.5
# SPDX-License-Identifier: LicenseRef-Proprietary-See-LICENSE
#
# This software is licensed under a custom license. See the LICENSE file
# in the root directory for full details.
#
# **Commercial use is prohibited without a separate license.**
# Contact MBM ScienceBridge GmbH (https://sciencebridge.de/en/) for licensing.


import json
import os
import platform
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, Literal, Dict, Any, List, Optional, Sequence, Tuple

from matplotlib import pyplot as plt
from ome_zarr.reader import Reader
from ome_zarr.writer import write_image
from ome_zarr.io import parse_url
import xarray as xr
import zarr
import numcodecs

import numpy as np
import tifffile
import torch

from sarcasm.exceptions import MetaDataError
from sarcasm.meta_data_handler import ImageMetadata
from sarcasm.utils import Utils


class SarcAsM:
    """
    Base class for sarcomere structural and functional analysis.

    Parameters
    ----------
    filepath : str | os.PathLike
        Path to the TIFF of OME-ZARR file for analysis.
    restart : bool, optional
        If True, deletes existing analysis and starts fresh (default: False).
    pixelsize : float or None, optional
        Physical pixel size in micrometres (µm). If None, the class tries to
        extract it from file metadata; otherwise it must be provided manually.
    frametime : float or None, optional
        Time between frames in seconds. If None, the class tries to extract it
        from file metadata; otherwise it must be provided manually.
    channel : int or None, optional
        Channel index that contains the sarcomere signal in multicolour stacks
        (default: None).
    axes : str or None, optional
        Explicit order of image dimensions (e.g. ``'TXYC'`` or ``'YX'``).
        If None, the order is auto-detected from OME-XML, ImageJ tags or shape
        heuristics; this is the recommended mode when the GUI offers a
        drop-down override.
    auto_save : bool, optional
        Automatically save analysis results when True (default: True).
    use_gui : bool, optional
        Enable GUI-mode behaviour (default: False).
    device : Union[torch.device, Literal['auto']], optional
        PyTorch computation device. ``'auto'`` selects CUDA/MPS if available
        (default: 'auto').
    **info : Any
        Additional user-supplied metadata key-value pairs
        (e.g. ``cell_line='wt'``).

    Attributes
    ----------
    filepath : str
        Absolute path to the input file (TIFF) or directory (OME-ZARR).
    ome_path : str
        Absolute path to the OME-Zarr store. Same as filepath for OME-ZARR
    is_ome_zarr_input : bool
        Whether the input is an OME-ZARR directory or a TIFF file.
    metadata : ImageMetadata
        Image metadata
    device : torch.device
        PyTorch device on which computations are performed.

    Dynamic Attributes (loaded on demand)
    -------------------------------------
    image : ndarray
        Image with axes in internal order (YX | TYX | ZYX).
    zbands : ndarray
        Z-band mask.
    zbands_fast_movie : ndarray
        Z-band mask for the high-temporal-resolution movie.
    mbands : ndarray
        M-band mask.
    orientation : ndarray
        Sarcomere orientation map.
    cell_mask : ndarray
        Cell mask.
    sarcomere_mask : ndarray
        Sarcomere mask.
    """

    metadata: ImageMetadata

    def __init__(
            self,
            filepath: Union[str, os.PathLike],
            restart: bool = False,
            pixelsize: Union[float, None] = None,
            frametime: Union[float, None] = None,
            channel: Union[int, None] = None,
            axes: Union[str, None] = None,
            auto_save: bool = True,
            use_gui: bool = False,
            device: Union[torch.device, Literal['auto', 'mps', 'cuda', 'cpu']] = 'auto',
            **info: Dict[str, Any]
    ):
        # Configuration
        self.auto_save = auto_save
        self.use_gui = use_gui
        self.info = info
        self.device = Utils.get_device() if device == "auto" else torch.device(device)
        self.model_dir = Utils.get_models_dir()

        # Convert to absolute path and validate
        self.filepath = os.path.abspath(str(filepath))
        self._validate_input_file()

        # Determine file type and set paths accordingly
        if self._is_ome_zarr(self.filepath):
            # Input is OME-ZARR: filepath and ome_path are the same
            self.ome_path = self.filepath
            self.is_ome_zarr_input = True

            # Handle restart for OME-ZARR input
            if restart:
                # For OME-ZARR input, restart means clearing analysis data only
                # not deleting the entire store
                self._clear_analysis_data()

        elif self._is_tiff_file(self.filepath):
            # Input is TIFF: create corresponding OME-ZARR path
            self.ome_path = os.path.splitext(self.filepath)[0] + ".ome.zarr"
            self.is_ome_zarr_input = False

            # Handle restart for TIFF input
            if restart and os.path.exists(self.ome_path):
                shutil.rmtree(self.ome_path)

            # Convert TIFF to OME-ZARR if needed
            if not os.path.exists(self.ome_path):
                self._convert_tiff_to_ome_zarr_with_metadata()

        else:
            raise ValueError(f"Unsupported file format: {self.filepath}")

        # Initialize metadata with deferred loading pattern
        self._initialize_metadata(
            pixelsize_override=pixelsize,
            frametime_override=frametime,
            channel_override=channel,
            axes_override=axes
        )

    def _is_ome_zarr(self, path: str) -> bool:
        """Check if the given path is an OME-ZARR directory."""
        if not os.path.isdir(path):
            return False

        # Check for required OME-ZARR metadata files
        zattrs_path = os.path.join(path, '.zattrs')
        zgroup_path = os.path.join(path, '.zgroup')

        return os.path.exists(zattrs_path) or os.path.exists(zgroup_path)

    def _is_tiff_file(self, path: str) -> bool:
        """Check if the given path is a TIFF file."""
        if not os.path.isfile(path):
            return False

        # Check file extension
        _, ext = os.path.splitext(path.lower())
        return ext in ['.tif', '.tiff']

    def _validate_input_file(self):
        """Validate the input file exists and is of supported format."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Input file not found: {self.filepath}")

        if not (self._is_ome_zarr(self.filepath) or self._is_tiff_file(self.filepath)):
            raise ValueError(f"Unsupported file format. Expected TIFF or OME-ZARR: {self.filepath}")

    def _convert_tiff_to_ome_zarr_with_metadata(
            self,
            pixelsize_override: Optional[float] = None,
            frametime_override: Optional[float] = None,
            channel_override: Optional[Union[int, str]] = None,
            axes_override: Optional[str] = None
    ):
        """Convert TIFF file to OME-ZARR format using enhanced metadata extraction."""
        import tifffile
        from ome_zarr.io import parse_url
        from ome_zarr.writer import write_image
        import zarr

        # Read TIFF file and extract metadata
        with tifffile.TiffFile(self.filepath) as tif:
            series = tif.series[0]  # Assume first series

            # Use your existing axis determination
            if axes_override:
                self._validate_axes(axes_override)
                axes = axes_override.upper()
            else:
                axes = self._determine_axes(series, tif)

            # Read image data
            image_data = series.asarray()

            # Apply channel selection if needed
            if channel_override is not None:
                image_data, axes = self._select_channel(image_data, axes, channel_override)

            # Permute to internal order using your existing function
            image_data = self._permute_to_internal(image_data, axes)

            # Extract metadata using your enhanced harvest function
            self.metadata = self._harvest_metadata(
                series, tif, axes,
                override_pixelsize=pixelsize_override,
                override_frametime=frametime_override
            )

        # Create OME-ZARR store
        store = parse_url(self.ome_path, mode="w").store
        root = zarr.group(store=store)

        # Write image data to OME-ZARR using NGFF axes
        write_image(
            image=image_data,
            group=root,
            axes=self.metadata.get_axes_string_lowercase(),
            storage_options=dict(chunks="auto")
        )

        # Store the complete metadata in OME-ZARR attributes
        root.attrs['sarcasm_metadata'] = self.metadata.to_dict()

        # Store NGFF multiscale metadata
        root.attrs['multiscales'] = [self.metadata.get_ngff_multiscale_metadata()]

        print(f"Converted TIFF to OME-ZARR with enhanced metadata: {self.ome_path}")

    def _initialize_metadata(
            self,
            pixelsize_override: Optional[float] = None,
            frametime_override: Optional[float] = None,
            channel_override: Optional[Union[int, str]] = None,
            axes_override: Optional[str] = None
    ):
        """Initialize metadata using lazy loading pattern with NGFF compatibility."""

        # For OME-ZARR input, try to load existing metadata first
        if self.is_ome_zarr_input and os.path.exists(self.ome_path):
            try:
                import zarr
                root = zarr.open_group(self.ome_path, mode="r")

                if "sarcasm_metadata" in root.attrs:
                    # Load existing SarcAsM metadata
                    stored_metadata = root.attrs["sarcasm_metadata"]
                    self.metadata = ImageMetadata.from_dict(stored_metadata)

                    # Apply any user overrides
                    self._apply_metadata_overrides(
                        pixelsize_override, frametime_override,
                        channel_override, axes_override
                    )
                    return

            except Exception as e:
                print(f"Warning: Could not load existing OME-ZARR metadata: {e}")

        # Create minimal metadata for deferred loading
        # This allows the class to be instantiated without reading the full image
        self.metadata = ImageMetadata(
            file_name=os.path.basename(self.filepath),
            file_path=self.filepath,
            pixelsize=pixelsize_override,
            frametime=frametime_override,
            channel=channel_override,
            axes=axes_override or "",  # Will be determined when image is first read
        )

        # Add user info
        self.metadata.add_user_info(**self.info)

    def _apply_metadata_overrides(
            self,
            pixelsize_override: Optional[float] = None,
            frametime_override: Optional[float] = None,
            channel_override: Optional[Union[int, str]] = None,
            axes_override: Optional[str] = None
    ):
        """Apply user-provided overrides to existing metadata."""
        overrides_applied = False

        if pixelsize_override is not None:
            self.metadata.pixelsize = pixelsize_override
            overrides_applied = True

        if frametime_override is not None:
            self.metadata.frametime = frametime_override
            overrides_applied = True

        if channel_override is not None:
            self.metadata.channel = channel_override
            overrides_applied = True

        if axes_override is not None:
            self._validate_axes(axes_override)
            self.metadata.axes = axes_override.upper()
            overrides_applied = True

        # Update user info
        if self.info:
            self.metadata.add_user_info(**self.info)
            overrides_applied = True

        # Regenerate NGFF metadata if physical parameters changed
        if overrides_applied:
            self.metadata.update_physical_parameters(
                self.metadata.pixelsize, self.metadata.frametime
            )

            # Save updated metadata if auto_save is enabled
            if self.auto_save and hasattr(self, 'root'):
                self._save_metadata()

    def _bootstrap_store(self, channel_override=None, pixelsize_override=None, frametime_override=None):
        """Bootstrap OME-ZARR store with proper metadata initialization."""

        # If OME-ZARR doesn't exist, create it from TIFF
        if not os.path.exists(self.ome_path):
            if self.is_ome_zarr_input:
                raise FileNotFoundError(f"OME-ZARR file not found: {self.ome_path}")
            else:
                # Convert TIFF to OME-ZARR with full metadata extraction
                self._convert_tiff_to_ome_zarr_with_metadata(
                    pixelsize_override=pixelsize_override,
                    frametime_override=frametime_override,
                    channel_override=channel_override
                )

        # Open the OME-ZARR store
        import zarr
        self.root = zarr.open_group(self.ome_path, mode="r+")

        # Update metadata with extracted information if it was minimal
        if not self.metadata.axes or self.metadata.axes == "":
            self._extract_and_update_metadata_from_store()

    def _extract_and_update_metadata_from_store(self):
        """Extract complete metadata from OME-ZARR store."""
        try:
            # Load from sarcasm_metadata if available
            if "sarcasm_metadata" in self.root.attrs:
                stored_metadata = self.root.attrs["sarcasm_metadata"]
                complete_metadata = ImageMetadata.from_dict(stored_metadata)

                # Preserve any user overrides from initialization
                if self.metadata.pixelsize is not None:
                    complete_metadata.pixelsize = self.metadata.pixelsize
                if self.metadata.frametime is not None:
                    complete_metadata.frametime = self.metadata.frametime
                if self.metadata.channel is not None:
                    complete_metadata.channel = self.metadata.channel

                # Update user info
                complete_metadata.add_user_info(**self.metadata.user_info)

                self.metadata = complete_metadata

            else:
                # Extract basic metadata from OME-ZARR structure
                self._extract_basic_metadata_from_omezarr()

        except Exception as e:
            print(f"Warning: Could not extract metadata from OME-ZARR: {e}")
            # Keep the minimal metadata created during initialization

    @staticmethod
    def _extract_axes_from_tiff(series, tif: tifffile.TiffFile) -> List[Dict[str, str]]:
        """
        Return a list of axes dictionaries following the NGFF format.

        Returns
        -------
        List[Dict[str, str]]
            List of axis dictionaries with 'name', 'type', and optionally 'unit' keys
            following the OME-NGFF specification format.

        Raises
        ------
        ValueError
            if no reasonable guess is possible and the caller must supply
            the order manually.
        """
        # Get the axis string using existing logic
        axes_string = SarcAsM._get_axes_string(series, tif)

        # Convert to NGFF format
        return SarcAsM._convert_axes_to_ngff_format(axes_string)

    @staticmethod
    def _get_axes_string(series, tif: tifffile.TiffFile) -> str:
        """Extract axes string using existing detection logic."""
        # OME-TIFF
        if tif.ome_metadata:
            try:
                root = ET.fromstring(tif.ome_metadata)
                return root.find('.//{*}Image').attrib['DimensionOrder'].upper()
            except Exception:
                pass  # fall through to next strategy

        # ImageJ hyper-stack
        if tif.imagej_metadata:
            ij = tif.imagej_metadata
            order = ''
            if ij.get('frames', 1) > 1: order += 'T'
            if ij.get('slices', 1) > 1: order += 'Z'
            if ij.get('channels', 1) > 1: order += 'C'
            order += 'YX'
            return order

        # tifffile's own guess
        if series.axes:
            axes = series.axes.upper().replace('S', 'C')  # S → C (samples)
            if 'Q' not in axes:  # ignore unknown axis
                return axes

        # heuristics on raw shape
        shape = series.shape
        if len(shape) == 2:  # (Y, X)
            return 'YX'
        if len(shape) == 3 and shape[-1] <= 10:  # (Y, X, C)  small C
            return 'YXC'
        if len(shape) == 3 and shape[-1] > 10:
            return 'TYX'

        raise ValueError(
            f"Could not determine axis order for shape {shape}. "
            "Please specify it explicitly (e.g. axes='TXYC')."
        )

    @staticmethod
    def _convert_axes_to_ngff_format(axes_string: str) -> List[Dict[str, str]]:
        """
        Convert uppercase axes string to NGFF-compliant axis dictionaries.

        Parameters
        ----------
        axes_string : str
            Uppercase axes string like 'TCZYX' or 'YX'

        Returns
        -------
        List[Dict[str, str]]
            List of axis dictionaries following NGFF format
        """
        # Define axis properties mapping
        axis_properties = {
            'T': {'name': 't', 'type': 'time', 'unit': 'second'},
            'C': {'name': 'c', 'type': 'channel'},  # No unit for channel
            'Z': {'name': 'z', 'type': 'space', 'unit': 'micrometer'},
            'Y': {'name': 'y', 'type': 'space', 'unit': 'micrometer'},
            'X': {'name': 'x', 'type': 'space', 'unit': 'micrometer'}
        }

        axes_list = []
        for axis_char in axes_string:
            if axis_char in axis_properties:
                axis_dict = axis_properties[axis_char].copy()
                axes_list.append(axis_dict)
            else:
                raise ValueError(f"Unknown axis character: {axis_char}")

        return axes_list

    def _harvest_metadata(self, series, tif, axes, override_pixelsize=None, override_frametime=None
                          ) -> ImageMetadata:
        """Collect metadata from tif and update the instance metadata object."""

        # Extract pixel size (in micrometers for NGFF compatibility)
        px = self._extract_pixel_size(tif, override_pixelsize)

        # Extract frame time and timestamps (in seconds for NGFF compatibility)
        ft, ts = self._extract_temporal_metadata(tif, override_frametime)

        # Calculate stack length
        stack_len = self._calculate_stack_length(series, axes)

        # Create NGFF-compatible coordinate transformations
        coordinate_transforms = self._create_coordinate_transformations(axes, px, ft)

        # Create metadata object with NGFF-compatible format
        metadata = ImageMetadata(
            file_name=os.path.basename(self.filepath),
            file_path=self.filepath,
            axes=axes,
            shape_orig=tuple(series.shape),
            n_stack=int(stack_len),
            pixelsize=px,  # in micrometers
            frametime=ft,  # in seconds
            timestamps=ts,  # in seconds
            coordinate_transformations=coordinate_transforms,
            **self.info
        )

        return metadata

    def _extract_pixel_size(self, tif, override_pixelsize=None) -> Optional[float]:
        """Extract pixel size in micrometers (NGFF standard unit)."""
        if override_pixelsize is not None:
            return float(override_pixelsize)

        px = None

        # Try OME-TIFF metadata first
        if tif.ome_metadata:
            try:
                root = ET.fromstring(tif.ome_metadata)
                px_elem = root.find('.//{*}Pixels')
                if px_elem is not None:
                    px = px_elem.get('PhysicalSizeX')
                    px = float(px) if px else None
                    # OME-XML PhysicalSizeX is already in micrometers
            except Exception:
                pass

        # Try ImageJ metadata
        if px is None and tif.imagej_metadata:
            ij = tif.imagej_metadata
            px = ij.get('pixel_width') or ij.get('PixelWidth')
            try:
                px = float(px) if px is not None else None
                # ImageJ pixel_width is typically in micrometers
            except (TypeError, ValueError):
                pass

        # Fallback to TIFF resolution tags
        if px is None:
            px = self._extract_pixel_size_from_resolution_tags(tif)

        return px

    def _extract_pixel_size_from_resolution_tags(self, tif) -> Optional[float]:
        """Extract pixel size from TIFF resolution tags, convert to micrometers."""
        try:
            page = tif.pages[0]
            if 'XResolution' in page.tags and 'ResolutionUnit' in page.tags:
                num, den = page.tags['XResolution'].value
                unit = page.tags['ResolutionUnit'].value  # 2=inches, 3=cm
                dpi = num / den
                if dpi > 0:
                    # Convert to micrometers (NGFF standard)
                    if unit == 2:  # inches
                        return 25_400 / dpi  # 25,400 µm per inch
                    elif unit == 3:  # centimeters
                        return 10_000 / dpi  # 10,000 µm per cm
                    else:
                        return 1_000_000 / dpi  # assume meters, convert to µm
        except Exception:
            pass
        return None

    def _extract_temporal_metadata(self, tif, override_frametime=None) -> Tuple[Optional[float], Optional[List[float]]]:
        """Extract frame time in seconds and timestamps (NGFF standard)."""
        if override_frametime is not None:
            return float(override_frametime), None

        ft, ts = None, None

        # Try OME-TIFF metadata
        if tif.ome_metadata:
            try:
                root = ET.fromstring(tif.ome_metadata)
                deltas = [float(p.get('DeltaT')) for p in
                          root.findall('.//{*}Plane') if p.get('DeltaT')]
                if deltas:
                    ts = deltas  # OME DeltaT is in seconds
                    ft = float(np.diff(deltas).mean()) if len(deltas) > 1 else deltas[0]
            except Exception:
                pass

        # Try ImageJ metadata
        if ft is None and tif.imagej_metadata:
            ij = tif.imagej_metadata
            ft = ij.get('finterval') or ij.get('Frame interval')
            if ft is None and (fps := ij.get('fps')):
                try:
                    ft = 1 / float(fps)  # Convert FPS to seconds per frame
                except (ValueError, ZeroDivisionError):
                    pass

            if ts is None:
                ts = ij.get('timestamps')
                if isinstance(ts, str):
                    try:
                        ts = json.loads(ts)
                    except Exception:
                        pass

        # Convert frame time to seconds if needed
        ft = float(ft) if ft else None

        return ft, ts

    def _create_coordinate_transformations(self, axes: str, pixelsize: Optional[float],
                                           frametime: Optional[float]) -> List[Dict[str, Any]]:
        """Create NGFF-compatible coordinate transformations."""
        scale_values = []

        for axis in axes:
            if axis == 'T':
                # Time axis: use frametime in seconds, default to 1.0 if not available
                scale_values.append(frametime if frametime is not None else 1.0)
            elif axis == 'C':
                # Channel axis: dimensionless, use 1.0
                scale_values.append(1.0)
            elif axis in ['X', 'Y', 'Z']:
                # Spatial axes: use pixelsize in micrometers, default to 1.0 if not available
                scale_values.append(pixelsize if pixelsize is not None else 1.0)
            else:
                # Unknown axis: default to 1.0
                scale_values.append(1.0)

        return [{"type": "scale", "scale": scale_values}]


class OUT:
    def __getattr__(self, name: str) -> Any:
        # here get labels
                # mapping identical to the old .tif filenames
        # if name in {"zbands", "zbands_fast_movie", "mbands",
        #             "orientation", "cell_mask", "sarcomere_mask"}:
        #     if name not in inter_grp:
        #         raise FileNotFoundError(
        #             f"{name} not found. Run the relevant detection routine.")
        #     return xr... openzarr ['labels']... [name]
        if name == "image":
            return self.root["raw"][0][:]

        raise AttributeError(name)

    def open_zarr_in_explorer(self):
        """
        Open the directory of a Zarr or OME-Zarr store in the system’s native
        file-explorer (Explorer, Finder, Nautilus, …).

        Parameters
        ----------
        zarr_path : str | os.PathLike
            Path to the “*.zarr” folder or to any file/group inside it.

        Raises
        ------
        FileNotFoundError – if the target does not exist.
        RuntimeError – when the OS call fails (e.g. missing xdg-utils).
        """
        p = Path(self.ome_path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(p)

        # If a specific array (.zarray) or chunk is given, open its parent store
        if p.is_file():
            p = p.parent

        system = platform.system()
        try:
            if system == "Windows":  # Explorer
                os.startfile(p)  # type: ignore
            elif system == "Darwin":  # macOS Finder
                subprocess.run(["open", p], check=False)
            else:  # Linux / BSD
                subprocess.run(["xdg-open", p], check=False)
        except Exception as exc:
            raise RuntimeError(f"Could not launch file explorer: {exc}")

    def view_zarr_in_browser(self):
        """
        Spawn ``ome_zarr view <store>`` which starts a small web server and
        opens the data in the default browser.
        """
        if shutil.which("ome_zarr") is None:
            raise RuntimeError(
                "ome_zarr CLI not found.  Install with `pip install ome-zarr[all]`.")
        subprocess.Popen(["ome_zarr", "view", str(self.ome_path)])  # non-blocking

    def save_metadata(self):
        self.root.attrs["sarcasm_metadata"] = self.metadata.to_dict()

    def read_image(
            self,
            frames: Optional[Union[int, Sequence[int], slice]] = None,
            channel: Optional[Union[int, str]] = None,
    ) -> np.ndarray:
        """
        Return the image in internal order (YX | TYX | ZYX).

        Parameters
        ----------
        frames   Frame selection for stacks; ``None`` → all
        channel  Channel to use; overrides metadata when given
        """
        # first call: create / open a store + cache metadata
        if not hasattr(self, "root"):
            self._bootstrap_store(channel_override=channel,
                                  pixelsize_override=self.metadata.pixelsize,
                                  frametime_override=self.metadata.frametime)

        # always load from OME-Zarr once it exists
        return self._read_from_omezarr(frames=frames, channel=channel)

    def _select_channel(
            self,
            data: np.ndarray,
            axes: str,
            channel_override: Optional[Union[int, str]] = None,
    ):
        """Return (data, new_axes) after optional channel extraction."""
        if "C" not in axes:
            return data, axes

        if channel_override is None:
            channel_override = getattr(self.metadata, "channel", 0)

        if isinstance(channel_override, str) and channel_override.upper() == "RGB":
            data = np.dot(data, [0.2989, 0.5870, 0.1140])
            return data, axes.replace("C", "")

        c_idx = axes.index("C")
        data = np.take(data, int(channel_override), axis=c_idx)
        return data, axes.replace("C", "")


    @staticmethod
    def _validate_axes(axes: str) -> None:
        """
        Raise if `axes` is not a unique subset of {X, Y, T, C, Z}.
        """
        allowed = set("XYTCZ")
        illegal = set(axes) - allowed
        if illegal:
            raise ValueError(
                f"Invalid axis letter(s): {''.join(sorted(illegal))}. "
                f"Only {''.join(sorted(allowed))} are permitted."
            )
        if len(axes) != len(set(axes)):
            dup = ''.join(sorted({c for c in axes if axes.count(c) > 1}))
            raise ValueError(
                f"Duplicate axis letter(s): {dup}. "
                "Each axis may appear at most once."
            )


    def _permute_to_internal(self, data: np.ndarray, source_axes: str) -> np.ndarray:
        """
        Parameters
        ----------
        data : np.ndarray
            The image data as stored on disk.
        source_axes : str
            Axis string returned by `_determine_axes`.

        Returns
        -------
        np.ndarray
            Array permuted to (Stack, Y, X) or (Y, X).
        """
        # Decide which dimension, if any, is treated as the stack
        stack_axis = 'T' if 'T' in source_axes else ('Z' if 'Z' in source_axes else None)

        target_axes: List[str] = []
        if stack_axis:
            target_axes.append(stack_axis)
        if 'Y' in source_axes:
            target_axes.append('Y')
        if 'X' in source_axes:
            target_axes.append('X')

        # Build the permutation list
        perm = [source_axes.index(ax) for ax in target_axes]
        if perm:
            data = data.transpose(perm)

        return data
