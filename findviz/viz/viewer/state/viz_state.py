"""
This module defines the visualization state classes for the FIND viewer.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Tuple, List, Union

import nibabel as nib
import numpy as np

from findviz.viz.viewer.types import (
    ColorOptions, SliceCoordsDict, OrthoSliceIndexDict, MontageSliceIndexDict,
    MontageSliceCoordsDict, NiftiDataDict, NiftiDataPreprocessedDict,
    GiftiDataDict, GiftiDataPreprocessedDict
)
from findviz.viz.viewer.state.components import (
    FmriPlotOptions, TimeCoursePlotOptions, TaskDesignPlotOptions,
    AnnotationMarkerPlotOptions, TimeMarkerPlotOptions, DistancePlotOptions,
    TimeCourseColor, TimeCourseGlobalPlotOptions
)

@dataclass
class VisualizationState:
    """Base visualization state class containing common attributes.
    
    Attributes:
        tr: Repetition time. If not provided, set to None.
        slicetime_ref: Slicetime reference. If not provided, set to None.
        timepoints: Timepoint indices. Default is None
        timepoints_seconds: Timepoint indices in seconds. Default is None
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
        annotation_marker_plot_options: Marker plot options. Default is MarkerPlotOptions()
        time_marker_plot_options: Time marker plot options. Default is TimeMarkerPlotOptions()
        distance_data_enabled: Whether distance data is enabled and plotted. Default is False
        distance_data: Distance data. Default is None
        distance_plot_options: Distance plot options. Default is None.
    """
    # metadata
    tr: Optional[float] = None
    slicetime_ref: Optional[float] = None
    timepoints: Optional[List[int]] = None
    timepoints_seconds: Optional[List[float]] = None
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
    task_data: Dict[str, Dict[Literal['block', 'hrf'], List[float]]] = field(default_factory=dict)
    task_conditions: List[str] = field(default_factory=list)
    task_plot_options: dict[str, TaskDesignPlotOptions] = field(default_factory=dict)
    annotation_markers: List[int] = field(default_factory=list)
    annotation_selection: Optional[int] = None
    annotation_marker_plot_options: AnnotationMarkerPlotOptions = field(
        default_factory=AnnotationMarkerPlotOptions
    )
    time_marker_plot_options: TimeMarkerPlotOptions = field(
        default_factory=TimeMarkerPlotOptions
    )
    # outputs from distance analysis
    distance_data_enabled: bool = False
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
        ortho_slice_idx: Indices of ortho slices for NIFTI data. Default is empty dict {}.
        montage_slice_idx: Indices of montage slices for NIFTI data for each slice direction. 
            Default is empty dict {}.
        ortho_slice_coords: Coordinates of ortho slices for NIFTI data. 
            Default is empty dict {}.
        montage_slice_dir: Direction of montage slice for NIFTI data. 
            Default is 'z'.
        montage_slice_coords: Coordinates of montage slices for NIFTI data. 
            Default is empty dict {}.
        selected_slice: Selected slice for NIFTI data. Default is 'slice_1'.
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

    # selected slice
    selected_slice: Literal['slice_1', 'slice_2', 'slice_3'] = 'slice_1'


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
        coord_labels: Vertex number and hemisphere for each vertex
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
    both_hemispheres: bool = False
    
    # gifti data
    gifti_data: GiftiDataDict = field(default_factory=dict)
    gifti_data_preprocessed: GiftiDataPreprocessedDict = field(default_factory=dict)

    # selected vertex and hemisphere
    selected_vertex: Optional[int] = None
    selected_hemi: Optional[Literal['left', 'right']] = None

    # vertex number and hemisphere for each vertex
    left_coord_labels: Optional[List[Tuple[int, Literal['left']]]] = None
    right_coord_labels: Optional[List[Tuple[int, Literal['right']]]] = None

    def __post_init__(self):
        # set both hemispheres to True if left and right hemispheres are provided
        if self.left_input and self.right_input:
            self.both_hemispheres = True
            