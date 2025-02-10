"""
This module defines the visualization state classes for the FIND viewer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional, List, Dict, Tuple

import nibabel as nib
import numpy as np

from findviz.viz.viewer.types import (
    DistancePlotOptionsDict, NiftiDataDict, NiftiDataPreprocessedDict,
    GiftiDataDict, GiftiDataPreprocessedDict, ColorOptions,
    SliceCoordsDict, SliceIndexDict, 
    MontageSliceIndexDict, MontageSliceCoordsDict
)
class ColorMaps(Enum):
    """
    Enum for color maps
    """
    GREYS = 'Greys'
    YLGNBU = 'YlGnBu'
    GREENS = 'Greens'
    YLORRD = 'YlOrRd'
    BLUERED = 'Bluered'
    RDBU = 'RdBu'
    REDS = 'Reds'
    BLUES = 'Blues'
    PICNIC = 'Picnic'
    RAINBOW = 'Rainbow'
    PORTLAND = 'Portland'
    JET = 'Jet'
    HOT = 'Hot'
    BLACKBODY = 'Blackbody'
    ELECTRIC = 'Electric'
    VIRIDIS = 'Viridis'
    CIVIDIS = 'Cividis'

class TimeCourseColor(Enum):
    """Time course color options."""
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'
    ORANGE = 'orange'
    PURPLE = 'purple'
    BLACK = 'black'
    GREY = 'grey'
    YELLOW = 'yellow'
    BROWN = 'brown'
    DARKRED = 'darkred'
    TOMATO = 'tomato'
    MAGENTA = 'magenta'
    CRIMSON = 'crimson'
    SALMON = 'salmon'
    FIREBRICK = 'firebrick'
    NAVY = 'navy'
    ROYALBLUE = 'royalblue'
    TURQUOISE = 'turquoise'
    CORAL = 'coral'
    SEA_GREEN = 'seagreen'
    FOREST_GREEN = 'forestgreen'
    OLIVE = 'olive'
    DARK_GREEN = 'darkgreen'
    DARK_ORANGE = 'darkorange'
    VIOLET = 'violet'
    SLATE_GREY = 'slategrey'
    SLATE_BLUE = 'slateblue'
    DARK_GREY = 'darkgrey'
    KHAKI = 'khaki'
    TAN = 'tan'

@dataclass
class DistancePlotOptions:
    """Distance plot options."""
    color_min: float
    color_max: float
    color_map: ColorMaps = ColorMaps.RDBU
    color_range: Tuple[float, float]
    precision: int = 6
    slider_step_size: float = 1.0
    allowed_precision: int = 6
    time_marker_on: bool = True
    time_marker_color: TimeCourseColor = TimeCourseColor.BLACK
    time_marker_width: float = 1.0
    time_marker_opacity: float = 0.8

    def to_dict(self) -> DistancePlotOptionsDict:
        """Convert to dictionary."""
        return {
            'color_map': self.color_map,
            'color_min': self.color_min,
            'color_max': self.color_max,
            'color_range': self.color_range,
            'precision': self.precision,
            'allowed_precision': self.allowed_precision,
            'slider_step_size': self.slider_step_size,
            'time_marker_on': self.time_marker_on,
            'time_marker_color': self.time_marker_color,
            'time_marker_width': self.time_marker_width,
            'time_marker_opacity': self.time_marker_opacity
        }
    
    def update_from_dict(self, data: DistancePlotOptionsDict) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)

@dataclass
class FmriPlotOptions:
    """Plot options for fMRI data.
    
    Attributes:
        color_min: Minimum value for color mapping. Default is None
        color_max: Maximum value for color mapping. Default is None
        color_range: Color range for color mapping. Default is None
        opacity: Opacity of the color mapping. Default is 1
        threshold_min: Minimum value for threshold mapping. Default is 0
        threshold_max: Maximum value for threshold mapping. Default is 0
        threshold_range: Threshold range for threshold mapping. Default is None
        color_map: Color map for color mapping. Default is 'Viridis'
        hover_text_on: Whether hover text is enabled. Default is True
        precision: Precision of the color mapping. Default is 6
        slider_steps: Stepsize of the sliders. Default is 100
        allowed_precision: Allowed precision of the sliders. Default is 6
        view_state: View state ('ortho' or 'montage') for NIFTI data. 
            Default is 'ortho'
        crosshair_on: Whether crosshair is enabled for NIFTI data. 
            Default is True
        direction_marker_on: Whether direction marker is enabled for NIFTI data. 
            Default is False
    """
    # fmri plot options
    color_min: Optional[float] = None
    color_max: Optional[float] = None
    color_range: Optional[Tuple[float, float]] = None
    opacity: float = 1
    threshold_min: float = 0
    threshold_max: float = 0
    threshold_range: Optional[Tuple[float, float]] = None
    color_map: ColorMaps = ColorMaps.VIRIDIS
    hover_text_on: bool = True
    precision: int = 6
    slider_steps: int = 100
    allowed_precision: int = 6
    crosshair_on: bool = True
    direction_marker_on: bool = False

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'color_map': self.color_map,
            'color_min': self.color_min,
            'color_max': self.color_max,
            'color_range': self.color_range,
            'threshold_min': self.threshold_min,
            'threshold_max': self.threshold_max,
            'threshold_range': self.threshold_range,
            'opacity': self.opacity,
            'hover_text_on': self.hover_text_on,
            'precision': self.precision,
            'slider_steps': self.slider_steps,
            'allowed_precision': self.allowed_precision,
            'crosshair_on': self.crosshair_on,
            'direction_marker_on': self.direction_marker_on
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)


@dataclass
class TimeCourseGlobalPlotOptions:
    """Global time course plot options."""
    grid_on: bool = True
    hover_text_on: bool = True
    time_marker_on: bool = True
    global_convolution: bool = True

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'grid_on': self.grid_on,
            'hover_text_on': self.hover_text_on,
            'time_marker_on': self.time_marker_on,
            'global_convolution': self.global_convolution
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)

@dataclass
class TimeCoursePlotOptions:
    """Time course plot options.
    
    Attributes:
        visibility: whether the time course is visible in the plot. Default is True.
        color: Color of the time course. Default is RED
        width: Width of the time course. Default is 2.0
        opacity: Opacity of the time course. Default is 1.0
        mode: Mode of the time course. Default is 'lines'
    """
    visibility: bool = True
    color: TimeCourseColor = field(default_factory=lambda: TimeCourseColor.RED)
    width: float = 2.0
    scale: float = 1.0
    opacity: float = 1.0
    mode: Literal['lines', 'markers', 'lines+markers'] = 'lines'

    @classmethod
    def with_color(cls, color: TimeCourseColor, **kwargs):
        """Create TimeCoursePlotOptions with a specific color."""
        return cls(color=color, **kwargs)

    @classmethod
    def with_next_color(cls, used_colors: set[TimeCourseColor], **kwargs):
        """Create TimeCoursePlotOptions with the next available color.
        
        Args:
            used_colors: Set of already used TimeCourseColor values
            **kwargs: Additional arguments to pass to constructor
            
        Returns:
            TimeCoursePlotOptions with first unused color from TimeCourseColor enum
        """
        available_colors = set(TimeCourseColor) - used_colors
        if not available_colors:
            # If all colors used, start over with first color
            next_color = list(TimeCourseColor)[0]
        else:
            next_color = list(available_colors)[0]
        return cls(color=next_color, **kwargs)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'color': self.color,
            'width': self.width,
            'scale': self.scale,
            'opacity': self.opacity,
            'mode': self.mode
        }

    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)

@dataclass
class TimeMarkerPlotOptions:
    """Time marker plot options."""
    opacity: float = 0.5
    width: float = 1.0
    shape: Literal['solid', 'dashed', 'dotted'] = 'solid'
    color: TimeCourseColor = field(default_factory=lambda: TimeCourseColor.GREY)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'opacity': self.opacity,
            'width': self.width,
            'shape': self.shape,
            'color': self.color
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)


@dataclass
class TaskDesignPlotOptions:
    """Task design plot options.
    
    Attributes:
        convolution: Whether convolution of task design with hrf is enabled. Default is True
        scale: Scale of the task design. Default is 1.0
        color: Color of the task design. Default is RED
        width: Width of the task design. Default is 2.0
        opacity: Opacity of the task design. Default is 1.0
        mode: Mode of the task design. Default is 'lines'
    """
    convolution: bool = True
    scale: float = 1.0
    color: TimeCourseColor = field(default_factory=lambda: TimeCourseColor.RED)
    width: float = 2.0
    opacity: float = 1.0
    mode: Literal['lines', 'markers', 'lines+markers'] = 'lines'

    @classmethod
    def with_color(cls, color: TimeCourseColor, **kwargs):
        """Create TaskDesignPlotOptions with a specific color."""
        return cls(color=color, **kwargs)

    @classmethod
    def with_next_color(cls, used_colors: set[TimeCourseColor], **kwargs):
        """Create TaskDesignPlotOptions with the next available color.
        
        Args:
            used_colors: Set of already used TimeCourseColor values
            **kwargs: Additional arguments to pass to constructor
            
        Returns:
            TimeCoursePlotOptions with first unused color from TimeCourseColor enum
        """
        available_colors = set(TimeCourseColor) - used_colors
        if not available_colors:
            # If all colors used, start over with first color
            next_color = list(TimeCourseColor)[0]
        else:
            next_color = list(available_colors)[0]
        return cls(color=next_color, **kwargs)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'convolution': self.convolution,
            'scale': self.scale,
            'color': self.color,
            'width': self.width,
            'opacity': self.opacity,
            'mode': self.mode
        }

    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)

@dataclass
class VisualizationState:
    """Base visualization state class containing common attributes.
    
    Attributes:
        tr: Repetition time. If not provided, set to None.
        slicetime_ref: Slicetime reference. If not provided, set to None.
        timepoints: Timepoint indices. Default is None
        global_min: Global minimum value across all timepoints. Default is None
        global_max: Global maximum value across all timepoints. Default is None
        file_type: Type of visualization data ('nifti' or 'gifti'). Default is None
        timepoint: Current timepoint index. Default is 0
        fmri_plot_options: Plot options for fMRI data. Default is FmriPlotOptions()
        preprocessed_fmri_plot_options: Plot options for preprocessed fMRI data. 
            Default is FmriPlotOptions()
        color_options_original: original color options from raw data. 
            Default is ColorOptions()
        preprocessed_color_options_original: original color options from preprocessed data. 
            Default is ColorOptions()
        ts_enabled: Whether time course data is enabled. Default is False
        task_enabled: Whether task design data is enabled. Default is False
        fmri_preprocessed: Whether preprocessed fMRI data is available. Default is False
        ts_preprocessed: Whether preprocessed timecourse data is available. Default is False
        used_colors: Set of used colors for time series. Default is empty set {}
        time_course_global_plot_options: Global time course plot options. 
            Default is TimeCourseGlobalPlotOptions()
        ts_data: Dictionary of timeseries data. Default is empty dict {}
        ts_data_preprocessed: Dictionary of preprocessed timeseries data. 
            Default is None
        ts_labels: Labels for timeseries. Default is empty list [].
        ts_type: Type of timeseries - fmri or user. Default is empty dict {}.
        ts_plot_options: Dictionary of time course plot options.
            Default is empty dict {}
        task_data: Task design information. Default is None
        task_plot_options: Dictionary of task design plot options. 
            Default is empty dict {}
        annotation_markers: List of annotation markers. Default is empty list []
        annotation_selection: Selected annotation marker. Default is None
        annotation_selection_highlight: Whether annotation selection is highlighted. 
            Default is True
        distance_data: Distance data. Default is None
        distance_plot_options: Distance plot options. Default is None.
    """
    # metadata
    tr: Optional[float] = None
    slicetime_ref: Optional[float] = None
    timepoints: List[int]
    global_min: float
    global_max: float
    file_type: Literal['nifti', 'gifti']
    timepoint: int = 0

    # plot state
    fmri_plot_options: FmriPlotOptions = field(default_factory=FmriPlotOptions)
    preprocessed_fmri_plot_options: FmriPlotOptions = field(
        default_factory=FmriPlotOptions
    )
    
    # preserved color state
    color_options_original: ColorOptions = field(default_factory=ColorOptions)
    preprocessed_color_options_original: ColorOptions = field(
        default_factory=ColorOptions
    )

    # state flags
    ts_enabled: bool = False
    task_enabled: bool = False
    fmri_preprocessed: bool = False
    ts_preprocessed: bool = False

    # time course and task design
    used_colors: set[TimeCourseColor] = field(default_factory=set)
    time_course_global_plot_options: TimeCourseGlobalPlotOptions = field(
        default_factory=TimeCourseGlobalPlotOptions
    )
    ts_data: Dict[str, List[float]] = field(default_factory=dict)
    ts_data_preprocessed: Optional[Dict[str, List[float]]] = None
    ts_labels: List[str] = field(default_factory=list)
    ts_type: Dict[str, Literal['fmri', 'user']] = field(default_factory=dict)
    ts_plot_options: dict[str, TimeCoursePlotOptions] = field(default_factory=dict)
    task_data: Dict[str, Dict[Literal['block', 'hrf'], np.ndarray]] = field(default_factory=dict)
    task_conditions: List[str] = field(default_factory=list)
    task_plot_options: dict[str, TaskDesignPlotOptions] = field(default_factory=dict)
    annotation_markers: List[int] = field(default_factory=list)
    annotation_selection: Optional[int] = None
    annotation_selection_highlight: bool = True
    time_marker_plot_options: TimeMarkerPlotOptions = field(
        default_factory=TimeMarkerPlotOptions
    )
    # outputs from distance analysis
    distance_data: Optional[np.ndarray] = None
    distance_plot_options: Optional[DistancePlotOptions] = None

@dataclass
class NiftiVisualizationState(VisualizationState):
    """Visualization state for NIFTI data.
    
    Attributes:
        file_type: constant 'nifti'
        slice_len: Length of each dimension for NIFTI images. Default is None
        coord_labels: Voxels coordinate labels for NIFTI data. Default is None
        anat_input: Whether anatomical data was provided. Default is False
        mask_input: Whether mask data was provided. Default is False
        nifti_data: Dictionary of NIFTI images. Default is empty dict {}
        nifti_data_preprocessed: Dictionary of preprocessed NIFTI images. 
            Default is empty dict {}
        func_header: Header of functional data. Default is None
        func_affine: Affine matrix of functional data. Default is None
        view_state: View state ('ortho' or 'montage'). Default is 'ortho'
        ortho_slice_idx: Indices of ortho slices for NIFTI data. Default is 0.
        montage_slice_idx: Indices of montage slices for NIFTI data for each slice direction. 
            Default is None.
        ortho_slice_coords: Coordinates of ortho slices for NIFTI data. 
            Default is None.
        montage_slice_dir: Direction of montage slice for NIFTI data. 
            Default is 'z'
        montage_slice_coords: Coordinates of montage slices for NIFTI data. 
            Default is None.
    """
    # metadata
    file_type: Literal['nifti'] = 'nifti'
    slice_len: Optional[Dict[str, int]] = None # {'x': int, 'y': int, 'z': int}
    coord_labels: Optional[List[Tuple[int, int, int]]] = None # [(x, y, z), (x, y, z), (x, y, z)]
    anat_input: bool = False
    mask_input: bool = False

    # nifti data
    nifti_data: NiftiDataDict = field(default_factory=dict)
    nifti_data_preprocessed: NiftiDataPreprocessedDict = field(default_factory=dict)

    # functional header and affine
    func_header: Optional[nib.Nifti1Header] = None
    func_affine: Optional[np.ndarray] = None

    # view state - orthogonal or montage view
    view_state: Literal['ortho', 'montage'] = 'ortho'

    # orthogonal view slice indices
    ortho_slice_idx: SliceIndexDict = field(default_factory=dict)
    # montage view slice indices
    montage_slice_idx: MontageSliceIndexDict = field(default_factory=dict)

    # ortho view slice coordinates
    ortho_slice_coords: Optional[SliceCoordsDict] = None

    # montage view slice coordinates
    montage_slice_dir: Optional[Literal['x', 'y', 'z']] = 'z'
    montage_slice_coords: Optional[MontageSliceCoordsDict] = None
    

@dataclass
class GiftiVisualizationState(VisualizationState):
    """Visualization state for GIFTI data.
    
    Attributes:
        file_type: constant 'gifti'
        left_input: Whether left hemisphere data was provided
        right_input: Whether right hemisphere data was provided
        gifti_data: Dictionary of GIFTI images
        gifti_data_preprocessed: Dictionary of preprocessed GIFTI images
        vertices_left: Vertex coordinates for left hemisphere
        faces_left: Face indices for left hemisphere
        vertices_right: Vertex coordinates for right hemisphere
        faces_right: Face indices for right hemisphere
        selected_vertex: Selected vertex index
        selected_hemi: Selected hemisphere ('left' or 'right')
    """
    # metadata
    file_type: Literal['gifti'] = 'gifti'
    left_input: bool = False
    right_input: bool = False
    vertices_left: Optional[List[float]] = None
    faces_left: Optional[List[float]] = None
    vertices_right: Optional[List[float]] = None
    faces_right: Optional[List[float]] = None
    
    # gifti data
    gifti_data: GiftiDataDict = field(default_factory=dict)
    gifti_data_preprocessed: GiftiDataPreprocessedDict = field(default_factory=dict)

    # selected vertex and hemisphere
    selected_vertex: Optional[int] = None
    selected_hemi: Optional[Literal['left', 'right']] = None