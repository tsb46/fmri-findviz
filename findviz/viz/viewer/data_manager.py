"""Backend Data Management with DataManager singleton pattern.

This module provides a centralized data management system for the FIND viewer,
handling both NIFTI and GIFTI visualization states. It implements a singleton
pattern to ensure consistent state across the application.

Classes:
    DataManager: Singleton manager for visualization state
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Literal, ClassVar, Any, TypedDict

import numpy as np
import nibabel as nib

from findviz.viz.io.timecourse import TaskDesignDict
from findviz.viz.viewer.types import (
    ViewerDataNiftiDict, ViewerDataGiftiDict, 
    ViewerMetadataNiftiDict, ViewerMetadataGiftiDict
)

logger = logging.getLogger(__name__)


@dataclass
class NiftiVisualizationState:
    """Visualization state for NIFTI data.
    
    Attributes:
        file_type: constant 'nifti'
        timepoints: Timepoint indices
        global_min: Global minimum value across all timepoints
        global_max: Global maximum value across all timepoints
        slice_len: Length of each dimension for NIFTI images
        anat_input: Whether anatomical data was provided
        mask_input: Whether mask data was provided
        ts_enabled: Whether time course data is enabled
        task_enabled: Whether task design data is enabled
        preprocessed: Whether preprocessed data is available
        view_state: View state ('ortho' or 'montage')
        nifti_data: Dictionary of NIFTI images
        ortho slices: Ortho slice indices for NIFTI data
        montage slice direction: Direction of montage slice for NIFTI data
        task_data: Task design information
        ts_data: Dictionary of timeseries data
        ts_labels: Labels for timeseries
    """
    # metadata
    timepoints: List[int]
    global_min: float
    global_max: float
    file_type: str = 'nifti'
    slice_len: Optional[Dict[str, int]] = None # {'x': int, 'y': int, 'z': int}
    anat_input: bool = False
    mask_input: bool = False
    ts_enabled: bool = False
    task_enabled: bool = False
    preprocessed: bool = False
    view_state: Literal['ortho', 'montage'] = 'ortho'

    # nifti data
    nifti_data: Dict[str, nib.Nifti1Image] = field(default_factory=dict)
    nifti_data_preprocessed: Dict[str, nib.Nifti1Image] = field(default_factory=dict)

    # ortho slice indices
    x_slice_idx: int = 0
    y_slice_idx: int = 0
    z_slice_idx: int = 0

    # montage slice direction
    montage_slice_dir: Optional[Literal['x', 'y', 'z']] = None

    # task design and timeseries
    task_data: Optional[TaskDesignDict] = None
    ts_data: Optional[Dict[str, List[float]]] = None
    ts_labels: Optional[List[str]] = None
    

@dataclass
class GiftiVisualizationState:
    """Visualization state for GIFTI data.
    
    Attributes:
        file_type: constant 'gifti'
        timepoints: Timepoint indices
        global_min: Global minimum value across all timepoints
        global_max: Global maximum value across all timepoints
        left_input: Whether left hemisphere data was provided
        right_input: Whether right hemisphere data was provided
        ts_enabled: Whether time course data is enabled
        task_enabled: Whether task design data is enabled
        preprocessed: Whether preprocessed data is available
        gifti_data: Dictionary of GIFTI images
        vertices_left: Vertex coordinates for left hemisphere
        faces_left: Face indices for left hemisphere
        vertices_right: Vertex coordinates for right hemisphere
        faces_right: Face indices for right hemisphere
        selected_vertex: Selected vertex index
        selected_hemi: Selected hemisphere ('left' or 'right')
        task_data: Task design information
        ts_data: Dictionary of timeseries data
        ts_labels: Labels for timeseries
    """
    # metadata
    timepoints: List[int]
    global_min: float
    global_max: float
    file_type: str = 'gifti'
    left_input: bool = False
    right_input: bool = False
    ts_enabled: bool = False
    task_enabled: bool = False
    preprocessed: bool = False
    vertices_left: Optional[List[float]] = None
    faces_left: Optional[List[float]] = None
    vertices_right: Optional[List[float]] = None
    faces_right: Optional[List[float]] = None
    
    # gifti data
    gifti_data: Dict[str, nib.gifti.GiftiImage] = field(default_factory=dict)
    gifti_data_preprocessed: Dict[str, nib.gifti.GiftiImage] = field(default_factory=dict)

    # selected vertex and hemisphere
    selected_vertex: Optional[int] = None
    selected_hemi: Optional[Literal['left', 'right']] = None
    
    # task design and timeseries
    task_data: Optional[TaskDesignDict] = None
    ts_data: Optional[Dict[str, List[float]]] = None
    ts_labels: Optional[List[str]] = None


class DataManager:
    """Singleton manager for visualization state.
    
    This class implements the singleton pattern to maintain a single source of truth
    for the visualization state across the entire application. It handles both NIFTI
    and GIFTI data types and their associated metadata.
    
    Attributes:
        _instance (ClassVar[Optional[DataManager]]): Singleton instance
        _state (Optional[VisualizationState]): Current visualization state
    
    Methods:
        create_nifti_state(): Initialize state for NIFTI data
        create_gifti_state(): Initialize state for GIFTI data
        add_timeseries(): Add timeseries data to state
        add_task_design(): Add task design data to state
        get_location_data(): Get brain location data
        get_viewer_metadata(): Get metadata for viewer
        get_viewer_data(): Get formatted data for viewer
        update_location(): Update brain location data
        store_preprocessed(): Store preprocessed data
        clear_preprocessed(): Clear preprocessed data
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
    def state(self) -> Optional[NiftiVisualizationState | GiftiVisualizationState]:
        return self._state
    
    @property
    def file_type(self) -> Optional[str]:
        return self._state.file_type if self._state else None
    
    @property
    def preprocessed(self) -> bool:
        return self._state.preprocessed
        
    def create_nifti_state(
        self, 
        func_img: nib.Nifti1Image,
        anat_img: Optional[nib.Nifti1Image] = None,
        mask_img: Optional[nib.Nifti1Image] = None
    ) -> None:
        """Create visualization state for NIFTI data"""
        from findviz.viz.viewer.utils import package_nii_metadata
        
        metadata = package_nii_metadata(func_img)
        
        self._state = NiftiVisualizationState(
            timepoints=metadata['timepoints'],
            global_min=metadata['global_min'],
            global_max=metadata['global_max'],
            slice_len=metadata['slice_len']
        )  # file_type defaults to 'nifti' in the dataclass
        
        # Store images
        if func_img:
            self._state.nifti_data['func'] = func_img
        if anat_img:
            self._state.nifti_data['anat'] = anat_img
            self._state.anat_input = True
        if mask_img:
            self._state.nifti_data['mask'] = mask_img
            self._state.mask_input = True
                
    def create_gifti_state(
        self,
        left_func: Optional[nib.gifti.GiftiImage] = None,
        right_func: Optional[nib.gifti.GiftiImage] = None,
        left_mesh: Optional[nib.gifti.GiftiImage] = None,
        right_mesh: Optional[nib.gifti.GiftiImage] = None
    ) -> None:
        """Create visualization state for GIFTI data"""
        from findviz.viz.viewer.utils import package_gii_metadata
        
        metadata = package_gii_metadata(left_func, right_func)
        
        self._state = GiftiVisualizationState(
            timepoints=metadata['timepoints'],
            global_min=metadata['global_min'],
            global_max=metadata['global_max']
        )  # file_type defaults to 'gifti' in the dataclass
        
        # Store functional data
        if left_func:
            self._state.gifti_data['left_func'] = left_func
            self._state.left_input = True
        if right_func:
            self._state.gifti_data['right_func'] = right_func
            self._state.right_input = True
            
        # Store mesh data
        # assumes first position is coordinates, and second is faces
        if left_mesh:
            self._state.vertices_left = left_mesh.darrays[0].data.tolist()
            self._state.faces_left = left_mesh.darrays[1].data.tolist()
        if right_mesh:
            self._state.vertices_right = right_mesh.darrays[0].data.tolist()
            self._state.faces_right = right_mesh.darrays[1].data.tolist()
                
    def add_timeseries(self, timeseries: Dict[str, np.ndarray]) -> None:
        """Add time series data if not already present"""
        if not self._state:
            logger.error("No state exists")
            return
        
        self._state.ts_data = timeseries
        self._state.ts_labels = list(timeseries.keys())
        self._state.ts_enabled = True
    
    def add_task_design(self, task_data: TaskDesignDict) -> None:
        """Add task design data"""
        if not self._state:
            logger.error("No state exists")
            return
        
        self._state.task_data = task_data
        self._state.task_enabled = True
    
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
    
    def get_viewer_metadata(self) -> ViewerMetadataNiftiDict | ViewerMetadataGiftiDict:
        """Get metadata for viewer"""
        if not self._state:
            logger.error("No state exists")
            return {}
        
        if self._state.file_type == 'nifti':
            data = ViewerMetadataNiftiDict(
                file_type=self._state.file_type,
                anat_input=self._state.anat_input,
                mask_input=self._state.mask_input,
                timepoints=self._state.timepoints,
                global_min=self._state.global_min,
                global_max=self._state.global_max,
                slice_len=self._state.slice_len,
                preprocessed=self._state.preprocessed,
                ts_enabled=self._state.ts_enabled,
                task_enabled=self._state.task_enabled
            )
        else:
            data = ViewerMetadataGiftiDict(
                file_type=self._state.file_type,
                left_input=self._state.left_input,
                right_input=self._state.right_input,
                vertices_left=self._state.vertices_left,
                faces_left=self._state.faces_left,
                vertices_right=self._state.vertices_right,
                faces_right=self._state.faces_right,
                timepoints=self._state.timepoints,
                global_min=self._state.global_min,
                global_max=self._state.global_max,
                preprocessed=self._state.preprocessed,
                ts_enabled=self._state.ts_enabled,
                task_enabled=self._state.task_enabled
            )

        return data

    def get_viewer_data(
        self,
        fmri_data: bool = True,
        use_preprocess: bool = False,
        time_course_data: bool = True,
        task_data: bool = True
    ) -> ViewerDataNiftiDict | ViewerDataGiftiDict:
        """Get data formatted for viewer.

        Arguments:
            fmri_data: Whether to include fMRI image data. Defaults to True.
            use_preprocess: Whether to use preprocessed data if available. Defaults to False.
            time_course_data: Whether to include time course data. Defaults to True.
            task_data: Whether to include task design data. Defaults to True.

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
                if use_preprocess:
                    if self._state.preprocessed:
                        data.update({
                            'func_img': self._state.nifti_data_preprocessed['func']
                        })
                    else:
                        logger.error("Preprocessed data not found")
                else:
                    data.update({
                        'func_img': self._state.nifti_data['func']
                    })

                data.update({
                    'anat_input': self._state.anat_input,
                    'mask_input': self.state.mask_input,
                    'anat_img': self._state.nifti_data['anat'],
                    'mask_img': self._state.nifti_data['mask'],
                    'func_img': self._state.nifti_data['func'],
                })
            else:  # gifti
                if use_preprocess:
                    if self._state.preprocessed:
                        data.update({
                            'left_func_img': self._state.gifti_data_preprocessed['left_func'],
                            'right_func_img': self._state.gifti_data_preprocessed['right_func']
                        })
                    else:
                        logger.error("Preprocessed data not found")
                else:
                    data.update({
                        'left_func_img': self._state.gifti_data['left_func'],
                        'right_func_img': self._state.gifti_data['right_func']
                    })
                
                data.update({
                    'left_input': self._state.left_input,
                    'right_input': self._state.right_input,
                })
        
        # add time series, if passed
        if time_course_data:
            if self._state.ts_enabled:
                data.update({
                    'ts': self._state.ts_data,
                    'ts_labels': self._state.ts_labels 
                })
        
        # add task data, if passed
        if task_data:
            if self._state.task_enabled:
                data.update({
                    'task': self._state.task_data
                })
        return data
    
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
    
    def pop_timecourse(self) -> None:
        """Pop most recent timecourse from state"""
        if not self._state:
            logger.error("No state exists")
            return
        
        self._state.ts_data.pop(self._state.ts_labels[-1])
        self._state.ts_labels = list(self._state.ts_data.keys())
    
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

    def store_preprocessed(self, data: Dict) -> None:
        """Store preprocessed data."""
        logger.info("Storing preprocessed data")
        self._state.preprocessed = True
        if self._state.file_type == 'nifti':
            self._state.nifti_data_preprocessed.update(data)
        else:
            self._state.gifti_data_preprocessed.update(data)
        
    def clear_preprocessed(self) -> None:
        """Clear preprocessed data."""
        logger.info("Clearing preprocessed data")
        self._state.preprocessed = False
        if self._state.file_type == 'nifti':
            self._state.nifti_data_preprocessed.clear()
        else:
            self._state.gifti_data_preprocessed.clear()

    def clear_state(self) -> None:
        """Clear state."""
        logger.info("Clearing data managerstate")
        self._state = None
