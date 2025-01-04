"""Backend Data Management with DataManager singleton pattern.

This module provides a centralized data management system for the FIND viewer,
handling both NIFTI and GIFTI visualization states. It implements a singleton
pattern to ensure consistent state across the application.

Classes:
    ImageMetadata: Metadata for image visualization
    VisualizationState: Complete state for visualization
    DataManager: Singleton manager for visualization state
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, ClassVar, Any, TypedDict

import numpy as np
import nibabel as nib

from findviz.viz.io.timecourse import TaskDesignDict

# define output dict from get_viewer_data() method
class ViewerDataDict(TypedDict):
    file_type: str
    timepoints: List[int]
    global_min: float
    global_max: float
    ts_enabled: bool
    task_enabled: bool
    anat_input: Optional[bool]
    mask_input: Optional[bool]
    left_input: Optional[bool]
    right_input: Optional[bool]
    vertices_left: Optional[List[float]]
    faces_left: Optional[List[float]]
    vertices_right: Optional[List[float]]
    faces_right: Optional[List[float]]
    ts: Optional[Dict[str, List[float]]]
    ts_labels: Optional[List[str]]
    task: Optional[TaskDesignDict]


@dataclass
class ImageMetadata:
    """Metadata for image visualization.
    
    Attributes:
        timepoints: list of time points in the image
        global_min: Global minimum value across all timepoints
        global_max: Global maximum value across all timepoints
        slice_len: Length of each dimension for NIFTI images
    """
    timepoints: List[int]
    global_min: float
    global_max: float
    slice_len: Optional[Dict[str, int]] = None  # Only for NIFTI: {'x': int, 'y': int, 'z': int}


@dataclass
class VisualizationState:
    """Complete state for visualization.
    
    Attributes:
        file_type: Type of neuroimaging file ('nifti' or 'gifti')
        metadata: Image metadata
        ts_enabled: Whether timeseries visualization is enabled
        task_enabled: Whether task design visualization is enabled
        nifti_data: Dictionary of NIFTI images
        anat_input: Boolean for whether anatomical NIFTI data was provided
        mask_input: Boolean for whether mask NIFTI data was provided
        gifti_data: Dictionary of GIFTI images
        left_input: Boolean for whether left hemisphere GIFTI data was provided
        right_input: Boolean for whether right hemisphere GIFTI data was provided
        vertices_left: Vertex coordinates for left hemisphere
        vertices_right: Vertex coordinates for right hemisphere
        faces_left: Face indices for left hemisphere
        faces_right: Face indices for right hemisphere
        timeseries: Dictionary of timeseries data
        ts_labels: Labels for timeseries
        task_data: Task design information
    """
    file_type: str  # 'nifti' or 'gifti'
    metadata: ImageMetadata
    ts_enabled: bool = False
    task_enabled: bool = False
    
    # NIFTI-specific fields
    nifti_data: Dict[str, nib.Nifti1Image] = field(default_factory=dict)
    anat_input: bool = False
    mask_input: bool = False
    
    # GIFTI-specific fields
    gifti_data: Dict[str, nib.gifti.GiftiImage] = field(default_factory=dict)
    left_input: bool = False
    right_input: bool = False
    vertices_left: Optional[np.ndarray] = None
    vertices_right: Optional[np.ndarray] = None
    faces_left: Optional[np.ndarray] = None
    faces_right: Optional[np.ndarray] = None
    
    # Time series data
    timeseries: Dict[str, np.ndarray] = field(default_factory=dict)
    ts_labels: List[str] = field(default_factory=list)
    
    # Task design data
    task_data: Optional[Dict] = None

class DataManager:
    """Singleton manager for visualization state.
    
    This class implements the singleton pattern to maintain a single source of truth
    for the visualization state across the entire application. It handles both NIFTI
    and GIFTI data types and their associated metadata.
    
    Attributes:
        _instance (ClassVar[Optional[DataManager]]): Singleton instance
        _state (Optional[VisualizationState]): Current visualization state
        _preprocessed (Dict): Storage for preprocessed data
    
    Methods:
        create_nifti_state(): Initialize state for NIFTI data
        create_gifti_state(): Initialize state for GIFTI data
        add_timeseries(): Add timeseries data to state
        add_task_design(): Add task design data to state
        get_viewer_data(): Get formatted data for viewer
    """
    _instance: ClassVar[Optional['DataManager']] = None
    _state: Optional[VisualizationState]
    _preprocessed: Dict[str, Any]
    
    def __new__(cls) -> 'DataManager':
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize instance attributes (without type annotations here)
            cls._instance._state = None
            cls._instance._preprocessed = {}
        return cls._instance

    @property
    def state(self) -> Optional[VisualizationState]:
        return self._state
        
    def create_nifti_state(
        self, 
        func_img: nib.Nifti1Image, 
        anat_img: Optional[nib.Nifti1Image] = None,
        mask_img: Optional[nib.Nifti1Image] = None
    ) -> None:
        """Create visualization state for NIFTI data"""
        from findviz.viz.viewer.utils import package_nii_metadata
        
        metadata = package_nii_metadata(func_img)
        
        self._state = VisualizationState(
            file_type='nifti',
            metadata=ImageMetadata(
                timepoints=metadata['timepoints'],
                global_min=metadata['global_min'],
                global_max=metadata['global_max'],
                slice_len=metadata['slice_len']
            )
        )
        
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
        
        self._state = VisualizationState(
            file_type='gifti',
            metadata=ImageMetadata(
                timepoints=metadata['timepoints'],
                global_min=metadata['global_min'],
                global_max=metadata['global_max']
            )
        )
        
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
        """Add time series data"""
        if self._state:
            self._state.timeseries = timeseries
            self._state.ts_labels = list(timeseries.keys())
            self._state.ts_enabled = True
    
    def add_task_design(self, task_data: Dict) -> None:
        """Add task design data"""
        if self._state:
            self._state.task_data = task_data
            self._state.task_enabled = True
    
    def get_viewer_data(self) -> ViewerDataDict:
        """Get data formatted for viewer"""
        if not self._state:
            return {}
            
        data = {
            'file_type': self._state.file_type,
            'timepoints': self._state.metadata.timepoints,
            'global_min': float(self._state.metadata.global_min),
            'global_max': float(self._state.metadata.global_max),
            'ts_enabled': self._state.ts_enabled,
            'task_enabled': self._state.task_enabled
        }
        
        # Add file type specific data
        if self._state.file_type == 'nifti':
            data.update({
                'anat_input': self._state.anat_input,
                'mask_input': self.state.mask_input,
                'slice_len': self._state.metadata.slice_len
            })
        else:  # gifti
            data.update({
                'left_input': self._state.left_input,
                'right_input': self._state.right_input,
                'vertices_left': self._state.vertices_left,
                'faces_left': self._state.faces_left,
                'vertices_right': self._state.vertices_right,
                'faces_right': self._state.faces_right
            })
        
        # add time series, if passed
        if self._state.ts_enabled:
            data.update({
                'ts': self._state.timeseries,
                'ts_labels': self._state.ts_labels 
            })
        
        if self._state.task_enabled:
            data.update({
                'task': self._state.task_data
            })
        return data
    
    def store_preprocessed(self, data: Dict) -> None:
        """Store preprocessed data."""
        self._preprocessed.update(data)
        
    def get_preprocessed(self, key: str) -> Optional[object]:
        """Get preprocessed data by key."""
        return self._preprocessed.get(key)
        
    def clear_preprocessed(self) -> None:
        """Clear preprocessed data."""
        self._preprocessed.clear()