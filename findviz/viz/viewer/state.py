"""
This module defines the visualization state classes for the FIND viewer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional, List, Dict, Tuple, TypedDict

import nibabel as nib
import numpy as np

from findviz.viz.io.timecourse import TaskDesignDict

class NiftiDataDict(TypedDict):
    """Dictionary for NIFTI data."""
    func_img: nib.Nifti1Image
    anat_img: nib.Nifti1Image
    mask_img: nib.Nifti1Image

class NiftiDataPreprocessedDict(TypedDict):
    """Dictionary for preprocessed NIFTI data."""
    func_img: nib.Nifti1Image

class GiftiDataDict(TypedDict):
    """Dictionary for GIFTI data."""
    left_func_img: nib.GiftiImage
    right_func_img: nib.GiftiImage

class GiftiDataPreprocessedDict(TypedDict):
    """Dictionary for preprocessed GIFTI data."""
    left_func_img: nib.GiftiImage
    right_func_img: nib.GiftiImage

class ColorOptions(TypedDict):
    """Color options."""
    color_min: float
    color_max: float
    color_range: Tuple[float, float]
    threshold_min: float
    threshold_max: float
    threshold_range: Tuple[float, float]
    opacity: float

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
class PlotOptions:
    """Plot options.
    
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
        montage_slice_dir: Direction of montage slice for NIFTI data. 
            Default is 'z'
        montage_slice_idx: Indices of montage slices for NIFTI data. 
            Default is {'x': 0.33, 'y': 0.5, 'z': 0.66}
        crosshair_on: Whether crosshair is enabled for NIFTI data. 
            Default is True
        direction_marker_on: Whether direction marker is enabled for NIFTI data. 
            Default is False
    """
    
    color_min: Optional[float] = None
    color_max: Optional[float] = None
    color_range: Optional[Tuple[float, float]] = None
    opacity: float = 1
    threshold_min: float = 0
    threshold_max: float = 0
    threshold_range: Optional[Tuple[float, float]] = None
    color_map: str = 'Viridis'
    hover_text_on: bool = True
    precision: int = 6
    slider_steps: int = 100
    allowed_precision: int = 6
    view_state: Literal['ortho', 'montage'] = 'ortho'
    montage_slice_dir: Optional[Literal['x', 'y', 'z']] = 'z'
    montage_slice_idx: Optional[Dict[str, Tuple[float, float, float]]] = None
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
            'view_state': self.view_state,
            'montage_slice_dir': self.montage_slice_dir,
            'montage_slice_idx': self.montage_slice_idx,
            'crosshair_on': self.crosshair_on,
            'direction_marker_on': self.direction_marker_on
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)


@dataclass
class TimeCoursePlotOptions:
    """Time course plot options."""
    color: TimeCourseColor = field(default_factory=lambda: TimeCourseColor.RED)
    plotType: Literal['block', 'hrf'] = 'block'
    width: float = 2.0
    opacity: float = 1.0
    mode: Literal['lines', 'markers', 'lines+markers'] = 'lines+markers'

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
            'plotType': self.plotType,
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
        timepoints: Timepoint indices. Default is None
        global_min: Global minimum value across all timepoints. Default is None
        global_max: Global maximum value across all timepoints. Default is None
        file_type: Type of visualization data ('nifti' or 'gifti'). Default is None
        timepoint: Current timepoint index. Default is 0
        plot_options: Plot options. Default is PlotOptions()
        preprocessed_plot_options: Plot options for preprocessed data. 
            Default is PlotOptions()
        color_options_original: original color options from raw data. 
            Default is ColorOptions()
        preprocessed_color_options_original: original color options from preprocessed data. 
            Default is ColorOptions()
        ts_enabled: Whether time course data is enabled. Default is False
        task_enabled: Whether task design data is enabled. Default is False
        fmri_preprocessed: Whether preprocessed fMRI data is available. Default is False
        ts_preprocessed: Whether preprocessed timecourse data is available. Default is False
        used_colors: Set of used colors for time series. Default is empty set {}
        ts_data: Dictionary of timeseries data. Default is empty dict {}
        ts_data_preprocessed: Dictionary of preprocessed timeseries data. 
            Default is None
        ts_labels: Labels for timeseries. Default is empty list [].
        ts_plot_options: Dictionary of time course plot options. 
            Default is empty dict {}
        task_data: Task design information. Default is None
        task_plot_options: Dictionary of task design plot options. 
            Default is empty dict {}
        annotation_markers: List of annotation markers. Default is empty list []
        annotation_selection: Selected annotation marker. Default is None
        annotation_selection_highlight: Whether annotation selection is highlighted. 
            Default is False
    """
    # metadata
    timepoints: List[int]
    global_min: float
    global_max: float
    file_type: Literal['nifti', 'gifti']
    timepoint: int = 0

    # plot state
    plot_options: PlotOptions = field(default_factory=PlotOptions)
    preprocessed_plot_options: PlotOptions = field(default_factory=PlotOptions)
    
    # preserved color state 
    color_options_original: ColorOptions = field(default_factory=ColorOptions)
    preprocessed_color_options_original: ColorOptions = field(default_factory=ColorOptions)

    # state flags
    ts_enabled: bool = False
    task_enabled: bool = False
    fmri_preprocessed: bool = False
    ts_preprocessed: bool = False

    # time course and task design
    used_colors: set[TimeCourseColor] = field(default_factory=set)
    ts_data: Dict[str, List[float]] = field(default_factory=dict)
    ts_data_preprocessed: Optional[Dict[str, List[float]]] = None
    ts_labels: List[str] = field(default_factory=list)
    ts_plot_options: dict[str, TimeCoursePlotOptions] = field(default_factory=dict)
    task_data: Optional[TaskDesignDict] = None
    task_plot_options: dict[str, TimeCoursePlotOptions] = field(default_factory=dict)
    annotation_markers: List[int] = field(default_factory=list)
    annotation_selection: Optional[int] = None
    annotation_selection_highlight: bool = False


@dataclass
class NiftiVisualizationState(VisualizationState):
    """Visualization state for NIFTI data.
    
    Attributes:
        file_type: constant 'nifti'
        slice_len: Length of each dimension for NIFTI images. Default is None
        coord_labels: Voxels coordinate labels for NIFTI data. Default is None
        anat_input: Whether anatomical data was provided. Default is False
        mask_input: Whether mask data was provided. Default is False
        view_state: View state ('ortho' or 'montage'). Default is 'ortho'
        montage_slice_dir: Direction of montage slices for NIFTI data. 
            Default is 'z'
        crosshair_on: Whether crosshair is enabled. Default is True
        direction_marker_on: Whether direction marker is enabled. Default is False
        nifti_data: Dictionary of NIFTI images. Default is empty dict {}
        nifti_data_preprocessed: Dictionary of preprocessed NIFTI images. 
            Default is empty dict {}
        x_slice_idx: Slice index for x-axis. Default is 0
        y_slice_idx: Slice index for y-axis. Default is 0
        z_slice_idx: Slice index for z-axis. Default is 0
    """
    # metadata
    file_type: Literal['nifti'] = 'nifti'
    slice_len: Optional[Dict[str, int]] = None # {'x': int, 'y': int, 'z': int}
    coord_labels: Optional[List[Tuple[int, int, int]]] = None # [(x, y, z), (x, y, z), (x, y, z)]
    anat_input: bool = False
    mask_input: bool = False

    # nifti data
    nifti_data: NiftiDataDict = field(default_factory=dict)
    nifti_data_preprocessed: NiftiDataDict = field(default_factory=dict)

    # functional header and affine
    func_header: Optional[nib.Nifti1Header] = None
    func_affine: Optional[np.ndarray] = None

    # slice indices
    x_slice_idx: int = 0
    y_slice_idx: int = 0
    z_slice_idx: int = 0
    

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
    gifti_data: Dict[str, nib.GiftiImage] = field(default_factory=dict)
    gifti_data_preprocessed: Dict[str, nib.GiftiImage] = field(default_factory=dict)

    # selected vertex and hemisphere
    selected_vertex: Optional[int] = None
    selected_hemi: Optional[Literal['left', 'right']] = None