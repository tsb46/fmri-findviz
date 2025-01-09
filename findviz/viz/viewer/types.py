"""
Types for viewer
"""

from typing import TypedDict, Optional, List, Dict, Literal
import nibabel as nib

from findviz.viz.io.timecourse import TaskDesignDict

# define outpus from get_metadata() method
class ViewerMetadataNiftiDict(TypedDict):
    file_type: Literal['nifti']
    anat_input: bool
    mask_input: bool
    x_slice_idx: int
    y_slice_idx: int
    z_slice_idx: int
    view_state: Literal['ortho', 'montage']
    montage_slice_dir: Literal['x', 'y', 'z']
    timepoints: List[int]
    preprocessed: bool
    global_min: float
    global_max: float
    slice_len: Dict[str, int]
    ts_enabled: bool
    task_enabled: bool  


class ViewerMetadataGiftiDict(TypedDict):
    file_type: Literal['gifti']
    left_input: bool
    right_input: bool
    vertices_left: List[float]
    faces_left: List[float]
    vertices_right: List[float]
    faces_right: List[float]
    timepoints: List[int]
    preprocessed: bool
    global_min: float
    global_max: float
    ts_enabled: bool
    task_enabled: bool


# define output dicts from get_viewer_data() method
class ViewerDataNiftiDict(TypedDict):
    anat_input: Optional[bool]
    mask_input: Optional[bool]
    func_img: Optional[nib.Nifti1Image]
    anat_img: Optional[nib.Nifti1Image]
    mask_img: Optional[nib.Nifti1Image]
    ts: Optional[Dict[str, List[float]]]
    ts_labels: Optional[List[str]]
    task: Optional[TaskDesignDict]


class ViewerDataGiftiDict(TypedDict):
    left_input: Optional[bool]
    right_input: Optional[bool]
    left_func_img: Optional[nib.gifti.GiftiImage]
    right_func_img: Optional[nib.gifti.GiftiImage]
    vertices_left: Optional[List[float]]
    faces_left: Optional[List[float]]
    vertices_right: Optional[List[float]]
    faces_right: Optional[List[float]]
    ts: Optional[Dict[str, List[float]]]
    ts_labels: Optional[List[str]]
    task: Optional[TaskDesignDict]