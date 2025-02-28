"""
This module defines the visualization state classes for the FIND viewer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional, List, Dict, Tuple, Union

import nibabel as nib
import numpy as np

from findviz.viz.analysis.scaler import SignalScaler, SignalShifter
from findviz.viz.viewer.types import (
    DistancePlotOptionsDict, NiftiDataDict, NiftiDataPreprocessedDict,
    GiftiDataDict, GiftiDataPreprocessedDict, ColorOptions,
    SliceCoordsDict, OrthoSliceIndexDict, 
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
    color_min: Optional[float] = None
    color_max: Optional[float] = None
    color_range: Optional[Tuple[float, float]] = None
    color_map: ColorMaps = ColorMaps.RDBU
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
            'color_map': self.color_map.value,
            'color_min': self.color_min,
            'color_max': self.color_max,
            'color_range': self.color_range,
            'precision': self.precision,
            'allowed_precision': self.allowed_precision,
            'slider_step_size': self.slider_step_size,
            'time_marker_on': self.time_marker_on,
            'time_marker_color': self.time_marker_color.value,
            'time_marker_width': self.time_marker_width,
            'time_marker_opacity': self.time_marker_opacity
        }
    
    def update_from_dict(self, data: DistancePlotOptionsDict) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color_map':
                setattr(self, key, ColorMaps(value))
            elif key == 'time_marker_color':
                setattr(self, key, TimeCourseColor(value))
            else:
                setattr(self, key, value)

@dataclass
class FmriPlotOptions:
    """Plot options for fMRI data.
    
    Attributes:
        color_min: Minimum value for color mapping. Default is None
        color_max: Maximum value for color mapping. Default is None
        color_range: Color range for color mapping. Default is None
        colorbar_on: Whether colorbar is enabled. Default is True
        opacity: Opacity of the color mapping. Default is 1
        threshold_min: Minimum value for threshold mapping. Default is 0
        threshold_max: Maximum value for threshold mapping. Default is 0
        threshold_range: Threshold range for threshold mapping. Default is None
        color_map: Color map for color mapping. Default is 'Viridis'
        reverse_colormap: Whether the colormap is reversed. Default is False
        hover_text_on: Whether hover text is enabled. Default is True
        precision: Precision of the color mapping. Default is 6
        play_movie_speed: Speed of the movie (in milliseconds). Default is 500
        slider_step_size: Stepsize of the sliders. Default is 100
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
    colorbar_on: bool = True
    opacity: float = 1
    threshold_min: float = 0
    threshold_max: float = 0
    threshold_range: Optional[Tuple[float, float]] = None
    color_map: ColorMaps = ColorMaps.VIRIDIS
    reverse_colormap: bool = False
    hover_text_on: bool = True
    precision: int = 6
    play_movie_speed: int = 500
    slider_step_size: int = 100
    allowed_precision: int = 6
    crosshair_on: bool = True
    direction_marker_on: bool = False

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'color_map': self.color_map.value,
            'reverse_colormap': self.reverse_colormap,
            'color_min': self.color_min,
            'color_max': self.color_max,
            'color_range': self.color_range,
            'colorbar_on': self.colorbar_on,
            'threshold_min': self.threshold_min,
            'threshold_max': self.threshold_max,
            'threshold_range': self.threshold_range,
            'opacity': self.opacity,
            'hover_text_on': self.hover_text_on,
            'precision': self.precision,
            'play_movie_speed': self.play_movie_speed,
            'slider_step_size': self.slider_step_size,
            'allowed_precision': self.allowed_precision,
            'crosshair_on': self.crosshair_on,
            'direction_marker_on': self.direction_marker_on
        }
    

    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color_map':
                setattr(self, key, ColorMaps(value))
            else:
                setattr(self, key, value)


@dataclass
class TimeCourseGlobalPlotOptions:
    """Global time course plot options.
    
    Attributes:
        global_min: Global minimum value for time course plot - 
            computed from all time courses. Default is None
        global_max: Global maximum value for time course plot - 
            computed from all time courses. Default is None
        default_global_min: Default global minimum value for time course plot. 
            Default is -1.0
        default_global_max: Default global maximum value for time course plot.
             Default is 1.0
        grid_on: Whether grid is enabled for time course plot. Default is True
        hover_text_on: Whether hover text is enabled for time course plot. 
            Default is True
        time_marker_on: Whether time marker is enabled for time course plot. 
            Default is True
        global_convolution: Whether global convolution is enabled for time course plot. 
            Default is True
        shift_unit: Constant shift unit applied to time course data on constant shift changes. 
            Default is 1.0. This value is updated when global min and max are updated.
        shift_update_ratio: Ratio of shift unit updates. 
            Default is 10.
        scale_unit: Scale unit applied to time course data on scale change. 
            Default is 0.1. This value is updated when global min and max are updated.
        scale_update_granularity: Granularity of scale unit updates. 
            Default is 10.
    """
    global_min: Optional[float] = None
    global_max: Optional[float] = None
    default_global_min: float = -1.0
    default_global_max: float = 1.0
    grid_on: bool = True
    global_convolution: bool = True
    hover_text_on: bool = True
    time_marker_on: bool = True
    shift_unit: float = 1.0
    shift_update_ratio: int = 10
    scale_unit: float = 0.1
    scale_update_granularity: int = 10

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'global_min': self.global_min,
            'global_max': self.global_max,
            'grid_on': self.grid_on,
            'hover_text_on': self.hover_text_on,
            'time_marker_on': self.time_marker_on,
            'global_convolution': self.global_convolution,
            'shift_unit': self.shift_unit,
            'shift_update_ratio': self.shift_update_ratio,
            'scale_unit': self.scale_unit,
            'scale_update_granularity': self.scale_update_granularity
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)

@dataclass
class TimeCoursePlotOptions:
    """Time course plot options.
    
    Attributes:
        label: Label of the time course. Default is None
        visibility: whether the time course is visible in the plot. Default is True.
        color: Color of the time course. Default is RED
        width: Width of the time course. Default is 2.0
        constant: History of constant shifts to the time course handled by SignalShifter.
        scale: History of scale changes to the time course handled by SignalScaler.
        preprocess_constant: History of constant shifts to the preprocessed time course 
            handled by SignalShifter.
        preprocess_scale: History of scale changes to the preprocessed time course 
            handled by SignalScaler.
        opacity: Opacity of the time course. Default is 1.0
        mode: Mode of the time course. Default is 'lines'
    """
    label: str = None
    visibility: bool = True
    color: TimeCourseColor = TimeCourseColor.RED
    width: float = 2.0
    constant: SignalShifter = field(default_factory=SignalShifter)
    scale: SignalScaler = field(default_factory=SignalScaler)
    preprocess_constant: SignalShifter = field(default_factory=SignalShifter)
    preprocess_scale: SignalScaler = field(default_factory=SignalScaler)
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
    
    def clear_preprocess_history(self) -> None:
        """Clear preprocess history."""
        self.preprocess_constant.clear_history()
        self.preprocess_scale.clear_history()

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'label': self.label,
            'visibility': self.visibility,
            'color': self.color.value,
            'width': self.width,
            'constant': self.constant.shift_history,
            'scale': self.scale.scale_history,
            'preprocess_constant': self.preprocess_constant.shift_history,
            'preprocess_scale': self.preprocess_scale.scale_history,
            'opacity': self.opacity,
            'mode': self.mode
        }

    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color':
                setattr(self, key, TimeCourseColor(value))
            else:
                setattr(self, key, value)

@dataclass
class TimeMarkerPlotOptions:
    """Time marker plot options."""
    opacity: float = 0.5
    width: float = 1.0
    shape: Literal['solid', 'dashed', 'dotted'] = 'solid'
    color: TimeCourseColor = TimeCourseColor.GREY

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'opacity': self.opacity,
            'width': self.width,
            'shape': self.shape,
            'color': self.color.value
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color':
                setattr(self, key, TimeCourseColor(value))
            else:
                setattr(self, key, value)


@dataclass
class TaskDesignPlotOptions:
    """Task design plot options.
    
    Attributes:
        label: Label of the task design. Default is None
        convolution: Whether convolution of task design with hrf is enabled, 
            otherwise block structure is plotted. Default is hrf.
        scale: History of scale changes to the task design handled by SignalScaler.
        constant: History of constant shifts to the task design handled by SignalShifter.
        color: Color of the task design. Default is RED
        width: Width of the task design. Default is 2.0
        opacity: Opacity of the task design. Default is 1.0
        mode: Mode of the task design. Default is 'lines'
    """
    label: str = None
    convolution: Literal['hrf', 'block'] = 'hrf'
    scale: SignalScaler = field(default_factory=SignalScaler)
    constant: SignalShifter = field(default_factory=SignalShifter)
    color: TimeCourseColor = TimeCourseColor.RED
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
            'label': self.label,
            'convolution': self.convolution,
            'scale': self.scale.scale_history,
            'constant': self.constant.shift_history,
            'color': self.color.value,
            'width': self.width,
            'opacity': self.opacity,
            'mode': self.mode
        }

    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color':
                setattr(self, key, TimeCourseColor(value))
            else:
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
        ts_labels_preprocessed: Labels for preprocessed timeseries. 
            Default is empty list [].
        ts_fmri_plotted: Whether fmri time course is plotted. Default is False.
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
    timepoints: Optional[List[int]] = None
    global_min: Optional[float] = None
    global_max: Optional[float] = None
    file_type: Optional[Literal['nifti', 'gifti']] = None
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
    ts_preprocessed: Dict[str, bool] = field(default_factory=dict)

    # time course and task design
    used_colors: set[TimeCourseColor] = field(default_factory=set)
    time_course_global_plot_options: TimeCourseGlobalPlotOptions = field(
        default_factory=TimeCourseGlobalPlotOptions
    )
    ts_data: Dict[str, List[float]] = field(default_factory=dict)
    # set ts_labels as a private property
    _ts_labels: List[str] = field(default_factory=list)
    ts_type: Dict[str, Literal['fmri', 'user']] = field(default_factory=dict)
    ts_data_preprocessed: Dict[str, Union[List[float], None]] = field(default_factory=dict)
    ts_labels_preprocessed: List[str] = field(default_factory=list)
    ts_fmri_plotted: bool = False
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

    @property
    def ts_labels(self) -> List[str]:
        """Get the time series labels."""
        return self._ts_labels

    @ts_labels.setter
    def ts_labels(self, value: List[str]) -> None:
        """Set the time series labels and update preprocessing state."""
        # get the current ts_labels
        current_ts_labels = self._ts_labels
        # set the new ts_labels
        self._ts_labels = value
        # get the newly added ts_labels
        new_ts_labels = set(value) - set(current_ts_labels)
        # get the newly removed ts_labels
        removed_ts_labels = set(current_ts_labels) - set(value)
        # set preprocess state for the new ts_labels
        for ts_label in new_ts_labels:
            self.ts_preprocessed[ts_label] = False
            # set the ts_data_preprocessed to None
            self.ts_data_preprocessed[ts_label] = None

        # remove the removed ts_labels from preprocess state
        for ts_label in removed_ts_labels:
            self.ts_preprocessed.pop(ts_label)
            self.ts_data_preprocessed.pop(ts_label)
    

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
    ortho_slice_idx: OrthoSliceIndexDict = field(default_factory=dict)
    # montage view slice indices
    montage_slice_idx: MontageSliceIndexDict = field(default_factory=dict)

    # ortho view slice coordinates
    ortho_slice_coords: Optional[SliceCoordsDict] = field(default_factory=dict)

    # montage view slice coordinates
    montage_slice_dir: Optional[Literal['x', 'y', 'z']] = 'z'
    montage_slice_coords: Optional[MontageSliceCoordsDict] = field(default_factory=dict)
    

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