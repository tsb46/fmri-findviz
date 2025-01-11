"""
FINDVIZ Visualization Module

This module provides core functionality for handling, processing, and visualizing
neuroimaging data in the FINDVIZ application.

Submodules:
    - io: Input/output operations for neuroimaging data formats (NIFTI, GIFTI)
    - viewer: Components for managing and visualizing neuroimaging data
    - analysis: Tools for analyzing neuroimaging data
    - transforms: Format conversions between neuroimaging data types
    - exception: Custom exceptions for error handling

Example:
    >>> from findviz.viz.io import FileUpload
    >>> from findviz.viz.viewer import DataManager
    >>> from findviz.viz.transforms import nifti_to_array
    >>> 
    >>> # Upload and process neuroimaging data
    >>> uploader = FileUpload()
    >>> data = uploader.upload(fmri_files={'func': 'func.nii.gz'})
    >>> 
    >>> # Convert NIFTI to array for processing
    >>> array_data = nifti_to_array(data['nifti']['func'])
    >>> 
    >>> # Create visualization state
    >>> dm = DataManager()
    >>> dm.create_nifti_state(func_img=data['nifti']['func'])
"""

from findviz.viz import io
from findviz.viz import viewer
from findviz.viz import analysis
from findviz.viz import transforms
from findviz.viz import exception

# Version information
__version__ = '0.1.0'

__all__ = [
    'io',          # Input/output operations
    'viewer',      # Visualization components
    'analysis',    # Analysis tools
    'transforms',  # Format conversions
    'exception',   # Custom exceptions
]

# Module level logger
import logging
logger = logging.getLogger(__name__)