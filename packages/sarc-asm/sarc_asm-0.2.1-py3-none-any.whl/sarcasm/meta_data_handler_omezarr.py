from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import datetime
from sarcasm._version import __version__


@dataclass
class ImageMetadata:
    """
    Metadata container with NGFF compatibility and persistence capabilities.
    """

    # Core image properties (set during read_imgs)
    axes: str = ""
    pixelsize: Optional[float] = None  # micrometers (NGFF standard)
    frametime: Optional[float] = None  # seconds (NGFF standard)
    shape_orig: Tuple[int, ...] = field(default_factory=tuple)
    shape: Optional[Tuple[int, ...]] = None
    n_stack: Optional[int] = None
    size: Optional[Tuple[int, int]] = None
    timestamps: Optional[List[float]] = None

    # File properties (set during initialization)
    file_name: str = ""
    file_path: str = ""

    # User-specified channel with sarcomere signal
    channel: Optional[int] = None

    # SarcAsM metadata
    sarcasm_version: str = field(default_factory=lambda: __version__)
    timestamp_analysis: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    # User-supplied metadata (dynamic)
    user_info: Dict[str, Any] = field(default_factory=dict)

    # NGFF-specific metadata (computed in __post_init__)
    coordinate_transformations: List[Dict[str, Any]] = field(default_factory=list, init=False)
    ngff_axes: List[Dict[str, str]] = field(default_factory=list, init=False)

    # Computed properties (set in __post_init__)
    time: Optional[np.ndarray] = field(init=False, repr=False, default=None)

    # Internal validation flags
    _validated: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        """Compute derived fields and NGFF metadata after initialization."""
        # Ensure version compatibility
        if not hasattr(self, 'sarcasm_version') or self.sarcasm_version is None:
            self.sarcasm_version = __version__
        if not hasattr(self, 'timestamp_analysis') or self.timestamp_analysis is None:
            self.timestamp_analysis = datetime.datetime.now().isoformat()

        # Create time array if we have both frametime and a stack
        if self.frametime and self.n_stack and self.n_stack > 1:
            self.time = np.arange(0, self.n_stack * self.frametime, self.frametime)
        else:
            self.time = None

        # Generate NGFF-compatible metadata
        if self.axes:
            self.ngff_axes = self._create_ngff_axes()
            self.coordinate_transformations = self._create_coordinate_transformations()

        # Perform validation
        self._validate_metadata()
        self._validated = True

    def _create_ngff_axes(self) -> List[Dict[str, str]]:
        """Create NGFF-compatible axes metadata from axes string."""
        axes_list = []

        axis_properties = {
            'T': {'name': 't', 'type': 'time', 'unit': 'second'},
            'C': {'name': 'c', 'type': 'channel'},  # No unit for channel
            'Z': {'name': 'z', 'type': 'space', 'unit': 'micrometer'},
            'Y': {'name': 'y', 'type': 'space', 'unit': 'micrometer'},
            'X': {'name': 'x', 'type': 'space', 'unit': 'micrometer'}
        }

        for axis_char in self.axes.upper():
            if axis_char in axis_properties:
                axes_list.append(axis_properties[axis_char].copy())

        return axes_list

    def _create_coordinate_transformations(self) -> List[Dict[str, Any]]:
        """Create NGFF-compatible coordinate transformations."""
        if not self.axes:
            return []

        scale_values = []

        for axis in self.axes.upper():
            if axis == 'T':
                # Time axis: use frametime in seconds, default to 1.0 if not available
                scale_values.append(self.frametime if self.frametime is not None else 1.0)
            elif axis == 'C':
                # Channel axis: dimensionless, use 1.0
                scale_values.append(1.0)
            elif axis in ['X', 'Y', 'Z']:
                # Spatial axes: use pixelsize in micrometers, default to 1.0 if not available
                scale_values.append(self.pixelsize if self.pixelsize is not None else 1.0)
            else:
                # Unknown axis: default to 1.0
                scale_values.append(1.0)

        return [{"type": "scale", "scale": scale_values}]

    def _validate_metadata(self):
        """Validate metadata values against reasonable ranges."""
        if self.pixelsize is not None and not (0.001 <= self.pixelsize <= 100.0):
            raise ValueError(f"Pixel size {self.pixelsize} µm is outside reasonable range (0.001-100.0 µm)")

        if self.frametime is not None and not (0.001 <= self.frametime <= 3600.0):
            raise ValueError(f"Frame time {self.frametime} s is outside reasonable range (0.001-3600.0 s)")

        if self.shape_orig and self.axes and len(self.shape_orig) != len(self.axes):
            raise ValueError(f"Shape dimensions {len(self.shape_orig)} don't match axes length {len(self.axes)}")

    def add_user_info(self, **kwargs):
        """Add arbitrary user metadata after initialization."""
        self.user_info.update(kwargs)

    def update_physical_parameters(self, pixelsize: Optional[float] = None,
                                   frametime: Optional[float] = None):
        """Update physical parameters and regenerate NGFF transformations."""
        if pixelsize is not None:
            self.pixelsize = pixelsize
        if frametime is not None:
            self.frametime = frametime

        # Regenerate derived fields
        if self.frametime and self.n_stack and self.n_stack > 1:
            self.time = np.arange(0, self.n_stack * self.frametime, self.frametime)
        else:
            self.time = None

        # Regenerate NGFF transformations
        if self.axes:
            self.coordinate_transformations = self._create_coordinate_transformations()

        # Re-validate
        self._validate_metadata()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for OME-ZARR storage."""
        # Convert numpy arrays to lists for JSON serialization
        time_list = self.time.tolist() if self.time is not None else None

        return {
            # Core properties
            'axes': self.axes,
            'pixelsize': self.pixelsize,
            'frametime': self.frametime,
            'shape_orig': list(self.shape_orig) if self.shape_orig else [],
            'shape': list(self.shape) if self.shape else None,
            'n_stack': self.n_stack,
            'size': list(self.size) if self.size else None,
            'timestamps': self.timestamps,

            # File properties
            'file_name': self.file_name,
            'file_path': self.file_path,

            # Channel info
            'channel': self.channel,

            # SarcAsM metadata
            'sarcasm_version': self.sarcasm_version,
            'timestamp_analysis': self.timestamp_analysis,

            # Computed properties
            'time': time_list,

            # NGFF metadata
            'coordinate_transformations': self.coordinate_transformations,
            'ngff_axes': self.ngff_axes,

            # User info
            'user_info': self.user_info
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageMetadata':
        """Create ImageMetadata from dictionary."""
        # Extract fields that should not be passed to constructor
        time_data = data.pop('time', None)
        coordinate_transformations = data.pop('coordinate_transformations', [])
        ngff_axes = data.pop('ngff_axes', [])
        user_info = data.pop('user_info', {})

        # Convert lists back to tuples where needed
        if 'shape_orig' in data and data['shape_orig']:
            data['shape_orig'] = tuple(data['shape_orig'])
        if 'shape' in data and data['shape']:
            data['shape'] = tuple(data['shape'])
        if 'size' in data and data['size']:
            data['size'] = tuple(data['size'])

        # Create instance
        instance = cls(**data)

        # Restore computed fields
        if time_data:
            instance.time = np.array(time_data)

        # Add user info
        instance.add_user_info(**user_info)

        return instance

    def get_ngff_multiscale_metadata(self) -> Dict[str, Any]:
        """Generate NGFF multiscale metadata block for OME-ZARR."""
        if not self.ngff_axes:
            return {}

        return {
            "axes": self.ngff_axes,
            "datasets": [
                {
                    "path": "0",
                    "coordinateTransformations": self.coordinate_transformations
                }
            ],
            "version": "0.4",
            "name": "sarcomere_analysis"
        }

    def get_axes_string_lowercase(self) -> str:
        """Get axes string in lowercase format for OME-ZARR compatibility."""
        return self.axes.lower()

    def __repr__(self) -> str:
        """Enhanced representation showing key metadata."""
        shape_str = f"{self.shape_orig}" if self.shape_orig else "unknown"
        px_str = f"{self.pixelsize}µm" if self.pixelsize else "unknown"
        ft_str = f"{self.frametime}s" if self.frametime else "unknown"

        return (f"ImageMetadata(axes='{self.axes}', shape={shape_str}, "
                f"pixelsize={px_str}, frametime={ft_str})")
