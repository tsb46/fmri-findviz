"""
FINDVIZ Viewer Module

This module provides functionality for managing and visualizing neuroimaging data.
It includes components for handling both NIFTI and GIFTI data formats, as well as
supporting time series and task design data visualization.

Components:
    - data_manager: Singleton class for managing visualization state
    - types: Type definitions for visualization states and data structures
    - state: Visualization state classes
    - utils: Utility functions for data processing and metadata extraction

Example:
    >>> from findviz.viz.viewer import data_manager
    >>> dm = data_manager.DataManager()
    >>> dm.create_nifti_state(func_img=nifti_img)
"""

from findviz.viz.viewer.utils import (
    package_gii_metadata,
    package_nii_metadata
)

from findviz.viz.viewer.types import (
    ViewerMetadataNiftiDict,
    ViewerMetadataGiftiDict,
    ViewerDataNiftiDict,
    ViewerDataGiftiDict
)

from findviz.viz.viewer.data_manager import DataManager
from findviz.viz.viewer.state.viz_state import (
    NiftiVisualizationState,
    GiftiVisualizationState
)
from findviz.viz.viewer.state import components

__all__ = [
    # Data Manager
    'DataManager',
    
    # states
    'components',
    'NiftiVisualizationState',
    'GiftiVisualizationState',
    
    # Type Definitions
    'ViewerMetadataNiftiDict',
    'ViewerMetadataGiftiDict',
    'ViewerDataNiftiDict',
    'ViewerDataGiftiDict',
    
    # Utility Functions
    'package_gii_metadata',
    'package_nii_metadata'
] 