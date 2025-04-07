"""
Types for viewer
"""

from typing import TypedDict, Optional, List, Dict, Literal, Tuple

import nibabel as nib
import numpy as np

class AnnotationMarkerPlotOptionsDict(TypedDict):
    """Dictionary of marker plot options"""
    opacity: Optional[float]
    width: Optional[float]
    shape: Optional[Literal['solid', 'dashed', 'dotted']]
    color: Optional[str]
    highlight: Optional[bool]

class CrosshairCoordsDict(TypedDict):
    """Dictionary of crosshair coordinates for nifti data plotting"""
    slice1: Dict[Literal['len_x', 'len_y', 'x', 'y'], int]
    slice2: Dict[Literal['len_x', 'len_y', 'x', 'y'], int]
    slice3: Dict[Literal['len_x', 'len_y', 'x', 'y'], int]

class DirectionLabelCoordsDict(TypedDict):
    """Dictionary of direction label coordinates for nifti data plotting"""
    slice1: Dict[str, Dict[str, int]]
    slice2: Dict[str, Dict[str, int]]
    slice3: Dict[str, Dict[str, int]]

class DistancePlotOptionsDict(TypedDict):
    """Output dict from get_distance_plot_options() method"""
    color_map: str
    color_min: float
    color_max: float
    color_range: Tuple[float, float]
    precision: int
    allowed_precision: int
    slider_step_size: float
    time_marker_on: bool
    time_marker_color: str
    time_marker_width: float
    time_marker_opacity: float

class FmriPlotOptionsDict(TypedDict):
    """Output dict from get_fmri_plot_options() method"""
    color_min: Optional[float]
    color_max: Optional[float]
    color_range: Optional[Tuple[float, float]]
    opacity: float
    threshold_min: float
    threshold_max: float
    threshold_range: Optional[Tuple[float, float]]
    color_map: str
    hover_text_on: bool
    precision: int
    slider_steps: int
    allowed_precision: int
    crosshair_on: bool
    direction_marker_on: bool

class GiftiDataDict(TypedDict):
    """Dictionary of GIFTI data input"""
    left_func_img: nib.GiftiImage
    right_func_img: nib.GiftiImage

class GiftiDataPreprocessedDict(TypedDict):
    """Dictionary of preprocessed GIFTI data input"""
    left_func_img: nib.GiftiImage
    right_func_img: nib.GiftiImage

class ColorOptions(TypedDict):
    """Color options for fmri plot"""
    color_min: float
    color_max: float
    threshold_min: float
    threshold_max: float
    opacity: float

class SliceCoordsDict(TypedDict):
    """Dictionary of x,y click coordinates (integers) for nifti slices"""
    slice_1: Dict[Literal['x', 'y'], int]
    slice_2: Dict[Literal['x', 'y'], int]
    slice_3: Dict[Literal['x', 'y'], int]

class OrthoSliceIndexDict(TypedDict):
    """Dictionary of x,y,z slice indices for ortho view"""
    x: int
    y: int
    z: int

class MontageSliceDirectionIndexDict(TypedDict):
    """Dictionary of x,y,z slice indices for a direction in montage view"""
    slice_1: Dict[Literal['x', 'y', 'z'], int]
    slice_2: Dict[Literal['x', 'y', 'z'], int]
    slice_3: Dict[Literal['x', 'y', 'z'], int]

class MontageSliceIndexDict(TypedDict):
    """Dictionary of montage slice indices for montage view
    Keys are slice directions:
    x: axial
    y: coronal
    z: sagittal

    Each slice direction has a dictionary of indices for the three slices.
    """
    x: MontageSliceDirectionIndexDict # axial
    y: MontageSliceDirectionIndexDict # coronal
    z: MontageSliceDirectionIndexDict # sagittal

class MontageSliceCoordsDict(TypedDict):
    """Dictionary of montage slice click coordinates (integers)
    Keys are slice directions:
    x: axial
    y: coronal
    z: sagittal

    Each slice direction has a dictionary of coordinates for the three slices.
    """
    x: SliceCoordsDict # axial
    y: SliceCoordsDict # coronal
    z: SliceCoordsDict # sagittal

class NiftiDataDict(TypedDict):
    """Dictionary of NIFTI data input"""
    func_img: nib.Nifti1Image
    anat_img: nib.Nifti1Image
    mask_img: nib.Nifti1Image

class NiftiDataPreprocessedDict(TypedDict):
    """Dictionary of preprocessed NIFTI data input"""
    func_img: nib.Nifti1Image

class TaskDesignPlotOptionsDict(TypedDict):
    """Output dict from get_task_design_plot_options() method"""
    convolution: Optional[bool]
    scale: Optional[float]
    color: Optional[str]
    width: Optional[float]
    opacity: Optional[float]
    mode: Optional[Literal['lines', 'markers', 'lines+markers']]

# define output dicts from get_timecourse_global_plot_options() method
class TimeCourseGlobalPlotOptionsDict(TypedDict):
    """Output dict from get_timecourse_global_plot_options() method"""
    grid_on: Optional[bool]
    hover_text_on: Optional[bool]
    time_marker_on: Optional[bool]
    global_convolution: Optional[bool]
    
# define output dicts from get_timecourse_plot_options() method
class TimeCoursePlotOptionsDict(TypedDict):
    """Output dict from get_timecourse_plot_options() method"""
    color: Optional[str]
    plotType: Optional[Literal['block', 'hrf']]
    width: Optional[float]
    opacity: Optional[float]
    mode: Optional[Literal['lines', 'markers', 'lines+markers']]
    scale: Optional[float]

# define output dicts from get_time_marker_plot_options() method
class TimeMarkerPlotOptionsDict(TypedDict):
    """output dict from get_time_marker_plot_options() method"""
    opacity: Optional[float]
    width: Optional[float]
    shape: Optional[Literal['solid', 'dashed', 'dotted']]
    color: Optional[str]

# define outpus from get_metadata() method
class ViewerMetadataNiftiDict(TypedDict):
    """output dict from get_metadata() method for nifti data"""
    file_type: Literal['nifti']
    timepoint: int
    anat_input: bool
    mask_input: bool
    tr: Optional[float]
    slicetime_ref: Optional[float]
    view_state: Literal['ortho', 'montage']
    montage_slice_dir: Literal['x', 'y', 'z']
    timepoints: List[int]
    fmri_preprocessed: bool
    ts_preprocessed: bool
    global_min: float
    global_max: float
    slice_len: Dict[str, int]
    ts_enabled: bool
    task_enabled: bool  

class ViewerMetadataGiftiDict(TypedDict):
    """output dict from get_metadata() method for gifti data"""
    file_type: Literal['gifti']
    timepoint: int
    left_input: bool
    right_input: bool
    tr: Optional[float]
    slicetime_ref: Optional[float]
    vertices_left: List[float]
    faces_left: List[float]
    vertices_right: List[float]
    faces_right: List[float]
    timepoints: List[int]
    fmri_preprocessed: bool
    ts_preprocessed: bool
    global_min: float
    global_max: float
    ts_enabled: bool
    task_enabled: bool


# define output dicts from get_viewer_data() method
class ViewerDataNiftiDict(TypedDict):
    """output dict from get_viewer_data() method for nifti data"""
    anat_input: Optional[bool]
    mask_input: Optional[bool]
    func_data: Optional[np.ndarray]
    anat_data: Optional[np.ndarray]
    mask_data: Optional[np.ndarray]
    ts: Optional[Dict[str, List[float]]]
    task: Optional[Dict[str, List[float]]]
    is_fmri_preprocessed: Optional[bool]
    is_ts_preprocessed: Optional[bool]
    coord_labels: Optional[List[Tuple[int, int, int]]]

class ViewerDataGiftiDict(TypedDict):
    """output dict from get_viewer_data() method for gifti data"""
    left_input: Optional[bool]
    right_input: Optional[bool]
    func_data: Optional[np.ndarray]
    ts: Optional[Dict[str, List[float]]]
    task: Optional[Dict[str, List[float]]]
    is_fmri_preprocessed: Optional[bool]
    is_ts_preprocessed: Optional[bool]
