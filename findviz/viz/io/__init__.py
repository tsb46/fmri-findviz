"""
File I/O module for handling various neuroimaging file formats and associated data.

This module provides utilities for loading, validating, and processing:
- NIFTI files (.nii, .nii.gz)
- GIFTI files (.gii)
- CIFTI files (.dtseries.nii)
- Time course data (.csv, .txt)
- Task design files (.csv, .txt)
"""

from findviz.viz.io import cifti
from findviz.viz.io import gifti
from findviz.viz.io import nifti
from findviz.viz.io import timecourse
from findviz.viz.io import upload
from findviz.viz.io import validate

__all__ = [
    'cifti',
    'gifti',
    'nifti',
    'timecourse',
    'upload',
    'validate'
]