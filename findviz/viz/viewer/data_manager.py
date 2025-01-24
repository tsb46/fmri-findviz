"""Backend Data Management with DataManager singleton pattern.

This module provides a centralized data management system for the FIND viewer,
handling both NIFTI and GIFTI visualization states. It implements a singleton
pattern to ensure consistent state across the application.

Classes:
    DataManager: Singleton manager for visualization state
"""

import logging

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Literal, ClassVar, Any, TypedDict, Tuple

import numpy as np
import nibabel as nib

from findviz.viz.viewer.state import (
    NiftiVisualizationState, 
    GiftiVisualizationState,
    PlotOptions,
    TimeCoursePlotOptions
)

from findviz.viz.io.timecourse import TaskDesignDict
from findviz.viz.viewer.types import (
    ViewerDataNiftiDict, ViewerDataGiftiDict, 
    ViewerMetadataNiftiDict, ViewerMetadataGiftiDict,
    PlotOptionsDict, TimeCoursePlotOptionsDict
)
from findviz.viz.viewer.utils import (
    apply_mask_nifti, get_coord_labels,
    package_nii_metadata, package_gii_metadata
)

logger = logging.getLogger(__name__)


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
        create_nifti_state(): Initialize state for NIFTI data
        create_gifti_state(): Initialize state for GIFTI data
        add_timeseries(): Add timeseries data to state
        add_task_design(): Add task design data to state
        get_location_data(): Get brain location data
        get_plot_options(): Get plot options
        get_timecourse_plot_options(): Get time course plot options for a given label
        get_viewer_metadata(): Get metadata for viewer
        get_viewer_data(): Get formatted data for viewer
        update_location(): Update brain location data
        update_plot_options(): Update plot options
        update_timecourse_plot_options(): Update time course plot options for a given label
        update_timepoint(): Update timepoint data
        pop_annotation_marker(): Pop most recent annotation marker from state
        pop_timecourse(): Pop most recent timecourse from state
        reset_color_options(): Reset color options to original
        store_fmri_preprocessed(): Store preprocessed fMRI data
        store_timecourse_preprocessed(): Store preprocessed timecourse data
        update_timecourse(): Update time course data with new timecourse and label
        clear_fmri_preprocessed(): Clear preprocessed fMRI data
        clear_timecourse_preprocessed(): Clear preprocessed timecourse data
        clear_state(): Clear state
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

    @property
    def allowed_precision(self) -> int:
        return self._state.allowed_precision if self._state else 6
    
    @property
    def state(self) -> Optional[NiftiVisualizationState | GiftiVisualizationState]:
        return self._state
    
    @property
    def file_type(self) -> Literal['nifti', 'gifti']:
        return self._state.file_type if self._state else None
    
    @property
    def timepoint(self) -> Optional[int]:
        return self._state.timepoint if self._state else None
    
    @property
    def fmri_preprocessed(self) -> bool:
        return self._state.fmri_preprocessed
    
    @property
    def ts_preprocessed(self) -> bool:
        return self._state.ts_preprocessed
    
    @property
    def annotation_markers(self) -> List[int]:
        return self._state.annotation_markers
    
    @property
    def annotation_selection(self) -> Optional[int]:
        return self._state.annotation_selection
    
    def add_annotation_marker(self, marker: int) -> None:
        """Add annotation marker"""
        if not self._state:
            logger.error("No state exists")
            return
        self._state.annotation_markers.append(marker)
        self._state.annotation_selection = marker
    
    def add_timeseries(self, timeseries: Dict[str, np.ndarray]) -> None:
        """Add time series data if not already present"""
        if not self._state:
            logger.error("No state exists")
            return
        # Initialize time series data
        self._state.ts_data = timeseries
        self._state.ts_labels = list(timeseries.keys())
        self._state.ts_enabled = True

        # Create plot options for each timeseries with unique colors
        for label in self._state.ts_labels:
            plot_options = TimeCoursePlotOptions.with_next_color(
                self._state.used_colors,
            )
            self._state.used_colors.add(plot_options.color)
            self._state.ts_plot_options[label] = plot_options

    
    def add_task_design(self, task_data: TaskDesignDict) -> None:
        """Add task design data"""
        if not self._state:
            logger.error("No state exists")
            return
        
        # add conditions
        self._state.conditions = task_data['task_regressors'].keys()
        self._state.task_data = task_data
        self._state.task_enabled = True

        # Create plot options for each task condition with unique colors
        for label in self._state.conditions:
            plot_options = TimeCoursePlotOptions.with_next_color(
                self._state.used_colors,
            )
            self._state.used_colors.add(plot_options.color)
            self._state.task_plot_options[label] = plot_options

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
            x_slice_idx=metadata['x_slice_idx'],
            y_slice_idx=metadata['y_slice_idx'],
            z_slice_idx=metadata['z_slice_idx'],
            plot_options=PlotOptions(
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
            'color_min': self._state.color_options.color_min,
            'color_max': self._state.color_options.color_max,
            'color_range': self._state.color_options.color_range,
            'threshold_min': self._state.color_options.threshold_min,
            'threshold_max': self._state.color_options.threshold_max,
            'threshold_range': self._state.color_options.threshold_range,
            'opacity': self._state.color_options.opacity
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
            plot_options=PlotOptions(
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
            'color_min': self._state.plot_options.color_min,
            'color_max': self._state.plot_options.color_max,
            'color_range': self._state.plot_options.color_range,
            'threshold_min': self._state.plot_options.threshold_min,
            'threshold_max': self._state.plot_options.threshold_max,
            'threshold_range': self._state.plot_options.threshold_range,
            'opacity': self._state.plot_options.opacity
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
    
    def get_location_data(self) -> Dict[str, Any]:
        """Get brain location data"""
        if not self._state:
            logger.error("No state exists")
            return {}
        if self._state.file_type == 'nifti':
            loc_data = {
                'x': self._state.x_slice_idx,
                'y': self._state.y_slice_idx,
                'z': self._state.z_slice_idx,
            }
        else:
            loc_data = {
                'selected_vertex': self._state.selected_vertex,
                'selected_hemi': self._state.selected_hemi
            }
        return loc_data
    
    def get_plot_options(self) -> PlotOptionsDict:
        """Get plot options"""
        if not self._state:
            logger.error("No state exists")
            return {}
        
        if self._state.fmri_preprocessed:
            data = self._state.preprocessed_plot_options.to_dict()
        else:
            data = self._state.plot_options.to_dict()
        
        return data
    
    def get_timecourse_plot_options(
        self, 
        label: Optional[str] = None
    ) -> TimeCoursePlotOptionsDict | Dict[str, TimeCoursePlotOptionsDict]:
        """Get time course plot options for a given label"""
        if not self._state:
            logger.error("No state exists")
            return {}
        if label:
            return self._state.ts_plot_options[label].to_dict()
        else:
            return {
                label: plot_options.to_dict()
                for label, plot_options in self._state.ts_plot_options.items()
            }
    
    def get_viewer_metadata(self) -> ViewerMetadataNiftiDict | ViewerMetadataGiftiDict:
        """Get metadata for viewer"""
        if not self._state:
            logger.error("No state exists")
            return {}
        
        if self._state.file_type == 'nifti':
            data = ViewerMetadataNiftiDict(
                file_type=self._state.file_type,
                timepoint=self._state.timepoint,
                anat_input=self._state.anat_input,
                mask_input=self._state.mask_input,
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
        if not self._state:
            logger.error("No state exists")
            return {}
        
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
                data.update({
                    'task': self._state.task_data
                })
            else:
                logger.warning(
                    "Task data request received, but no "
                    "task data exists"
                )
        return data
    
    def pop_annotation_marker(self) -> None:
        """Pop most recent annotation marker from state"""
        if not self._state:
            logger.error("No state exists")
            return
        
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

    def pop_timecourse(self) -> None:
        """Pop most recent timecourse from state"""
        if not self._state:
            logger.error("No state exists")
            return
        
        # remove last timecourse
        last_label = self._state.ts_labels[-1]
        self._state.ts_data.pop(last_label)
        # Remove the color from used colors before removing plot options
        if last_label in self._state.ts_plot_options:
            self._state.used_colors.remove(
                self._state.ts_plot_options[last_label].color
            )
        self._state.ts_plot_options.pop(last_label)
        self._state.ts_labels = list(self._state.ts_data.keys())
        logger.info("Popped most recent timecourse from state")

    def reset_color_options(self) -> None:
        """Reset color options to original"""
        if not self._state:
            logger.error("No state exists")
            return
        
        # return color options to original state
        if self._state.fmri_preprocessed:
            color_options = self._state.preprocessed_color_options_original
            self._state.preprocessed_plot_options.update_from_dict(
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
            self._state.plot_options.update_from_dict(
                {
                    'color_min': color_options['color_min'],
                    'color_max': color_options['color_max'],
                    'threshold_min': color_options['threshold_min'],
                    'threshold_max': color_options['threshold_max'],
                    'opacity': color_options['opacity']
                }
            )

        logger.info("Reset color options to original")
    
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
        self._state.preprocessed_plot_options = PlotOptions(
            color_min=metadata['color_min'],
            color_max=metadata['color_max'],
            color_range=metadata['color_range'],
            threshold_min=metadata['threshold_min'],
            threshold_max=metadata['threshold_max'],
            threshold_range=metadata['threshold_range'],
            precision=metadata['precision'],
            slider_steps=metadata['slider_step_size'],
            hover_text_on=self._state.plot_options.hover_text_on,
            color_map=self._state.plot_options.color_map,
            opacity=self._state.plot_options.opacity,
            view_state=self._state.plot_options.view_state,
            montage_slice_dir=self._state.plot_options.montage_slice_dir,
            crosshair_on=self._state.plot_options.crosshair_on,
            direction_marker_on=self._state.plot_options.direction_marker_on,
            montage_slice_idx=self._state.plot_options.montage_slice_idx
        )
        
        # preserve original color options
        self._state.preprocessed_color_options_original = {
            'color_min': self._state.preprocessed_plot_options.color_min,
            'color_max': self._state.preprocessed_plot_options.color_max,
            'color_range': self._state.preprocessed_plot_options.color_range,
            'threshold_min': self._state.preprocessed_plot_options.threshold_min,
            'threshold_max': self._state.preprocessed_plot_options.threshold_max,
            'threshold_range': self._state.preprocessed_plot_options.threshold_range,
            'opacity': self._state.preprocessed_plot_options.opacity
        }
    
    def store_timecourse_preprocessed(self, data: Dict) -> None:
        """Store preprocessed timecourse data."""
        logger.info("Storing preprocessed timecourse data")
        self._state.ts_preprocessed = True
        self._state.ts_data_preprocessed = data

    def update_annotation_selection(self, marker_value: int) -> None:
        """Update annotation selection"""
        if not self._state:
            logger.error("No state exists")
            return
        
        # check if marker value is in annotation markers
        if marker_value in self._state.annotation_markers:
            # get index of marker value
            marker_idx = self._state.annotation_markers.index(marker_value)
            # update selection
            self._state.annotation_selection = marker_idx
            logger.info("Updated annotation selection")
        else:
            logger.warning("Marker value not found in annotation markers")

    def update_location(self, loc_data: Dict[str, Any]) -> None:
        """Update brain location data"""
        if not self._state:
            logger.error("No state exists")
            return
        
        if self._state.file_type == 'nifti':
            self._state.x_slice_idx = loc_data['x']
            self._state.y_slice_idx = loc_data['y']
            self._state.z_slice_idx = loc_data['z']
        else:
            self._state.selected_vertex = loc_data['selected_vertex']
            self._state.selected_hemi = loc_data['selected_hemi']
        
        logger.info("Updated brain location data")
    
    def update_plot_options(
        self,
        display_options: Dict[str, Any]
    ) -> None:
        """Update plot options"""
        if not self._state:
            logger.error("No state exists")
            return
        
        if self._state.fmri_preprocessed:
            self._state.preprocessed_plot_options.update_from_dict(display_options)
        else:
            self._state.plot_options.update_from_dict(display_options)
        
        logger.info("Updated plot options")
    
    def update_timecourse_plot_options(
        self, 
        label: str, 
        plot_options: Dict[str, Any]
    ) -> None:
        """Update time course plot options"""
        if not self._state:
            logger.error("No state exists")
            return
        
        self._state.ts_plot_options[label].update_from_dict(plot_options)
        logger.info("Updated time course plot options")

    def update_timepoint(self, timepoint: int) -> None:
        """Update timepoint data"""
        if not self._state:
            logger.error("No state exists")
            return
        
        # check if timepoint is within range
        if timepoint < 0 or timepoint >= self._state.timepoints:
            logger.error("Timepoint out of range")
            return
        
        self._state.timepoint = timepoint
        logger.info("Updated timepoint data")
    
    def update_timecourse(
        self, 
        timecourse: List[float], 
        label: str
    ) -> None:
        """Update time course data with new timecourse and label"""
        if not self._state:
            logger.error("No state exists")
            return
        if self._state.ts_data is None:
            raise ValueError(
                "Please initialize time course data first. "
                "Use add_timeseries() to initialize."
            )
        self._state.ts_data[label] = timecourse
        self._state.ts_labels = list(self._state.ts_data.keys())

        # Create plot options if not already present
        if label not in self._state.ts_plot_options:
            plot_options = TimeCoursePlotOptions.with_next_color(
                self._state.used_colors
            )
            self._state.used_colors.add(plot_options.color)
            self._state.ts_plot_options[label] = plot_options
    
    def clear_annotation_markers(self) -> None:
        """Clear annotation markers"""
        logger.info("Clearing annotation markers")
        self._state.annotation_markers = []
        self._state.annotation_selection = None

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
        
    def clear_timecourse_preprocessed(self) -> None:
        """Clear preprocessed timecourse data."""
        logger.info("Clearing preprocessed timecourse data")
        self._state.ts_preprocessed = False
        self._state.ts_data_preprocessed = None
        
    def clear_state(self) -> None:
        """Clear state."""
        logger.info("Clearing data managerstate")
        self._state = None
