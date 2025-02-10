"""Backend Data Management with DataManager singleton pattern.

This module provides a centralized data management system for the FIND viewer,
handling both NIFTI and GIFTI visualization states. It implements a singleton
pattern to ensure consistent state across the application.

Classes:
    DataManager: Singleton manager for visualization state
"""

import logging

from typing import Dict, Optional, List, Literal, ClassVar, Any

import numpy as np
import nibabel as nib

from findviz.logger_config import setup_logger
from findviz.viz.viewer.state import (
    NiftiVisualizationState, 
    GiftiVisualizationState,
    FmriPlotOptions,
    TimeCoursePlotOptions,
    TaskDesignPlotOptions,
    DistancePlotOptions
)
from findviz.viz.viewer.types import (
    ViewerDataNiftiDict, ViewerDataGiftiDict, 
    ViewerMetadataNiftiDict, ViewerMetadataGiftiDict,
    FmriPlotOptionsDict, TimeCourseGlobalPlotOptionsDict,
    TimeCoursePlotOptionsDict, TimeMarkerPlotOptionsDict, 
    TaskDesignPlotOptionsDict, DistancePlotOptionsDict,
    SliceIndexDict, CrosshairCoordsDict, DirectionLabelCoordsDict
)
from findviz.viz.viewer.utils import (
    apply_mask_nifti, get_coord_labels,
    package_nii_metadata, package_gii_metadata,
    package_distance_metadata, requires_state
)

logger = setup_logger(__name__)

class DataManager:
    """Singleton manager for visualization state.
    
    This class implements the singleton pattern to maintain a single source of truth
    for the visualization state across the entire application. It handles both NIFTI
    and GIFTI data types and their associated metadata.
    
    Attributes:
        _instance (ClassVar[Optional[DataManager]]): Singleton instance
        _state (Optional[VisualizationState]): Current visualization state
    
    Methods:
        add_annotation_marker(): Add annotation marker
        add_timeseries(): Add timeseries data to state
        add_task_design(): Add task design data to state
        change_timecourse_scale(): Change the scale of the time course(s)
        clear_annotation_markers(): Clear annotation markers
        clear_distance_plot_state(): Clear distance plot state
        clear_fmri_preprocessed(): Clear preprocessed fMRI data
        clear_timecourse_preprocessed(): Clear preprocessed timecourse data
        clear_state(): Clear state
        create_distance_plot_state(): Create distance plot state
        create_nifti_state(): Initialize state for NIFTI data
        create_gifti_state(): Initialize state for GIFTI data
        get_click_coords(): Get click coordinates
        get_crosshair_coords(): Get coordinates for crosshair shape
        get_distance_plot_options(): Get distance plot options
        get_fmri_plot_options(): Get plot options
        get_slice_idx(): Get slice indices
        get_timecourse_global_plot_options(): Get time course global plot options
        get_timecourse_plot_options(): Get time course plot options for a given label
        get_task_design_plot_options(): Get task design plot options for a given label
        get_viewer_metadata(): Get metadata for viewer
        get_viewer_data(): Get formatted data for viewer
        move_annotation_selection(): Move annotation selection
        pop_annotation_marker(): Pop most recent annotation marker from state
        pop_timecourse(): Pop most recent timecourse from state
        reset_fmri_color_options(): Reset fMRI color options to original
        store_fmri_preprocessed(): Store preprocessed fMRI data
        store_timecourse_preprocessed(): Store preprocessed timecourse data
        update_location(): Update brain location data
        update_distance_plot_options(): Update distance plot options
        update_fmri_plot_options(): Update plot options
        update_montage_slice_dir(): Update montage slice direction
        update_montage_slice_idx(): Update montage slice indices
        update_timecourse_global_plot_options(): Update time course global plot options
        update_task_design_plot_options(): Update task design plot options
        update_timecourse_plot_options(): Update time course plot options for a given label
        update_time_marker_plot_options(): Update time marker plot options
        update_timepoint(): Update timepoint data
        update_timecourse(): Update time course data with new timecourse and label
        update_view_state(): Update view state
    """
    _instance: ClassVar[Optional['DataManager']] = None
    _state: Optional[NiftiVisualizationState | GiftiVisualizationState]
    
    def __new__(cls) -> 'DataManager':
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize instance attributes 
            cls._instance._state = None

        return cls._instance

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
    def annotation_selection(self) -> int:
        return self._state.annotation_selection
    
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
    def montage_slice_dir(self) -> Optional[Literal['x', 'y', 'z']]:
        if self._state.file_type == 'nifti':
            return self._state.montage_slice_dir
        else:
            logger.error("No montage slice dir exist for GIFTI data")
            return None

    @requires_state
    @property
    def montage_slice_coords(self) -> Optional[SliceIndexDict]:
        if self._state.file_type == 'nifti':
            montage_slice_dir = self._state.montage_slice_dir
            return self._state.montage_slice_coords[montage_slice_dir]
        else:
            logger.error("No montage slice coords exist for GIFTI data")
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
    def state(self) -> NiftiVisualizationState | GiftiVisualizationState:
        return self._state
    
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
    def ts_preprocessed(self) -> bool:
        return self._state.ts_preprocessed

    @requires_state
    @property
    def ts_labels(self) -> List[str]:
        return self._state.ts_labels

    @requires_state
    @property
    def task_conditions(self) -> List[str]:
        return self._state.task_conditions
    
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
    def view_state(self) -> Literal['ortho', 'montage']: 
        return self._state.view_state


    @requires_state
    def add_annotation_markers(self, markers: int | List[int]) -> None:
        """Add annotation markers"""
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
        
    @requires_state
    def add_timeseries(
        self, 
        timeseries: Optional[Dict[str, np.ndarray]] = None
    ) -> None:
        """Add time series data if not already present. 
        
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
            )
            self._state.used_colors.add(plot_options.color)
            self._state.ts_plot_options[label] = plot_options

    
    @requires_state
    def add_task_design(
        self, 
        task_data: Dict[str, np.ndarray], 
        tr: float, 
        slicetime_ref: float
    ) -> None:
        """Add task design data
        
        Arguments:
            task_data: The task design data to add.
            tr: The repetition time.
            slicetime_ref: The slicetime reference.
        """        
        # add conditions
        self._state.task_conditions = list(task_data.keys())
        self._state.task_data = task_data
        self._state.task_enabled = True
        # add metadata
        self._state.tr = tr
        self._state.slicetime_ref = slicetime_ref

        # Create plot options for each task condition with unique colors
        for label in self._state.task_conditions:
            plot_options = TaskDesignPlotOptions.with_next_color(
                self._state.used_colors,
            )
            self._state.used_colors.add(plot_options.color)
            self._state.task_plot_options[label] = plot_options
    
    @requires_state
    def change_timecourse_scale(
        self,
        label: str,
        scale_change: Literal['increase', 'decrease'],
        scale_change_unit: float = 0.1
    ) -> None:
        """Change the scale of the time course(s)
        
        Arguments:
            label: The label of the time course or task
            ts_type: The type of time course or task
            scale_change: The direction of the scale change
            scale_change_unit: The unit of scale change
        """
        if scale_change == 'increase':
            scale_change_unit = 1 + scale_change_unit
        elif scale_change == 'decrease':
            scale_change_unit = 1 - scale_change_unit
        if self._state.timecourse_source[label] == 'timecourse':
            scale_orig = self._state.ts_plot_options[label].scale
            scale_new = scale_orig * scale_change_unit
            self._state.ts_plot_options[label].scale = scale_new
        else:
            scale_orig = self._state.task_plot_options[label].scale
            scale_new = scale_orig * scale_change_unit
            self._state.task_plot_options[label].scale = scale_new

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
        if not self._state.distance_data:
            logger.error("No distance data exists")
            return
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
    def clear_timecourse_preprocessed(self) -> None:
        """Clear preprocessed timecourse data."""
        logger.info("Clearing preprocessed timecourse data")
        self._state.ts_preprocessed = False
        self._state.ts_data_preprocessed = None

    @requires_state
    def clear_state(self) -> None:
        """Clear state."""
        logger.info("Clearing data managerstate")
        self._state = None
    
    @requires_state
    def create_distance_plot_state(
        self,
        distance_data: np.ndarray,
    ) -> None:
        """Create distance plot state"""
        logger.info("Creating distance plot state")
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
        """Create visualization state for NIFTI data"""        
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
            coord_labels=get_coord_labels(func_img)
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
        right_mesh: Optional[nib.GiftiImage] = None
    ) -> None:
        """Create visualization state for GIFTI data"""
        metadata = package_gii_metadata(left_func_img, right_func_img)
        
        self._state = GiftiVisualizationState(
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
            )
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
        
        # Store inputs
        if left_func_img:
            self._state.left_input = True
        if right_func_img:
            self._state.right_input = True
            
        # Store mesh data
        # assumes first position is coordinates, and second is faces
        if left_mesh:
            self._state.vertices_left = left_mesh.darrays[0].data.tolist()
            self._state.faces_left = left_mesh.darrays[1].data.tolist()
        if right_mesh:
            self._state.vertices_right = right_mesh.darrays[0].data.tolist()
            self._state.faces_right = right_mesh.darrays[1].data.tolist()
    
    @requires_state
    def get_click_coords(self) -> Dict[str, Any]:
        """Get click coordinates for brain data"""
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
        """Get coordinates for crosshair shape
          for nifti plot from slice length and coordinates"""
        if self._state.file_type == 'nifti':
            if self._state.view_state == 'ortho':
                crosshair_data = {
                    'slice1': {
                        'len_x': self._state.slice_len['y'],
                        'len_y': self._state.slice_len['z'],
                        'x': self._state.ortho_slice_coords['slice1']['x'],
                        'y': self._state.ortho_slice_coords['slice1']['y']
                    },
                    'slice2': {
                        'len_x': self._state.slice_len['x'],
                        'len_y': self._state.slice_len['z'],
                        'x': self._state.ortho_slice_coords['slice2']['x'],
                        'y': self._state.ortho_slice_coords['slice2']['y']
                    },
                    'slice3': {
                        'len_x': self._state.slice_len['x'],
                        'len_y': self._state.slice_len['y'],
                        'x': self._state.ortho_slice_coords['slice3']['x'],
                        'y': self._state.ortho_slice_coords['slice3']['y']
                    }
                }
            else:
                slice_dir = self._state.montage_slice_dir
                crosshair_data = {
                    'slice1': {
                        'len_x': self._state.slice_len['y'],
                        'len_y': self._state.slice_len['z'],
                        'x': self._state.montage_slice_coords[slice_dir]['slice1']['x'],
                        'y': self._state.montage_slice_coords[slice_dir]['slice1']['y']
                    },
                    'slice2': {
                        'len_x': self._state.slice_len['x'],
                        'len_y': self._state.slice_len['z'],
                        'x': self._state.montage_slice_coords[slice_dir]['slice2']['x'],
                        'y': self._state.montage_slice_coords[slice_dir]['slice2']['y']
                    },
                    'slice3': {
                        'len_x': self._state.slice_len['x'],
                        'len_y': self._state.slice_len['y'],
                        'x': self._state.montage_slice_coords[slice_dir]['slice3']['x'],
                        'y': self._state.montage_slice_coords[slice_dir]['slice3']['y']
                    }
                }
            
            return crosshair_data
        
        else:
            logger.error("Crosshair plot not supported for GIFTI data")
            return {}
    
    @requires_state
    def get_direction_label_coords(self) -> DirectionLabelCoordsDict:
        """Get coordinates for direction labels to plot on NIFTI data"""
        if self._state.file_type == 'nifti':
            if self._state.view_state == 'ortho':
                return {
                    'slice1': self._get_slice_direction_label_coords('x'),
                    'slice2': self._get_slice_direction_label_coords('y'),
                    'slice3': self._get_slice_direction_label_coords('z')
                }
            else:
                slice_dir = self._state.montage_slice_dir
                return {
                    'slice1': self._get_slice_direction_label_coords(slice_dir),
                    'slice2': self._get_slice_direction_label_coords(slice_dir),
                    'slice3': self._get_slice_direction_label_coords(slice_dir)
                }
        else:
            logger.error("Direction labels not supported for GIFTI data")
            return {}
    
    @requires_state
    def get_distance_plot_options(self) -> DistancePlotOptionsDict:
        """Get distance plot options"""
        if self._state.distance_plot_options:
            return self._state.distance_plot_options.to_dict()
        else:
            logger.error("No distance plot state exists")
            return {}
    
    @requires_state
    def get_fmri_plot_options(self) -> FmriPlotOptionsDict:
        """Get plot options"""
        if self._state.fmri_preprocessed:
            data = self._state.preprocessed_fmri_plot_options.to_dict()
        else:
            data = self._state.fmri_plot_options.to_dict()
        
        return data
    
    @requires_state
    def get_slice_idx(self) -> SliceIndexDict:
        """Get slice indices"""
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
        """Get task design plot options for a given label"""
        if label:
            return self._state.task_plot_options[label].to_dict()
        else:
            return {
                label: plot_options.to_dict()
                for label, plot_options in self._state.task_plot_options.items()
            }
    
    @requires_state
    def get_timecourse_global_plot_options(self) -> TimeCourseGlobalPlotOptionsDict:
        """Get time course global plot options"""
        return self._state.time_course_global_plot_options.to_dict()
    
    @requires_state
    def get_timecourse_plot_options(
        self, 
        label: Optional[str] = None
    ) -> TimeCoursePlotOptionsDict | Dict[str, TimeCoursePlotOptionsDict]:
        """Get time course plot options for a given label"""
        if label:
            return self._state.ts_plot_options[label].to_dict()
        else:
            return {
                label: plot_options.to_dict()
                for label, plot_options in self._state.ts_plot_options.items()
            }
    
    @requires_state
    def get_time_marker_plot_options(self) -> TimeMarkerPlotOptionsDict:
        """Get time marker plot options"""
        return self._state.time_marker_plot_options.to_dict()
    
    @requires_state
    def get_viewer_metadata(self) -> ViewerMetadataNiftiDict | ViewerMetadataGiftiDict:
        """Get metadata for viewer"""        
        if self._state.file_type == 'nifti':
            data = ViewerMetadataNiftiDict(
                file_type=self._state.file_type,
                timepoint=self._state.timepoint,
                anat_input=self._state.anat_input,
                mask_input=self._state.mask_input,
                tr=self._state.tr,
                slicetime_ref=self._state.slicetime_ref,
                timepoints=self._state.timepoints,
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
            if self._state.file_type == 'nifti':
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
                    'mask_img': self._state.nifti_data['mask_img'],
                    'func_img': self._state.nifti_data['func_img'],
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
            if self._state.ts_enabled:
                if self._state.ts_preprocessed:
                    data.update({
                        'ts': self._state.ts_data_preprocessed,
                        'is_ts_preprocessed': True
                    })
                else:
                    data.update({
                        'ts': self._state.ts_data,
                        'ts_labels': self._state.ts_labels,
                        'is_ts_preprocessed': False
                    })
            else:
                logger.warning(
                    "Time course request received, but no "
                    "time course data exists"
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
                    "Task data request received, but no "
                    "task data exists"
                )
        return data
    
    @requires_state
    def move_annotation_selection(self, direction: Literal['left', 'right']) -> None:
        """Move annotation selection"""
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

    @requires_state
    def pop_annotation_marker(self) -> None:
        """Pop most recent annotation marker from state"""
        # remove last annotation marker
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

            self._state.annotation_markers.pop()
            logger.info("Popped most recent annotation marker from state")
        else:
            logger.warning("No annotation markers to pop")

    @requires_state
    def pop_fmri_timecourse(self) -> None:
        """Pop most recent fmri timecourse from state"""
        # filter time courses to fmri time courses
        fmri_labels = [
            label for label in self._state.ts_labels 
            if self._state.ts_type[label] == 'fmri'
        ]
        if len(fmri_labels) == 0:
            logger.warning("No fmri timecourses to pop")
            return
        # remove last fmri timecourse
        last_fmri_label = fmri_labels[-1]
        self._state.ts_data.pop(last_fmri_label)
        # Remove the color from used colors before removing plot options
        if last_fmri_label in self._state.ts_plot_options:
            self._state.used_colors.remove(
                self._state.ts_plot_options[last_fmri_label].color
            )
        # remove plot options and type
        self._state.ts_plot_options.pop(last_fmri_label)
        self._state.ts_type.pop(last_fmri_label)
        # update labels
        self._state.ts_labels = list(self._state.ts_data.keys())
        logger.info("Popped most recent fmri timecourse from state")
    
    @requires_state
    def remove_fmri_timecourses(self) -> None:
        """Remove all fmri time courses from state"""
        # remove all fmri time courses
        for label in self._state.ts_labels:
            if self._state.ts_type[label] == 'fmri':
                self._state.ts_data.pop(label)
                self._state.ts_labels.remove(label)
                self._state.ts_type.pop(label)
                self._state.ts_plot_options.pop(label)
                self._state.used_colors.remove(self._state.ts_plot_options[label].color)
        logger.info("Removed all fmri time courses from state")
    
    @requires_state
    def reset_fmri_color_options(self) -> None:
        """Reset fMRI color options to original"""
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
    def store_fmri_preprocessed(self, data: Dict) -> None:
        """Store preprocessed fMRI data."""
        logger.info("Storing preprocessed fMRI data")
        self._state.fmri_preprocessed = True
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
            threshold_min=metadata['threshold_min'],
            threshold_max=metadata['threshold_max'],
            threshold_range=metadata['threshold_range'],
            precision=metadata['precision'],
            slider_steps=metadata['slider_step_size'],
            hover_text_on=self._state.fmri_plot_options.hover_text_on,
            color_map=self._state.fmri_plot_options.color_map,
            opacity=self._state.fmri_plot_options.opacity,
            crosshair_on=self._state.fmri_plot_options.crosshair_on,
            direction_marker_on=self._state.fmri_plot_options.direction_marker_on,
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
    
    @requires_state
    def store_timecourse_preprocessed(self, data: Dict) -> None:
        """Store preprocessed timecourse data."""
        logger.info("Storing preprocessed timecourse data")
        self._state.ts_preprocessed = True
        self._state.ts_data_preprocessed = data

    @requires_state
    def update_annotation_selection(self, marker_value: int) -> None:
        """Update annotation selection"""
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
        """Update distance plot options"""
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
        slice_name: Optional[Literal['slice1', 'slice2', 'slice3']] = None
    ) -> None:
        """Update brain location data
        
        Arguments:
            click_coords: Dictionary containing coordinate data (x, y) from the click.
            slice_name: slice container where the click occurred.
        """
        if self._state.file_type == 'nifti':
            # update slice indices for nifti data
            self._update_slice_indices(click_coords, slice_name)
            # update click coordinates for nifti data
            if self._state.view_state == 'ortho':
                self._state.ortho_slice_coords[slice_name] = click_coords
            elif self._state.view_state == 'montage':
                # get montage slice direction
                montage_slice_dir = self._state.montage_slice_dir
                # update click coordinates for montage slice direction
                self._state.montage_slice_coords[montage_slice_dir][slice_name] = click_coords
        else:
            self._state.selected_vertex = click_coords['selected_vertex']
            self._state.selected_hemi = click_coords['selected_hemi']
        
        logger.info("Updated brain location data")
    
    @requires_state
    def update_fmri_plot_options(
        self,
        display_options: Dict[str, Any]
    ) -> None:
        """Update plot options"""
        if self._state.fmri_preprocessed:
            self._state.preprocessed_fmri_plot_options.update_from_dict(display_options)
        else:
            self._state.fmri_plot_options.update_from_dict(display_options)
        
        logger.info("Updated plot options")
    
    @requires_state
    def update_montage_slice_dir(self, montage_slice_dir: Literal['x', 'y', 'z']) -> None:
        """Update montage slice direction"""
        self._state.montage_slice_dir = montage_slice_dir
        logger.info("Updated montage slice direction")
    
    @requires_state
    def update_montage_slice_idx(self, slice_name: str, slice_idx: int) -> None:
        """Update individual montage slice index from slider changes"""
        montage_slice_dir = self._state.montage_slice_dir
        self._state.montage_slice_idx[montage_slice_dir][slice_name][montage_slice_dir] = slice_idx
        logger.info("Updated montage slice index for slice %s", slice_name)

    @requires_state
    def update_task_design_plot_options(
        self, 
        label: str, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update task design plot options"""
        self._state.task_plot_options[label].update_from_dict(plot_options)
        logger.info("Updated task design plot options")

    @requires_state
    def update_timecourse_global_plot_options(
        self, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update time course global plot options"""
        self._state.time_course_global_plot_options.update_from_dict(plot_options)
        logger.info("Updated time course global plot options")

    @requires_state
    def update_timecourse_plot_options(
        self, 
        label: str, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update time course plot options"""
        self._state.ts_plot_options[label].update_from_dict(plot_options)
        logger.info("Updated time course plot options")
    
    @requires_state
    def update_time_marker_plot_options(
        self, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update time marker plot options"""
        self._state.time_marker_plot_options.update_from_dict(plot_options)
        logger.info("Updated time marker plot options")

    @requires_state
    def update_timepoint(self, timepoint: int) -> None:
        """Update timepoint data"""
        # check if timepoint is within range
        if timepoint < 0 or timepoint >= self._state.timepoints:
            logger.error("Timepoint out of range")
            return
        
        self._state.timepoint = timepoint
        logger.info("Updated timepoint data")
    
    @requires_state
    def update_timecourse(
        self, 
        timecourse: List[float], 
        label: str
    ) -> None:
        """Update time course data with new timecourse and label"""
        if self._state.ts_data is None:
            raise ValueError(
                "Please initialize time course data first. "
                "Use add_timeseries() to initialize."
            )
        self._state.ts_data[label] = timecourse
        self._state.ts_labels = list(self._state.ts_data.keys())
        # the only ts types passed after initialization are fmri time courses
        self._state.ts_type.update({label: 'fmri'})
        logger.info("Updated time course data with new fmri time course")

        # Create plot options if not already present
        if label not in self._state.ts_plot_options:
            plot_options = TimeCoursePlotOptions.with_next_color(
                self._state.used_colors
            )
            self._state.used_colors.add(plot_options.color)
            self._state.ts_plot_options[label] = plot_options
    
    @requires_state
    def update_view_state(self, view_state: Literal['ortho', 'montage']) -> None:
        """Update view state"""
        self._state.view_state = view_state
        logger.info("Updated view state")
    

    def _get_direction_labels_montage(self) -> None:
        """Get direction labels for montage view"""
        return {
            'x': {
                'L': {
                    'x': 1,
                    'y': self._state.slice_len['z'] // 2,
                },
            }
        }

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
        slice_name: Literal['slice1', 'slice2', 'slice3']
    ) -> None:
        """Update slice indices for nifti data from click coordinates in the ortho
        or montage view
        
        Arguments:
            click_coords: Coordinate (x, y) where the click occurred.
            slice_name: Slice where the click occurred.
        """
        if self._state.fmri_plot_options.view_state == 'ortho':
            # Convert click coordinates to slice indices based on which slice was clicked
            # slice1 is axial, slice2 is coronal, slice3 is sagittal
            if slice_name == 'slice1':
                self._state.ortho_slice_idx['x'] = click_coords['x']
                self._state.ortho_slice_idx['y'] = click_coords['y']
                self._state.ortho_slice_idx['z'] = self._state.ortho_slice_idx['z']
            elif slice_name == 'slice2':
                self._state.ortho_slice_idx['x'] = click_coords['x']
                self._state.ortho_slice_idx['y'] = self._state.ortho_slice_idx['y']
                self._state.ortho_slice_idx['z'] = click_coords['y']
            elif slice_name == 'slice3':
                self._state.ortho_slice_idx['x'] = click_coords['x']
                self._state.ortho_slice_idx['y'] = click_coords['y']
                self._state.ortho_slice_idx['z'] = self._state.ortho_slice_idx['z']

        elif self._state.fmri_plot_options.view_state == 'montage':
            montage_slice_idx = self._state.montage_slice_idx
            for montage_slice in montage_slice_idx:
                if self._state.montage_slice_dir == 'x':
                    montage_slice_idx[montage_slice]['y'] = click_coords['x']
                    montage_slice_idx[montage_slice]['z'] = click_coords['y']
                elif self._state.montage_slice_dir == 'y':
                    montage_slice_idx[montage_slice]['x'] = click_coords['x']
                    montage_slice_idx[montage_slice]['z'] = click_coords['y']
                elif self._state.montage_slice_dir == 'z':
                    montage_slice_idx[montage_slice]['x'] = click_coords['x']
                    montage_slice_idx[montage_slice]['y'] = click_coords['y']