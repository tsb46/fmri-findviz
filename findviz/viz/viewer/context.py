
"""
Visualization Context

This module provides a context for visualization state, which includes the state of the
visualization and the data associated with the visualization.

Classes:
    VisualizationContext: Context for visualization state
"""
from typing import Dict, Optional, List, Literal, Any, Union, Tuple

import numpy as np
import nibabel as nib

from findviz.logger_config import setup_logger
from findviz.viz.analysis.scaler import SignalScaler, SignalShifter
from findviz.viz.viewer.state.viz_state import (
    NiftiVisualizationState, 
    GiftiVisualizationState
)
from findviz.viz.viewer.state.components import (
    DistancePlotOptions,
    FmriPlotOptions, 
    TimeCoursePlotOptions, 
    TaskDesignPlotOptions,
    TimeCourseColor
)
from findviz.viz.viewer.types import (
    ViewerDataNiftiDict, ViewerDataGiftiDict, 
    ViewerMetadataNiftiDict, ViewerMetadataGiftiDict,
    FmriPlotOptionsDict, TimeCourseGlobalPlotOptionsDict,
    TimeCoursePlotOptionsDict, TimeMarkerPlotOptionsDict, 
    TaskDesignPlotOptionsDict, DistancePlotOptionsDict,
    OrthoSliceIndexDict, AnnotationMarkerPlotOptionsDict, 
    MontageSliceDirectionIndexDict, MontageSliceCoordsDict,
    MontageSliceIndexDict, CrosshairCoordsDict, DirectionLabelCoordsDict,
    ColorOptions
)
from findviz.viz.viewer.utils import (
    apply_mask_nifti, get_coord_labels_gifti, 
    get_coord_labels_nifti, get_ortho_slice_coords, 
    get_ts_minmax, package_nii_metadata, 
    package_gii_metadata, package_distance_metadata, 
    requires_state, transform_to_world_coords
)

logger = setup_logger(__name__)


class VisualizationContext:
    """
    Represents a single visualization context (input files or analysis results).

    This class provides a context for visualization state, which includes the state of the
    visualization and the data associated with the visualization.

    Attributes:
        context_id (str): The id of the visualization context.
        _state (Optional[NiftiVisualizationState | GiftiVisualizationState]): The visualization state
    
    Methods:
        add_annotation_marker(): Add annotation marker
        add_timeseries(): Add timeseries data to state
        add_task_design(): Add task design data to state
        clear_annotation_markers(): Clear annotation markers
        clear_distance_plot_state(): Clear distance plot state
        clear_fmri_preprocessed(): Clear preprocessed fMRI data
        clear_timecourse_preprocessed(): Clear preprocessed timecourse data
        clear_state(): Clear state
        convert_timepoints(): Convert timepoints to seconds
        create_distance_plot_state(): Create distance plot state
        create_nifti_state(): Initialize state for NIFTI data
        create_gifti_state(): Initialize state for GIFTI data
        get_annotation_marker_plot_options(): Get annotation marker plot options
        get_click_coords(): Get click coordinates
        get_crosshair_coords(): Get coordinates for crosshair shape
        get_distance_plot_options(): Get distance plot options
        get_fmri_plot_options(): Get plot options
        get_last_timecourse(): Get last added fmri timecourse
        get_slice_idx(): Get slice indices
        get_task_design_plot_options(): Get task design plot options for a given label
        get_timecourse_global_plot_options(): Get time course global plot options
        get_timecourse_plot_options(): Get time course plot options for a given label
        get_timecourse_shift_history(): Get time course shift history
        get_timepoints(): Get all timepoints
        get_time_marker_plot_options(): Get time marker plot options
        get_world_coords(): Get world coordinates of currently selected coordinates
        get_viewer_metadata(): Get metadata for viewer
        get_viewer_data(): Get formatted data for viewer
        move_annotation_selection(): Move annotation selection
        pop_annotation_marker(): Pop most recent annotation marker from state
        pop_fmri_timecourse(): Pop most recent fmri timecourse from state
        reset_fmri_color_options(): Reset fMRI color options to original
        reset_timecourse_shift(): Reset time course shift (scale or constant)
        set_timepoints(): set the timepoints for the time course
        set_tr(): set the fMRI TR (repitition time)
        store_fmri_preprocessed(): Store preprocessed fMRI data
        store_timecourse_preprocessed(): Store preprocessed timecourse data
        update_annotation_marker_plot_options(): Update annotation marker plot options
        update_annotation_selection(): Update annotation selection
        update_distance_plot_options(): Update distance plot options
        update_location(): Update brain location data
        update_fmri_plot_options(): Update plot options
        update_montage_slice_dir(): Update montage slice direction
        update_montage_slice_idx(): Update montage slice indices
        update_timecourse_global_plot_options(): Update time course global plot options
        update_task_design_plot_options(): Update task design plot options
        update_timecourse(): Update time course data with new timecourse and label
        update_timecourse_global_plot_options(): Update time course global plot options
        update_timecourse_plot_options(): Update time course plot options for a given label
        update_timecourse_shift(): Update time course shift (scale or constant)
        update_time_marker_plot_options(): Update time marker plot options
        update_timepoint(): Update timepoint data
        update_view_state(): Update view state
    """
    def __init__(self, context_id: str):
        self.context_id = context_id
        self._state = Optional[NiftiVisualizationState | GiftiVisualizationState]
    
    @requires_state
    @property
    def allowed_precision(self) -> int:
        return self._state.allowed_precision
    
    @requires_state
    @property
    def annotation_highlight_on(self) -> bool:
        return self._state.annotation_selection_highlight

    @requires_state
    @property
    def annotation_markers(self) -> List[int]:
        return self._state.annotation_markers
    
    @requires_state
    @property
    def annotation_marker_plot_options(self) -> AnnotationMarkerPlotOptionsDict:
        return self._state.annotation_marker_plot_options
    
    @requires_state
    @property
    def annotation_selection(self) -> int:
        return self._state.annotation_selection

    @requires_state
    @property
    def both_hemispheres(self) -> bool:
        if self._state.file_type == 'gifti':
            return self._state.both_hemispheres
        else:
            logger.warning("both_hemispheres attribute does not exist for NIFTI data")
            return False
        
    @requires_state
    @property
    def coord_labels(self) -> np.ndarray | List[Tuple[int, Literal['left', 'right']]]:
        if self._state.file_type == 'nifti':
            return self._state.coord_labels
        else:
            return self._state.left_coord_labels, self._state.right_coord_labels
    
    @requires_state
    @property
    def color_options_original(self) -> ColorOptions:
        return self._state.color_options_original

    @requires_state
    @property
    def distance_data(self) -> np.ndarray:
        if self._state.distance_data is None:
            logger.error("No distance data exists")
            return None
        return self._state.distance_data
    
    @requires_state
    @property
    def fmri_preprocessed(self) -> bool:
        return self._state.fmri_preprocessed

    @requires_state
    @property
    def fmri_file_type(self) -> Literal['nifti', 'gifti']:
        return self._state.file_type
    
    @requires_state
    @property
    def left_surface_input(self) -> bool:
        if self._state.file_type == 'gifti':
            return self._state.left_input
        else:
            logger.warning("left_surface_input attribute does not exist for NIFTI data")
            return False

    @requires_state
    @property
    def montage_slice_coords(self) -> Optional[MontageSliceCoordsDict]:
        if self._state.file_type == 'nifti':
            montage_slice_dir = self._state.montage_slice_dir
            return self._state.montage_slice_coords[montage_slice_dir]
        else:
            logger.error("No montage slice coords exist for GIFTI data")
            return None
    
    @requires_state
    @property
    def montage_slice_dir(self) -> Optional[Literal['x', 'y', 'z']]:
        if self._state.file_type == 'nifti':
            return self._state.montage_slice_dir
        else:
            logger.error("No montage slice dir exist for GIFTI data")
            return None
    
    @requires_state
    @property
    def montage_slice_idx(self) -> Optional[MontageSliceIndexDict]:
        if self._state.file_type == 'nifti':
            return self._state.montage_slice_idx
        else:
            logger.error("No montage slice idx exist for GIFTI data")
            return None
    
    @requires_state
    @property
    def n_timepoints(self) -> int:
        return len(self._state.timepoints)
    
    @requires_state
    @property
    def right_surface_input(self) -> bool:
        if self._state.file_type == 'gifti':
            return self._state.right_input
        else:
            logger.warning("right_surface_input attribute does not exist for NIFTI data")
            return False
    
    @requires_state
    @property
    def selected_hemi(self) -> Literal['left', 'right']:
        if self._state.file_type == 'gifti':
            return self._state.selected_hemi
        else:
            logger.warning("Selected hemisphere attribute does not exist for NIFTI data")
            return None
    
    @requires_state
    @property
    def selected_slice(self) -> Literal['slice_1', 'slice_2', 'slice_3']:
        if self._state.file_type == 'nifti':
            return self._state.selected_slice
        else:
            logger.warning("Selected slice attribute does not exist for GIFTI data")
            return None
    
    @requires_state
    @property
    def selected_vertex(self) -> int:
        if self._state.file_type == 'gifti':
            return self._state.selected_vertex
        else:
            logger.warning("Selected vertex attribute does not exist for NIFTI data")
            return None
    
    @requires_state
    @property
    def slice_len(self) -> Dict[str, int]:
        if self._state.file_type == 'nifti':
            return self._state.slice_len
        else:
            logger.error("No slice lengths exist for GIFTI data")
            return None

    @requires_state
    @property
    def slice_mid(self) -> Optional[Dict[str, int]]:
        if self._state.file_type == 'nifti':
            slice_mid = {
                'x': self._state.slice_len['x'] // 2,
                'y': self._state.slice_len['y'] // 2,
                'z': self._state.slice_len['z'] // 2
            }
            return slice_mid
        else:
            logger.error("No slice mid exist for GIFTI data")
            return None
        
    @requires_state
    @property
    def state(self) -> NiftiVisualizationState | GiftiVisualizationState:
        return self._state

    @requires_state
    @property
    def task_conditions(self) -> List[str]:
        return self._state.task_conditions

    @requires_state
    @property
    def task_plot_options(self) -> Dict[str, TaskDesignPlotOptions]:
        return self._state.task_plot_options

    @requires_state
    @property
    def timepoint(self) -> int:
        return self._state.timepoint
    
    @requires_state
    @property
    def timecourse_source(self) -> Dict[str, Literal['timecourse', 'task']]:
        # get time course labeled by task or timecourse
        timecourse_source = {}
        for label in self._state.ts_labels:
            if label in self._state.task_conditions:
                timecourse_source[label] = 'task'
            else:
                timecourse_source[label] = 'timecourse'
        return timecourse_source
    
    @requires_state
    @property
    def ts_fmri_plotted(self) -> bool:
        return self._state.ts_fmri_plotted
    
    @requires_state
    @property
    def ts_labels(self) -> List[str]:
        return self._state.ts_labels
    
    @requires_state
    @property
    def ts_labels_preprocessed(self) -> List[str]:
        if self._state.ts_preprocessed:
            return self._state.ts_labels_preprocessed
        else:
            logger.warning("No preprocessed time course labels exist")
            return []

    @requires_state
    @property
    def ts_plot_options(self) -> Dict[str, TimeCoursePlotOptions]:
        return self._state.ts_plot_options
    
    @requires_state
    @property
    def ts_preprocessed(self) -> bool:
        return self._state.ts_preprocessed
    
    @requires_state
    @property
    def view_state(self) -> Literal['ortho', 'montage']: 
        if self._state.file_type == 'nifti':
            return self._state.view_state
        else:
            logger.warning("view_state attribute does not exist for GIFTI data")
            return None

    @requires_state
    def add_annotation_markers(self, markers: int | List[int]) -> None:
        """Add annotation markers
        
        Arguments:
            markers: The time point marker(s) to add specified as an 
                integer or list of integers
        """
        # add marker(s) to annotation markers, if not already present
        if isinstance(markers, int):
            if markers not in self._state.annotation_markers:
                self._state.annotation_markers.append(markers)
                # set annotation selection as current selection
                self._state.annotation_selection = markers
        else:
            for m in markers:
                if m not in self._state.annotation_markers:
                    self._state.annotation_markers.append(m)
                # set annotation selection as last appended marker
                self._state.annotation_selection = self._state.annotation_markers[-1]

        # sort annotation markers
        self._state.annotation_markers.sort()
        
    @requires_state
    def add_timeseries(
        self, 
        timeseries: Optional[Dict[str, np.ndarray]] = None
    ) -> None:
        """Add time series data if not already present. If no time series data is 
        provided, initialize with empty dict.
        
        Arguments:
            timeseries: The time series data to add. If none, initialize with empty dict.
        """
        # Initialize time series data
        if timeseries is None:
            timeseries = {}
            self._state.ts_enabled = False
        else:
            self._state.ts_data = timeseries
            self._state.ts_enabled = True

        self._state.ts_labels = list(timeseries.keys())

        # the only ts types passed are user input time courses
        self._state.ts_type.update({label: 'user' for label in self._state.ts_labels})

        # Create plot options for each timeseries with unique colors
        for label in self._state.ts_labels:
            plot_options = TimeCoursePlotOptions.with_next_color(
                self._state.used_colors,
                label=label
            )
            self._state.used_colors.add(plot_options.color)
            self._state.ts_plot_options[label] = plot_options
        
        # update global ts min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()

    
    @requires_state
    def add_task_design(
        self, 
        task_data: Dict[str, Dict[str, List[float]]], 
        tr: float, 
        slicetime_ref: float
    ) -> None:
        """Add task design data
        
        Arguments:
            task_data: The task design data to add. Conditions are keys, and
                time courses are values. Time courses are convolved -'hrf' and 
                not convolved -'block'. Example: 
                {'condition_1': {'hrf': [1, 2, 3], 'block': [4, 5, 6]}}
            tr: The repetition time.
            slicetime_ref: The slicetime reference.
        """
        # add conditions
        self._state.task_conditions = list(task_data.keys())
        self._state.task_data = task_data
        self._state.task_enabled = True
        # add metadata
        self.set_tr(tr)
        self._state.slicetime_ref = slicetime_ref

        # Create plot options for each task condition with unique colors
        for label in self._state.task_conditions:
            plot_options = TaskDesignPlotOptions.with_next_color(
                self._state.used_colors,
                label=label
            )
            self._state.used_colors.add(plot_options.color)
            self._state.task_plot_options[label] = plot_options
        
        # update global ts min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()
    
    @requires_state
    def check_ts_preprocessed(self, label: str) -> bool:
        """Check if specific time course is preprocessed
        
        Arguments:
            label: The label of the time course to check
            
        Returns:
            bool: True if time course is preprocessed, False otherwise
        """
        if label not in self._state.ts_preprocessed:
            logger.warning(f"Time course {label} not stored in state")
            return False
        
        # check if time course is preprocessed
        return self._state.ts_preprocessed[label]
    
    @requires_state
    def clear_annotation_markers(self) -> None:
        """Clear annotation markers"""
        logger.info("Clearing annotation markers")
        self._state.annotation_markers = []
        self._state.annotation_selection = None
    
    @requires_state
    def clear_distance_plot_state(self) -> None:
        """Clear distance plot state"""
        logger.info("Clearing distance plot state")
        if not self._state.distance_data_enabled:
            logger.error("No distance data exists")
            return
        self._state.distance_data_enabled = False
        self._state.distance_data = None
        self._state.distance_plot_options = None

    @requires_state
    def clear_fmri_preprocessed(self) -> None:
        """Clear preprocessed fMRI data."""
        logger.info("Clearing preprocessed fMRI data")
        self._state.fmri_preprocessed = False
        if self._state.file_type == 'nifti':
            self._state.nifti_data_preprocessed.clear()
        else:
            self._state.gifti_data_preprocessed.clear()

        # clear preprocessed plot options
        self._state.preprocessed_plot_options = None

    @requires_state
    def clear_timecourse_preprocessed(self, ts_labels: List[str]) -> None:
        """Clear preprocessed timecourse data for specified time courses.
        
        Arguments:
            ts_labels: The labels of the time courses to clear
        """
        logger.info(f"Clearing preprocessed timecourse data for {ts_labels}")
        for ts_label in ts_labels:
            self._state.ts_preprocessed[ts_label] = False
            self._state.ts_data_preprocessed[ts_label] = None
            self._state.ts_labels_preprocessed.remove(ts_label)
            # rename time course in plot options for display
            self._state.ts_plot_options[ts_label].label = ts_label
            # clear shift history
            self._state.ts_plot_options[ts_label].clear_preprocess_history()

        # update time course global min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()

    @requires_state
    def clear_state(self) -> None:
        """Clear state."""
        logger.info("Clearing data manager state")
        self._state = None
    
    @requires_state
    def convert_timepoints(self, round_to: int = 5) -> None:
        """Convert timepoints to seconds"""
        logger.info("Converting timepoints to seconds")
        tr = self._state.tr
        if tr is None:
            logger.error("TR is not set")
            return
        self._state.timepoints_seconds = [
            round(tp * tr, round_to) for tp in self._state.timepoints
        ]
    
    @requires_state
    def create_distance_plot_state(
        self,
        distance_data: np.ndarray,
    ) -> None:
        """Create distance plot state
        
        Arguments:
            distance_data: The time point distance data to plot
        """
        logger.info("Creating distance plot state")
        self._state.distance_data_enabled = True
        self._state.distance_data = distance_data
        metadata = package_distance_metadata(
            distance_data,
            slider_steps=100,
            precision=6
        )
        self._state.distance_plot_options = DistancePlotOptions(
            color_min=metadata['color_min'],
            color_max=metadata['color_max'],
            color_range=metadata['color_range'],
            precision=metadata['precision'],
            slider_step_size=metadata['slider_step_size']
        )
    
    def create_nifti_state(
        self, 
        func_img: nib.Nifti1Image,
        anat_img: Optional[nib.Nifti1Image] = None,
        mask_img: Optional[nib.Nifti1Image] = None
    ) -> None:
        """Create visualization state for NIFTI data
        
        Arguments:
            func_img: The functional NIFTI image
            anat_img: The anatomical NIFTI image (optional)
            mask_img: The mask NIFTI image (optional)
        """
        metadata = package_nii_metadata(func_img)
        
        self._state = NiftiVisualizationState(
            timepoints=metadata['timepoints'],
            global_min=metadata['global_min'],
            global_max=metadata['global_max'],
            slice_len=metadata['slice_len'],
            ortho_slice_idx=metadata['ortho_slice_idx'],
            montage_slice_idx=metadata['montage_slice_idx'],
            ortho_slice_coords=metadata['ortho_slice_coords'],
            montage_slice_coords=metadata['montage_slice_coords'],
            fmri_plot_options=FmriPlotOptions(
                color_min=metadata['color_min'],
                color_max=metadata['color_max'],
                color_range=metadata['color_range'],
                slider_step_size=metadata['slider_step_size'],
                precision=metadata['precision'],
                threshold_range=metadata['threshold_range']
            ),
            coord_labels=get_coord_labels_nifti(func_img),
            func_affine=func_img.affine,
            func_header=func_img.header
        )

        # preserve original color options
        self._state.color_options_original = {
            'color_min': self._state.fmri_plot_options.color_min,
            'color_max': self._state.fmri_plot_options.color_max,
            'color_range': self._state.fmri_plot_options.color_range,
            'threshold_min': self._state.fmri_plot_options.threshold_min,
            'threshold_max': self._state.fmri_plot_options.threshold_max,
            'threshold_range': self._state.fmri_plot_options.threshold_range,
            'opacity': self._state.fmri_plot_options.opacity
        }

        # apply mask if present
        if mask_img:
            logger.info("Applying mask to NIFTI data")
            func_img = apply_mask_nifti(func_img, mask_img)

        self._state.nifti_data['func_img'] = func_img
        self._state.nifti_data['anat_img'] = anat_img
        self._state.nifti_data['mask_img'] = mask_img
        
        # Store inputs
        if anat_img:
            self._state.anat_input = True
        if mask_img:
            self._state.mask_input = True
                
    def create_gifti_state(
        self,
        left_func_img: Optional[nib.GiftiImage] = None,
        right_func_img: Optional[nib.GiftiImage] = None,
        left_mesh: Optional[nib.GiftiImage] = None,
        right_mesh: Optional[nib.GiftiImage] = None,
        faces_left: Optional[np.ndarray] = None,
        faces_right: Optional[np.ndarray] = None,
        vertices_left: Optional[np.ndarray] = None,
        vertices_right: Optional[np.ndarray] = None
    ) -> None:
        """Create visualization state for GIFTI data. At least one hemisphere
        functional and mesh GIFTI images must be provided. Instead of a mesh
        GIFTI image, the faces and vertices of the mesh can be provided. If mesh
        image is provided, the faces and vertices are ignored.
        
        Arguments:
            left_func_img: The left functional GIFTI image
            right_func_img: The right functional GIFTI image
            left_mesh: The left mesh GIFTI image
            right_mesh: The right mesh GIFTI image
            left_faces: The left faces of the mesh
            right_faces: The right faces of the mesh
            left_vertices: The left vertices of the mesh
            right_vertices: The right vertices of the mesh
        """
        metadata = package_gii_metadata(left_func_img, right_func_img)
        
        # check right and/or left hemisphere inputs
        if left_func_img:
            left_input = True
        else:
            left_input = False

        if right_func_img:
            right_input = True
        else:
            right_input = False

        self._state = GiftiVisualizationState(
            left_input=left_input,
            right_input=right_input,
            timepoints=metadata['timepoints'],
            global_min=metadata['global_min'],
            global_max=metadata['global_max'],
            fmri_plot_options=FmriPlotOptions(
                color_min=metadata['color_min'],
                color_max=metadata['color_max'],
                color_range=metadata['color_range'],
                slider_step_size=metadata['slider_step_size'],
                precision=metadata['precision'],
                threshold_range=metadata['threshold_range']
            ),
            left_coord_labels=get_coord_labels_gifti(left_func_img, 'left'),
            right_coord_labels=get_coord_labels_gifti(right_func_img, 'right')
        )  
        # preserve original color options
        self._state.color_options_original = {
            'color_min': self._state.fmri_plot_options.color_min,
            'color_max': self._state.fmri_plot_options.color_max,
            'color_range': self._state.fmri_plot_options.color_range,
            'threshold_min': self._state.fmri_plot_options.threshold_min,
            'threshold_max': self._state.fmri_plot_options.threshold_max,
            'threshold_range': self._state.fmri_plot_options.threshold_range,
            'opacity': self._state.fmri_plot_options.opacity
        }

        # Store functional data
        self._state.gifti_data['left_func_img'] = left_func_img
        self._state.gifti_data['right_func_img'] = right_func_img
            
        # Store mesh data
        # TODO: ensure first position is coordinates, and second is faces
        if left_mesh:
            self._state.vertices_left = left_mesh.darrays[0].data.tolist()
            self._state.faces_left = left_mesh.darrays[1].data.tolist()
        if right_mesh:
            self._state.vertices_right = right_mesh.darrays[0].data.tolist()
            self._state.faces_right = right_mesh.darrays[1].data.tolist()
        
        # if no mesh data is provided, use faces and vertices
        if not left_mesh and not right_mesh:
            self._state.vertices_left = vertices_left
            self._state.faces_left = faces_left
            self._state.vertices_right = vertices_right
            self._state.faces_right = faces_right
        
    
    @requires_state
    def get_annotation_marker_plot_options(self) -> AnnotationMarkerPlotOptionsDict:
        """Get annotation marker plot options.
        
        Returns:
            AnnotationMarkerPlotOptionsDict: Marker plot options
        """
        return self._state.annotation_marker_plot_options.to_dict()
    
    @requires_state
    def get_click_coords(self) -> Dict[str, Any]:
        """Get click coordinates for brain data
        
        Returns:
            Dict[str, Any]: X, Y click coordinates for 2D slice data (nifti) or
                surface coordinates (gifti)
        """
        if self._state.file_type == 'nifti':
            if self._state.view_state == 'ortho':
                return self._state.ortho_slice_coords
            else:
                slice_dir = self._state.montage_slice_dir
                return self._state.montage_slice_coords[slice_dir]
        else:
            return {
                'selected_vertex': self._state.selected_vertex,
                'selected_hemi': self._state.selected_hemi
            }
    
    @requires_state
    def get_crosshair_coords(self) -> CrosshairCoordsDict:
        """Get x,y coordinates for crosshair shape
          for nifti plot from slice length and indices
          
        Returns:
            CrosshairCoordsDict: Coordinates for crosshair shape to plot 
                on nifti fmri plot
        """
        if self._state.file_type == 'nifti':
            if self._state.view_state == 'ortho':
                crosshair_data = {
                    'slice_1': {
                        'len_x': self._state.slice_len['y'] - 1,
                        'len_y': self._state.slice_len['z'] - 1,
                        'x': self._state.ortho_slice_coords['slice_1']['x'],
                        'y': self._state.ortho_slice_coords['slice_1']['y']
                    },
                    'slice_2': {
                        'len_x': self._state.slice_len['x'] - 1,
                        'len_y': self._state.slice_len['z'] - 1,
                        'x': self._state.ortho_slice_coords['slice_2']['x'],
                        'y': self._state.ortho_slice_coords['slice_2']['y']
                    },
                    'slice_3': {
                        'len_x': self._state.slice_len['x'] - 1,
                        'len_y': self._state.slice_len['y'] - 1,
                        'x': self._state.ortho_slice_coords['slice_3']['x'],
                        'y': self._state.ortho_slice_coords['slice_3']['y']
                    }
                }
            else:
                slice_dir = self._state.montage_slice_dir
                if slice_dir == 'x':
                    len_x = self._state.slice_len['y'] - 1
                    len_y = self._state.slice_len['z'] - 1
                elif slice_dir == 'y':
                    len_x = self._state.slice_len['x'] - 1
                    len_y = self._state.slice_len['z'] - 1
                elif slice_dir == 'z':
                    len_x = self._state.slice_len['x'] - 1
                    len_y = self._state.slice_len['y'] - 1
                else:
                    logger.error(f"Invalid slice direction: {slice_dir}")
                    return {}
                
                crosshair_data = {
                    'slice_1': {
                        'len_x': len_x,
                        'len_y': len_y,
                        'x': self._state.montage_slice_coords[slice_dir]['slice_1']['x'],
                        'y': self._state.montage_slice_coords[slice_dir]['slice_1']['y']
                    },
                    'slice_2': {
                        'len_x': len_x,
                        'len_y': len_y,
                        'x': self._state.montage_slice_coords[slice_dir]['slice_2']['x'],
                        'y': self._state.montage_slice_coords[slice_dir]['slice_2']['y']
                    },
                    'slice_3': {
                        'len_x': len_x,
                        'len_y': len_y,
                        'x': self._state.montage_slice_coords[slice_dir]['slice_3']['x'],
                        'y': self._state.montage_slice_coords[slice_dir]['slice_3']['y']
                    }
                }
            return crosshair_data
        
        else:
            logger.error("Crosshair plot not supported for GIFTI data")
            return {}
    
    @requires_state
    def get_direction_label_coords(self) -> DirectionLabelCoordsDict:
        """Get coordinates for direction labels to plot on NIFTI data
        
        Returns:
            DirectionLabelCoordsDict: Coordinates for direction marker labels
                (e.g. Anterior, Posterior, Superior, Inferior) to plot on nifti
                fmri plot
        """
        if self._state.file_type == 'nifti':
            if self._state.view_state == 'ortho':
                return {
                    'slice_1': self._get_slice_direction_label_coords('x'),
                    'slice_2': self._get_slice_direction_label_coords('y'),
                    'slice_3': self._get_slice_direction_label_coords('z')
                }
            else:
                slice_dir = self._state.montage_slice_dir
                return {
                    'slice_1': self._get_slice_direction_label_coords(slice_dir),
                    'slice_2': self._get_slice_direction_label_coords(slice_dir),
                    'slice_3': self._get_slice_direction_label_coords(slice_dir)
                }
        else:
            logger.error("Direction labels not supported for GIFTI data")
            return {}
    
    @requires_state
    def get_distance_plot_options(self) -> DistancePlotOptionsDict:
        """Get distance plot options
        
        Returns:
            DistancePlotOptionsDict: Plot options for time point distance plot
        """
        if self._state.distance_plot_options:
            return self._state.distance_plot_options.to_dict()
        else:
            logger.error("No distance plot state exists")
            return {}
    
    @requires_state
    def get_fmri_plot_options(self) -> FmriPlotOptionsDict:
        """Get plot options
        
        Returns:
            FmriPlotOptionsDict: Plot options for fmri data
        """
        if self._state.fmri_preprocessed:
            data = self._state.preprocessed_fmri_plot_options.to_dict()
        else:
            data = self._state.fmri_plot_options.to_dict()
        
        return data
    
    @requires_state
    def get_last_timecourse(self) -> dict[str, List[float]]:
        """Get last added timecourse
        
        Returns:
            dict[str, List[float]]: Last added timecourse
        """
        # check if there are any timecourses
        if not self._state.ts_labels:
            logger.warning("No timecourses to get")
            return {}
        # get last fmri timecourse
        last_label = self._state.ts_labels[-1]
        return {
            last_label: self._state.ts_data[last_label]
        }
    
    @requires_state
    def get_slice_idx(self) -> OrthoSliceIndexDict | MontageSliceDirectionIndexDict:
        """Get slice indices of currently selected coordinates
        
        Returns:
            OrthoSliceIndexDict | MontageSliceDirectionIndexDict: Slice indices for either
            ortho or montage view. For montage view, the indices returned are for the
            currently selected slice direction.
        """
        if self._state.view_state == 'ortho':
            return self._state.ortho_slice_idx
        else:
            slice_dir = self._state.montage_slice_dir
            return self._state.montage_slice_idx[slice_dir]
    
    @requires_state
    def get_task_design_plot_options(
        self, 
        label: Optional[str] = None
    ) -> TaskDesignPlotOptionsDict | Dict[str, TaskDesignPlotOptionsDict]:
        """Get task design plot options for a given label
        
        Returns:
            TaskDesignPlotOptionsDict | Dict[str, TaskDesignPlotOptionsDict]: Task design plot options
        """
        if label:
            return self._state.task_plot_options[label].to_dict()
        else:
            return {
                label: plot_options.to_dict()
                for label, plot_options in self._state.task_plot_options.items()
            }
    
    @requires_state
    def get_timecourse_global_plot_options(self) -> TimeCourseGlobalPlotOptionsDict:
        """Get time course global plot options
        
        Returns:
            TimeCourseGlobalPlotOptionsDict: Time course global plot options - not specific
            to an individual time course
        """
        return self._state.time_course_global_plot_options.to_dict()
    
    @requires_state
    def get_timecourse_plot_options(
        self, 
        label: Optional[str] = None
    ) -> TimeCoursePlotOptionsDict | Dict[str, TimeCoursePlotOptionsDict]:
        """Get time course plot options for a given label
        
        Arguments:
            label: The label of the time course to get plot options for
        
        Returns:
            TimeCoursePlotOptionsDict | Dict[str, TimeCoursePlotOptionsDict]: 
                Time course plot options
        """
        if label:
            return self._state.ts_plot_options[label].to_dict()
        else:
            return {
                label: plot_options.to_dict()
                for label, plot_options in self._state.ts_plot_options.items()
            }
    
    @requires_state
    def get_timecourse_shift_history(
        self, 
        label: str,
        source: Literal['timecourse', 'task']
    ) -> Dict[str, List[float]]:
        """Get timecourse shift history

        Arguments:
            label: The label of the time course to get shift history
            source: The time course source, either 'timecourse' or 'task'

        Returns:
            Dict[str, List[float]]: Timecourse shift history 
                with keys 'constant' and 'scale'
        """
        if source == 'timecourse':
            if self._state.ts_preprocessed[label]:
                constant = self._state.ts_plot_options[label].preprocess_constant
                scale = self._state.ts_plot_options[label].preprocess_scale
            else:
                constant = self._state.ts_plot_options[label].constant
                scale = self._state.ts_plot_options[label].scale
        else:
            constant = self._state.task_plot_options[label].constant
            scale = self._state.task_plot_options[label].scale

        return {
            'scale': scale.scale_history, 
            'constant': constant.shift_history
        }

    @requires_state
    def get_timepoints(self) -> List[float | int]:
        """Return timepoints in seconds or in TRs
        
        Returns:
            List[float | int]: All timepoints
        """
        if self._state.fmri_plot_options.tr_convert_on:
            return self._state.timepoints_seconds
        else:
            return self._state.timepoints
    
    @requires_state
    def get_time_marker_plot_options(self) -> TimeMarkerPlotOptionsDict:
        """Get time marker plot options. The time marker is a vertical line
        that is plotted on the time course plot at the current time point.
        
        Returns:
            TimeMarkerPlotOptionsDict: Time marker plot options
        """
        return self._state.time_marker_plot_options.to_dict()
    
    @requires_state
    def get_world_coords(self) -> Tuple[float, float, float] | None:
        """Get world coordinates of currently selected coordinates
        
        Returns:
            Tuple[float, float, float]: World coordinates
        """
        if self._state.file_type == 'nifti':
            # get slice indices of currently selected coordinates
            slice_idx = self.get_slice_idx()
            # if montage view, get the slice indices for the currently selected slice 
            if self._state.view_state == 'montage':
                slice_idx = slice_idx[self._state.selected_slice]
            # get the world coordinates
            return transform_to_world_coords(
                slice_idx,
                self._state.func_affine
            )
        else:
            logger.warning("World coordinates not supported for GIFTI data")
            return None
    
    @requires_state
    def get_viewer_metadata(self) -> ViewerMetadataNiftiDict | ViewerMetadataGiftiDict:
        """Get metadata for viewer
        
        Returns:
            ViewerMetadataNiftiDict | ViewerMetadataGiftiDict: Metadata for viewer
        """        
        if self._state.file_type == 'nifti':
            data = ViewerMetadataNiftiDict(
                file_type=self._state.file_type,
                timepoint=self._state.timepoint,
                anat_input=self._state.anat_input,
                mask_input=self._state.mask_input,
                tr=self._state.tr,
                slicetime_ref=self._state.slicetime_ref,
                timepoints=self._state.timepoints,
                timepoints_seconds=self._state.timepoints_seconds,
                global_min=self._state.global_min,
                global_max=self._state.global_max,
                slice_len=self._state.slice_len,
                fmri_preprocessed=self._state.fmri_preprocessed,
                ts_preprocessed=self._state.ts_preprocessed,
                ts_enabled=self._state.ts_enabled,
                task_enabled=self._state.task_enabled
            )
        else:
            data = ViewerMetadataGiftiDict(
                file_type=self._state.file_type,
                timepoint=self._state.timepoint,
                left_input=self._state.left_input,
                right_input=self._state.right_input,
                tr=self._state.tr,
                slicetime_ref=self._state.slicetime_ref,
                vertices_left=self._state.vertices_left,
                faces_left=self._state.faces_left,
                vertices_right=self._state.vertices_right,
                faces_right=self._state.faces_right,
                timepoints=self._state.timepoints,
                timepoints_seconds=self._state.timepoints_seconds,
                global_min=self._state.global_min,
                global_max=self._state.global_max,
                fmri_preprocessed=self._state.fmri_preprocessed,
                ts_preprocessed=self._state.ts_preprocessed,
                ts_enabled=self._state.ts_enabled,
                task_enabled=self._state.task_enabled
            )

        return data

    @requires_state
    def get_viewer_data(
        self,
        fmri_data: bool = True,
        time_course_data: bool = True,
        task_data: bool = True,
        coord_labels: bool = False
    ) -> ViewerDataNiftiDict | ViewerDataGiftiDict:
        """Get data formatted for viewer.

        Arguments:
            fmri_data: Whether to include fMRI image data. Defaults to True.
            time_course_data: Whether to include time course data. Defaults to True.
            task_data: Whether to include task design data. Defaults to True.
            coord_labels: Whether to include coordinate labels. Defaults to False.

        Returns:
            ViewerDataNiftiDict | ViewerDataGiftiDict: Dictionary containing viewer data formatted
            based on file type (NIFTI or GIFTI). Returns empty dict if no state exists.
        """
        data = {}
        
        # Add file type specific data
        if fmri_data:
            if self.fmri_file_type == 'nifti':
                if self._state.fmri_preprocessed:
                    data.update({
                        'func_img': self._state.nifti_data_preprocessed['func_img'],
                        'is_fmri_preprocessed': True
                    })
                else:
                    data.update({
                        'func_img': self._state.nifti_data['func_img'],
                        'is_fmri_preprocessed': False
                    })

                data.update({
                    'anat_input': self._state.anat_input,
                    'mask_input': self.state.mask_input,
                    'anat_img': self._state.nifti_data['anat_img'],
                    'mask_img': self._state.nifti_data['mask_img']
                })
                if coord_labels:
                    data.update({
                        'coord_labels': self._state.coord_labels
                    })
            else:  # gifti
                if self._state.fmri_preprocessed:
                    data.update({
                        'left_func_img': self._state.gifti_data_preprocessed['left_func_img'],
                        'right_func_img': self._state.gifti_data_preprocessed['right_func_img'],
                        'is_fmri_preprocessed': True
                    })
                else:
                    data.update({
                        'left_func_img': self._state.gifti_data['left_func_img'],
                        'right_func_img': self._state.gifti_data['right_func_img'],
                        'is_fmri_preprocessed': False
                    })
                
                data.update({
                    'left_input': self._state.left_input,
                    'right_input': self._state.right_input,
                })
        
        # add time series, if passed
        if time_course_data:
            if self._state.ts_enabled or self._state.ts_fmri_plotted:
                ts_out = {}
                for ts_label in self._state.ts_labels:
                    if self._state.ts_preprocessed[ts_label]:
                        ts_data = self._state.ts_data_preprocessed[ts_label]
                    else:
                        ts_data = self._state.ts_data[ts_label]
                    ts_out[ts_label] = ts_data

                data.update({
                    'ts': ts_out,
                })
            else:
                logger.warning(
                    "Time course request received, but no time course data exists"
                )
        
        # add task data, if passed
        if task_data:
            if self._state.task_enabled:
                task_out = {}
                for label in self._state.task_conditions:
                    # get specified convolution
                    convolution = self._state.task_plot_options[label].convolution
                    task_out[label] = self._state.task_data[label][convolution]
                    
                data.update({
                    'task': task_out
                })
            else:
                logger.warning(
                    "Task data request received, but no task data exists"
                )
        return data
    
    @requires_state
    def move_annotation_selection(self, direction: Literal['left', 'right']) -> int:
        """Move annotation selection to the left or right. If at the first or last
        marker, the selection will wrap around to the other end of the list. 
        Return the selected marker.
        
        Arguments:
            direction: The direction to move the annotation selection
        """
        # check if there are any annotation markers
        if not self._state.annotation_markers:
            logger.warning("No annotation markers to move")
            return
        # get index of current annotation selection
        selected_idx = self._state.annotation_markers.index(
            self._state.annotation_selection
        )
        if direction == 'left':
            # circular shift left
            if selected_idx == 0:
                logger.warning("Selected marker is the first one, "
                               "shifting to last")
                self._state.annotation_selection = self._state.annotation_markers[
                    -1
                ]
            else:
                self._state.annotation_selection = self._state.annotation_markers[
                    selected_idx - 1
                ]
        elif direction == 'right':
            # circular shift right
            if selected_idx == len(self._state.annotation_markers) - 1:
                logger.warning("Selected marker is the last one, "
                               "shifting to first")
                self._state.annotation_selection = self._state.annotation_markers[
                    0
                ]
            else:
                self._state.annotation_selection = self._state.annotation_markers[
                    selected_idx + 1
                ]
        logger.info(f"Moved annotation selection to {self._state.annotation_selection}")
        return self._state.annotation_selection

    @requires_state
    def pop_annotation_marker(self) -> Optional[int]:
        """Pop most recent annotation marker from state - remove last added marker
        and update selection to the previous marker. If the last added marker is
        the selected marker, the selection will be updated to the previous marker.

        Returns:
            int: The marker value of the last added annotation marker
        """
        # remove most recent annotation marker
        if self._state.annotation_markers:
            # get index of selected annotation marker
            selected_idx = self._state.annotation_markers.index(
                self._state.annotation_selection
            )
            # if selected marker is the last one, shift selection to previous
            if selected_idx == len(self._state.annotation_markers) - 1:
                logger.warning(
                    "Selected marker is the last one, "
                    "shifting to previous"
                )
                self._state.annotation_selection = self._state.annotation_markers[
                    selected_idx - 1
                ]
            marker = self._state.annotation_markers.pop()
            # check if there are any markers left
            if len(self._state.annotation_markers) == 0:
                logger.info("No annotation markers left, setting annotation_selection to None")
                self._state.annotation_selection = None
                logger.info(f"Popped most recent annotation marker from state, marker = {marker}")
            else:
                logger.info(f"Popped most recent annotation marker from state, marker = {marker}")
            return marker
        else:
            logger.warning("No annotation markers to pop")
            return None
        
    @requires_state
    def pop_fmri_timecourse(self) -> Union[None, str]:
        """Pop most recent fmri timecourse from state and return label
        
        Returns:
            Union[None, str]: Label of the last fmri timecourse, 
                or None if no fmri timecourses exist
        """
        # filter time courses to fmri time courses
        fmri_labels = [
            label for label in self._state.ts_labels 
            if self._state.ts_type[label] == 'fmri'
        ]
        if len(fmri_labels) == 0:
            logger.warning("No fmri timecourses to pop")
            return None
        # remove last fmri timecourse
        last_fmri_label = fmri_labels[-1]
        self._state.ts_data.pop(last_fmri_label)

        # Remove the color from used colors before removing plot options
        if last_fmri_label in self._state.ts_plot_options:
            # remove color from used colors
            self._state.used_colors.remove(
                self._state.ts_plot_options[last_fmri_label].color
            )
        # remove plot options and type
        self._state.ts_plot_options.pop(last_fmri_label)
        self._state.ts_type.pop(last_fmri_label)
        # update labels
        self._state.ts_labels = list(self._state.ts_data.keys())

        # check for any fmri timecourses left
        if len(fmri_labels) == 1:
            self._state.ts_fmri_plotted = False
            logger.info("No fmri timecourses left, setting ts_fmri_plotted to False")
        else:
            logger.info("Popped most recent fmri timecourse from state %s", last_fmri_label)
        
        # update global ts min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()

        return last_fmri_label
    
    @requires_state
    def remove_fmri_timecourses(self) -> Union[None, List[str]]:
        """Remove all fmri time courses from state and return labels
        
        Returns:
            Union[None, List[str]]: Labels of the fmri timecourses, or None if no fmri timecourses exist
        """
        # remove all fmri time courses
        fmri_labels = [
            label for label in self._state.ts_labels 
            if self._state.ts_type[label] == 'fmri'
        ]
        # loop through fmri time courses and remove associated data from state
        for label in fmri_labels:
            # remove fmri time course data
            self._state.ts_data.pop(label)
            # remove fmri time course label
            self._state.ts_labels.remove(label)
            # remove fmri time course type
            self._state.ts_type.pop(label)
            # 'give back' fmri time course color
            self._state.used_colors.remove(self._state.ts_plot_options[label].color)
            # remove fmri time course plot options
            self._state.ts_plot_options.pop(label)

        self._state.ts_fmri_plotted = False
        logger.info("Removed all fmri time courses from state")
        # update global ts min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()

        return fmri_labels
    
    @requires_state
    def reset_fmri_color_options(self) -> None:
        """Reset fMRI color options to original. Original color options are
        stored in the state when the fMRI data (raw or preprocessed) is first
        stored.
        """
        # return color options to original state
        if self._state.fmri_preprocessed:
            color_options = self._state.preprocessed_color_options_original
            self._state.preprocessed_fmri_plot_options.update_from_dict(
                {
                    'color_min': color_options['color_min'],
                    'color_max': color_options['color_max'],
                    'threshold_min': color_options['threshold_min'],
                    'threshold_max': color_options['threshold_max'],
                    'opacity': color_options['opacity']
                }
            )
        else:
            color_options = self._state.color_options_original
            self._state.fmri_plot_options.update_from_dict(
                {
                    'color_min': color_options['color_min'],
                    'color_max': color_options['color_max'],
                    'threshold_min': color_options['threshold_min'],
                    'threshold_max': color_options['threshold_max'],
                    'opacity': color_options['opacity']
                }
            )

        logger.info("Reset color options to original")
    
    @requires_state
    def reset_timecourse_shift(
        self, 
        label: str,
        change_type: Literal['constant', 'scale'],
        source: Literal['timecourse', 'task']
    ) -> None:
        """Reset time course shift (scale or constant).
        
        Arguments:
            label: Label of the time course to reset.
            source: Source of the time course (timecourse or task).
        """
        # get time course data
        if source == 'timecourse':
            if self._state.ts_preprocessed[label]:
                signal = self._state.ts_data_preprocessed[label]
                scaler = self._state.ts_plot_options[label].preprocess_scale
                shifter = self._state.ts_plot_options[label].preprocess_constant
            else:
                signal = self._state.ts_data[label]
                scaler = self._state.ts_plot_options[label].scale
                shifter = self._state.ts_plot_options[label].constant
        else:
            signal = self._state.task_data[label]
            scaler = self._state.task_plot_options[label].scale
            shifter = self._state.task_plot_options[label].constant

        # reset shift
        if source == 'timecourse':
            if change_type == 'constant':
                signal = shifter.reset([signal])[0]
            else:
                signal = scaler.reset([signal])[0]
            # update time course data
            if self._state.ts_preprocessed[label]:
                self._state.ts_data_preprocessed[label] = signal
            else:
                self._state.ts_data[label] = signal
        else:
            if change_type == 'constant':
                signal = shifter.reset([signal['hrf'], signal['block']])
            else:
                signal = scaler.reset([signal['hrf'], signal['block']])
            # update task data
            self._state.task_data[label] = {
                'hrf': signal[0],
                'block': signal[1]
            }
        
        # update ts min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()
        
        logger.info("Reset time course %s %s shift", label, change_type)
    
    @requires_state
    def set_timepoints(self, timepoints: List[float]) -> None:
        """Override the time point array with a new array. Must be 
        equal length to the number of time points in the time courses.
        
        Arguments:
            timepoints: List of time points.
        """
        # check if timepoints are the same length as the time courses
        if len(timepoints) != self.n_timepoints:
            raise ValueError(
                "Timepoints must be equal length to the number of time points of the time courses"
            )
        self._state.timepoints = timepoints
        logger.info("Set timepoints to %s", timepoints)
    
    @requires_state
    def set_tr(self, tr: float) -> None:
        """Override the TR (repitition time) with a new value.
        
        Arguments:
            tr: New TR value.
        """
        # check if TR is valid
        if tr <= 0:
            raise ValueError("TR must be greater than 0")
        # set TR
        self._state.tr = tr
        logger.info("Set TR to %s", tr)

    @requires_state
    def store_fmri_preprocessed(self, data: Dict) -> None:
        """Store preprocessed fMRI data.
        
        Arguments:
            data: Dictionary containing preprocessed fMRI data.
        """
        logger.info("Storing preprocessed fMRI data")
        self._state.fmri_preprocessed = True
        if self._state.file_type == 'nifti':
            # apply mask to preprocessed data (should always be present for preprocessing)
            if self._state.mask_input:
                data['func_img'] = apply_mask_nifti(
                    data['func_img'], 
                    self._state.nifti_data['mask_img']
                )
        if self._state.file_type == 'nifti':
            self._state.nifti_data_preprocessed.update(data)
        else:
            self._state.gifti_data_preprocessed.update(data)
        
        # create preprocessed plot options
        if self._state.file_type == 'nifti':
            metadata = package_nii_metadata(data['func_img'])
        else:
            metadata = package_gii_metadata(
                data['left_func_img'], data['right_func_img']
            )
        
        # create preprocessed plot options, copy some options from raw
        self._state.preprocessed_fmri_plot_options = FmriPlotOptions(
            color_min=metadata['color_min'],
            color_max=metadata['color_max'],
            color_range=metadata['color_range'],
            threshold_range=metadata['threshold_range'],
            precision=metadata['precision'],
            slider_step_size=metadata['slider_step_size'],
            hover_text_on=self._state.fmri_plot_options.hover_text_on,
            color_map=self._state.fmri_plot_options.color_map,
            opacity=self._state.fmri_plot_options.opacity,
            crosshair_on=self._state.fmri_plot_options.crosshair_on,
            direction_marker_on=self._state.fmri_plot_options.direction_marker_on,
            play_movie_speed=self._state.fmri_plot_options.play_movie_speed,
            reverse_colormap=self._state.fmri_plot_options.reverse_colormap,
            colorbar_on=self._state.fmri_plot_options.colorbar_on,
        )
        
        # preserve original color options
        self._state.preprocessed_color_options_original = {
            'color_min': self._state.preprocessed_fmri_plot_options.color_min,
            'color_max': self._state.preprocessed_fmri_plot_options.color_max,
            'color_range': self._state.preprocessed_fmri_plot_options.color_range,
            'threshold_min': self._state.preprocessed_fmri_plot_options.threshold_min,
            'threshold_max': self._state.preprocessed_fmri_plot_options.threshold_max,
            'threshold_range': self._state.preprocessed_fmri_plot_options.threshold_range,
            'opacity': self._state.preprocessed_fmri_plot_options.opacity
        }
        logger.info("Preprocessed fMRI data stored")
    
    @requires_state
    def store_timecourse_preprocessed(self, data: Dict) -> None:
        """Store preprocessed timecourse data.
        
        Arguments:
            data: Dictionary containing preprocessed timecourse data.
        """
        logger.info("Storing preprocessed timecourse data")
        for ts_label in data:
            self._state.ts_preprocessed[ts_label] = True
            self._state.ts_data_preprocessed[ts_label] = data[ts_label]
            self._state.ts_labels_preprocessed.append(ts_label)
            # rename time course in plot options for display
            self._state.ts_plot_options[ts_label].label = \
                f'{ts_label} (preprocessed)'

        # update time course global min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()
        logger.info("Preprocessed timecourse data stored for %s", data.keys())

    @requires_state
    def update_annotation_marker_plot_options(
        self, 
        plot_options: AnnotationMarkerPlotOptionsDict
    ) -> None:
        """Update annotation marker plot options.
        
        Arguments:
            plot_options: Dictionary containing marker plot options.
        """
        self._state.annotation_marker_plot_options.update_from_dict(plot_options)
        logger.info("Updated annotation marker plot options")

    @requires_state
    def update_annotation_selection(self, marker_value: int) -> None:
        """Update annotation selection.
        
        Arguments:
            marker_value: The marker value to update the selection to.
        """
        # check if marker value is in annotation markers
        if marker_value in self._state.annotation_markers:
            # get index of marker value
            marker_idx = self._state.annotation_markers.index(marker_value)
            # update selection
            self._state.annotation_selection = marker_idx
            logger.info("Updated annotation selection")
        else:
            logger.warning("Marker value not found in annotation markers")
    
    @requires_state
    def update_distance_plot_options(self, plot_options: DistancePlotOptionsDict) -> None:
        """Update distance plot options.
        
        Arguments:
            plot_options: Dictionary containing distance plot options.
        """
        if self._state.distance_plot_options:
            self._state.distance_plot_options.update_from_dict(plot_options)
            logger.info("Updated distance plot options")
        else:
            logger.error("No distance plot state exists")
            return

    @requires_state
    def update_location(
        self, 
        click_coords: Dict[Literal['x', 'y'], int] | Dict[Literal['selected_vertex', 'selected_hemi'], int | str], 
        slice_name: Optional[Literal['slice_1', 'slice_2', 'slice_3']] = None
    ) -> None:
        """Update brain location data. For nifti data, the slice indices and click
        coordinates are updated based on the X,Y coordinates of the click. For
        gifti data, the selected vertex and hemisphere are updated.
        
        Arguments:
            click_coords: Dictionary containing coordinate data (x, y) from the click.
            slice_name: slice container where the click occurred.
        """
        if self._state.file_type == 'nifti':
            # update selected slice
            self._state.selected_slice = slice_name
            # update slice indices for nifti data
            self._update_slice_indices(click_coords, slice_name)
            # update click coordinates for nifti data
            if self._state.view_state == 'ortho':
                # update ortho slice coordinates
                self._state.ortho_slice_coords = get_ortho_slice_coords(
                    self._state.ortho_slice_idx
                )
                # update click coordinates for ortho slice
                self._state.ortho_slice_coords[slice_name] = click_coords
            elif self._state.view_state == 'montage':
                # get montage slice directions
                montage_slice_dir = self._state.montage_slice_dir
                # update click coordinates for montage slice direction
                self._state.montage_slice_coords[montage_slice_dir]['slice_1'] = click_coords
                self._state.montage_slice_coords[montage_slice_dir]['slice_2'] = click_coords
                self._state.montage_slice_coords[montage_slice_dir]['slice_3'] = click_coords
        else:
            self._state.selected_vertex = click_coords['selected_vertex']
            self._state.selected_hemi = click_coords['selected_hemi']
        
        logger.info("Updated brain location data")
    
    @requires_state
    def update_fmri_plot_options(
        self,
        display_options: Dict[str, Any]
    ) -> None:
        """Update plot options.
        
        Arguments:
            display_options: Dictionary containing plot options.
        """
        if self._state.fmri_preprocessed:
            self._state.preprocessed_fmri_plot_options.update_from_dict(display_options)
        else:
            self._state.fmri_plot_options.update_from_dict(display_options)
        
        logger.info("Updated plot options")
    
    @requires_state
    def update_montage_slice_dir(self, montage_slice_dir: Literal['x', 'y', 'z']) -> None:
        """Update montage slice direction.
        
        Arguments:
            montage_slice_dir: The direction of the montage slice.
        """
        self._state.montage_slice_dir = montage_slice_dir
        logger.info("Updated montage slice direction")
    
    @requires_state
    def update_montage_slice_idx(self, slice_name: str, slice_idx: int) -> None:
        """Update individual montage slice index from slice index slider changes in 
        montage popover.
        
        Arguments:
            slice_name: The name of the slice.
            slice_idx: The index of the slice.
        """
        montage_slice_dir = self._state.montage_slice_dir
        # update montage slice index
        self._state.montage_slice_idx[montage_slice_dir][slice_name][montage_slice_dir] = slice_idx
        logger.info("Updated montage slice index for slice %s", slice_name)

    @requires_state
    def update_task_design_plot_options(
        self, 
        label: str, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update task design plot options for a specific condition.
        
        Arguments:
            label: The condition of the task design.
            plot_options: Dictionary containing task design plot options.
        """
        # if a color update is made, update the used colors
        if 'color' in plot_options:
            self._state.used_colors.remove(self._state.task_plot_options[label].color)
            self._state.used_colors.add(TimeCourseColor(plot_options['color']))

        # update task design plot options
        self._state.task_plot_options[label].update_from_dict(plot_options)
        logger.info("Updated task design plot options for %s", label)
    
    @requires_state
    def update_timecourse(
        self, 
        timecourse: List[float], 
        label: str
    ) -> None:
        """Update time course data with new timecourse and label.
        
        Arguments:
            timecourse: List of timecourse data.
            label: The label of the time course.
        """
        if self._state.ts_data is None:
            raise ValueError(
                "Please initialize time course data first. "
                "Use add_timeseries() to initialize."
            )
        self._state.ts_data[label] = timecourse
        self._state.ts_labels = list(self._state.ts_data.keys())
        # the only ts types passed after initialization are fmri time courses
        self._state.ts_type.update({label: 'fmri'})
        self._state.ts_fmri_plotted = True
        logger.info("Updated time course data with new fmri time course")

        # Create plot options if not already present
        if label not in self._state.ts_plot_options:
            plot_options = TimeCoursePlotOptions.with_next_color(
                self._state.used_colors,
                label=label
            )
            self._state.used_colors.add(plot_options.color)
            self._state.ts_plot_options[label] = plot_options
        
        # update global ts min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()

    @requires_state
    def update_timecourse_global_plot_options(
        self, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update time course global plot options for all time courses.
        
        Arguments:
            plot_options: Dictionary containing time course global plot options.
        """
        self._state.time_course_global_plot_options.update_from_dict(plot_options)
        logger.info("Updated time course global plot options")

    @requires_state
    def update_timecourse_plot_options(
        self, 
        label: str, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update time course plot options for a specific time course.
        
        Arguments:
            label: The label of the time course.
            plot_options: Dictionary containing time course plot options.
        """
        # if a color update is made, update the used colors
        if 'color' in plot_options:
            self._state.used_colors.remove(self._state.ts_plot_options[label].color)
            self._state.used_colors.add(TimeCourseColor(plot_options['color']))

        # update time course plot options
        self._state.ts_plot_options[label].update_from_dict(plot_options)
        
        logger.info("Updated time course plot options for %s", label)
    
    @requires_state
    def update_timecourse_shift(
        self, 
        label: str,
        source: Literal['task', 'timecourse'],
        change_type: Literal['constant', 'scale'],
        change_direction: Literal['increase', 'decrease']
    ) -> None:
        """Scale and/or add a constant shift to time course data.
        
        Arguments:
            label: The label of the time course.
            source: The source of the time course ['timecourse', 'task'].
            change_type: The type of change ['constant', 'scale'].
            change_direction: The direction of the change ['increase', 'decrease'].
        """
        
        # get time course data
        if source == 'timecourse':
            if self._state.ts_preprocessed[label]:
                ts_data = self._state.ts_data_preprocessed[label]
                scaler = self._state.ts_plot_options[label].preprocess_scale
                shifter = self._state.ts_plot_options[label].preprocess_constant
            else:
                ts_data = self._state.ts_data[label]
                scaler = self._state.ts_plot_options[label].scale
                shifter = self._state.ts_plot_options[label].constant
        else:
            ts_data = self._state.task_data[label]
            scaler = self._state.task_plot_options[label].scale
            shifter = self._state.task_plot_options[label].constant
        
        # get constant and scale unit
        constant_unit = self._state.time_course_global_plot_options.shift_unit
        scale_unit = self._state.time_course_global_plot_options.scale_unit

        # apply shift to time course data
        ts_data = self._apply_ts_shift(
            ts_data,
            source,
            change_type,
            change_direction,
            constant_unit if change_type == 'constant' else scale_unit,
            scaler,
            shifter
        )
        
        # Update data
        if source == 'timecourse':
            if self._state.ts_preprocessed[label]:
                self._state.ts_data_preprocessed[label] = ts_data
            else:
                self._state.ts_data[label] = ts_data
        else:
            self._state.task_data[label] = ts_data
                
        # update global ts min and max
        self._update_ts_minmax()
        # update shift unit
        self._update_shift_unit()

        logger.info("Updated time course shift for %s", label)

    
    @requires_state
    def update_time_marker_plot_options(
        self, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update time marker plot options.
        
        Arguments:
            plot_options: Dictionary containing time marker plot options.
        """
        self._state.time_marker_plot_options.update_from_dict(plot_options)
        logger.info("Updated time marker plot options")

    @requires_state
    def update_timepoint(self, timepoint: int) -> None:
        """Update timepoint data.
        
        Arguments:
            timepoint: The index of the timepoint.
        """
        # check if timepoint is within range
        if timepoint < 0 or timepoint >= len(self._state.timepoints):
            logger.error("Timepoint out of range")
            return
        
        self._state.timepoint = timepoint
        logger.info("Updated timepoint data")
    
    @requires_state
    def update_view_state(self, view_state: Literal['ortho', 'montage']) -> None:
        """Update view state to ortho or montage.
        
        Arguments:
            view_state: The state of the view ['ortho', 'montage'].
        """
        self._state.view_state = view_state
        logger.info("Updated view state")

    def _apply_ts_shift(
        self, 
        ts_data: Union[List[float], Dict[str, float]], 
        source: Literal['timecourse', 'task'],
        shift_type: Literal['constant', 'scale'], 
        shift_direction: Literal['increase', 'decrease'], 
        shift_unit: float,
        scaler: Optional[SignalScaler] = None,
        shifter: Optional[SignalShifter] = None
    ) -> Union[List[float], Dict[str, float]]:
        """
        Apply shift (scale or constant) to time course data and 
        return new time course data. If task data, apply to both 
        the block and hrf data.
        
        Arguments:
            ts_data: List of time course data or dictionary of time course data.
            source: The source of the time course ['timecourse', 'task'].
            shift_type: The type of shift ['constant', 'scale'].
            shift_direction: The direction of the shift ['increase', 'decrease'].
            shift_unit: The unit of the shift.
        
        Returns:
            Tuple containing new time course data and shift change.
        """
        # check that shift_type and appropriate scaler/shifter are provided
        if shift_type == 'scale':
            if not scaler:
                raise ValueError("Scale shift requires a scaler")
        elif shift_type == 'constant':
            if not shifter:
                raise ValueError("Constant shift requires a shifter")

        # Convert shift unit to negative if decreasing
        if shift_direction == 'decrease':
            shift_unit = -shift_unit

        # Apply shift to data
        if source == 'timecourse':
            if shift_type == 'scale':
                ts_data = scaler.scale([ts_data], scale_unit=shift_unit)[0]
            elif shift_type == 'constant':
                ts_data = shifter.shift([ts_data], shift_amount=shift_unit)[0]
        else:
            if shift_type == 'scale':
                ts_data_conv = scaler.scale(
                    [ts_data['hrf'], ts_data['block']], 
                    scale_unit=shift_unit
                )
            elif shift_type == 'constant':
                ts_data_conv = shifter.shift(
                    [ts_data['hrf'], ts_data['block']], 
                    shift_amount=shift_unit
                )
            ts_data = {
                'hrf': ts_data_conv[0],
                'block': ts_data_conv[1]
            }

        return ts_data

    def _get_slice_direction_label_coords(
        self, 
        slice_dir: Literal['x', 'y', 'z']
    ) -> Dict[str, Dict[str, int]]:
        """Get direction labels for ortho or montage data"""
        # sagittal slice - anterior and posterior
        if slice_dir == 'x':
            return {
                'P': {
                    'x': 1,
                    'y': self._state.slice_len['z'] // 2,
                },
                'A': {
                    'x': self._state.slice_len['y'] - 2,
                    'y': self._state.slice_len['z'] // 2,
                }
            }
        # coronal slice - left and right
        elif slice_dir == 'y':
            return {
                'L': {
                    'x': 1,
                    'y': self._state.slice_len['z'] // 2,
                },
                'R': {
                    'x': self._state.slice_len['x'] - 2,
                    'y': self._state.slice_len['z'] // 2,
                }
            }
        # axial slice - posterior and anterior, left and right
        elif slice_dir == 'z':
            return {
                'L': {
                    'x': 1,
                    'y': self._state.slice_len['y'] // 2,
                },
                'R': {
                    'x': self._state.slice_len['x'] - 2,
                    'y': self._state.slice_len['y'] // 2,
                },
                'P': {
                    'x': self._state.slice_len['x'] // 2,
                    'y': 1,
                },
                'A': {
                    'x': self._state.slice_len['x'] // 2,
                    'y': self._state.slice_len['y'] - 2,
                }
            }
        else:
            raise ValueError("Invalid slice direction")

    def _update_slice_indices(
        self, 
        click_coords: Dict[str, Literal['x', 'y']], 
        slice_name: Literal['slice_1', 'slice_2', 'slice_3']
    ) -> None:
        """Update slice indices for nifti data from click coordinates in the ortho
        or montage view
        
        Arguments:
            click_coords: Coordinate (x, y) where the click occurred.
            slice_name: Slice where the click occurred.
        """
        if self._state.view_state == 'ortho':
            # Convert click coordinates to slice indices based on which slice was clicked
            # slice_1 is axial, slice_2 is coronal, slice_3 is sagittal
            if slice_name == 'slice_1':
                self._state.ortho_slice_idx['x'] = self._state.ortho_slice_idx['x']
                self._state.ortho_slice_idx['y'] = click_coords['x']
                self._state.ortho_slice_idx['z'] = click_coords['y']
            elif slice_name == 'slice_2':
                self._state.ortho_slice_idx['x'] = click_coords['x']
                self._state.ortho_slice_idx['y'] = self._state.ortho_slice_idx['y']
                self._state.ortho_slice_idx['z'] = click_coords['y']
            elif slice_name == 'slice_3':
                self._state.ortho_slice_idx['x'] = click_coords['x']
                self._state.ortho_slice_idx['y'] = click_coords['y']
                self._state.ortho_slice_idx['z'] = self._state.ortho_slice_idx['z']

        elif self._state.view_state == 'montage':
            montage_slice_idx = self._state.montage_slice_idx
            montage_slice_dir = self._state.montage_slice_dir
            for montage_slice in montage_slice_idx[montage_slice_dir]:
                if montage_slice_dir == 'x':
                    montage_slice_idx[montage_slice_dir][montage_slice]['y'] = click_coords['x']
                    montage_slice_idx[montage_slice_dir][montage_slice]['z'] = click_coords['y']
                elif montage_slice_dir == 'y':
                    montage_slice_idx[montage_slice_dir][montage_slice]['x'] = click_coords['x']
                    montage_slice_idx[montage_slice_dir][montage_slice]['z'] = click_coords['y']
                elif montage_slice_dir == 'z':
                    montage_slice_idx[montage_slice_dir][montage_slice]['x'] = click_coords['x']
                    montage_slice_idx[montage_slice_dir][montage_slice]['y'] = click_coords['y']
            
    def _update_ts_minmax(self):
        """Update time series min and max values"""
        if self._state.ts_enabled or self._state.ts_fmri_plotted:
            ts_data = {}
            for ts_label in self._state.ts_labels:
                if self._state.ts_preprocessed[ts_label]:
                    ts_data[ts_label] = self._state.ts_data_preprocessed[ts_label]
                else:
                    ts_data[ts_label] = self._state.ts_data[ts_label]
        else:
            ts_data = None

        if self._state.task_enabled:
            task_data = {}
            for condition in self._state.task_data:
                task_data[f'{condition}_hrf'] = self._state.task_data[condition]['hrf']
                task_data[f'{condition}_block'] = self._state.task_data[condition]['block']
        else:
            task_data = None

        ts_min, ts_max = get_ts_minmax(
            ts_data=ts_data,
            task_data=task_data,
            default_min=self._state.time_course_global_plot_options.default_global_min,
            default_max=self._state.time_course_global_plot_options.default_global_max
        )
        self._state.time_course_global_plot_options.global_min = ts_min
        self._state.time_course_global_plot_options.global_max = ts_max
        logger.info("Updated time series min and max values")
    
    def _update_shift_unit(self):
        """
        Update constant shift and scale unit for time course data to be responsive
        to the range of the data. This should be applied after global min and max are
        updated.
        """
        # get global min and max
        ts_min = self._state.time_course_global_plot_options.global_min
        ts_max = self._state.time_course_global_plot_options.global_max

        # update shift unit
        update_ratio = self._state.time_course_global_plot_options.shift_update_ratio
        shift_unit = (ts_max - ts_min) / update_ratio
        self._state.time_course_global_plot_options.shift_unit = shift_unit
        logger.info("Updated shift unit to %s", shift_unit)

        # update scale unit based on logarithmic scaling
        scale_range = abs(ts_max - ts_min)
        update_factor = self._state.time_course_global_plot_options.scale_update_granularity
        if scale_range > 0:
            # Use logarithmic scaling for better handling of different ranges
            scale_unit = (10 ** (np.floor(np.log10(scale_range)) - 2)) * update_factor
            
            # Ensure scale unit is between reasonable bounds
            MIN_SCALE = 0.001  # 0.1% minimum change
            MAX_SCALE = 0.9    # 90% maximum change
            scale_unit = np.clip(scale_unit, MIN_SCALE, MAX_SCALE)
        else:
            scale_unit = 0.01  # Default when range is 0

        self._state.time_course_global_plot_options.scale_unit = scale_unit
        logger.info("Updated scale unit to %s", scale_unit)