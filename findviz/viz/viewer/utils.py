"""Utility functions for processing neuroimaging data.

This module provides helper functions for processing NIFTI and GIFTI data,
including metadata extraction and value range calculations.
"""

from typing import Dict, Tuple, Union, Optional, List, Literal

import numpy as np

from nibabel.gifti import GiftiImage
from nibabel.nifti1 import Nifti1Image

def get_minmax(
    data: Union[np.ndarray, GiftiImage], 
    file_type: Literal['gifti', 'nifti']
) -> Tuple[float, float]:
    """Calculate global minimum and maximum values for neuroimaging data.
    
    Args:
        data: Input data array or GiftiImage
        file_type: Type of neuroimaging data ('gifti' or 'nifti')
    
    Returns:
        Tuple containing (global_minimum, global_maximum)
    
    Raises:
        ValueError: If file_type is not 'gifti' or 'nifti'
    """
    if file_type == 'nifti':
        if not isinstance(data, np.ndarray):
            raise TypeError("NIFTI data must be numpy array")
        data_min = float(np.nanmin(data))
        data_max = float(np.nanmax(data))
    elif file_type == 'gifti':
        if not isinstance(data, GiftiImage):
            raise TypeError("GIFTI data must be GiftiImage")
        data_min = float(np.nanmin([np.min(d.data) for d in data.darrays]))
        data_max = float(np.nanmax([np.max(d.data) for d in data.darrays]))
    else:
        raise ValueError("file_type must be 'gifti' or 'nifti'")

    return data_min, data_max


def package_gii_metadata(
    left_img: Optional[GiftiImage],
    right_img: Optional[GiftiImage]
) -> Dict[str, Union[float, List[int]]]:
    """Package metadata for GIFTI visualization.
    
    Args:
        left_img: Left hemisphere GIFTI image
        right_img: Right hemisphere GIFTI image
    
    Returns:
        Dictionary containing:
            - global_min: Global minimum value across both hemispheres
            - global_max: Global maximum value across both hemispheres
            - timepoints: List of timepoint indices
    """
    metadata: Dict[str, Union[float, List[int]]] = {}
    timepoints: Optional[List[int]] = None
    
    # Initialize with NaN
    global_min_left = np.nan
    global_max_left = np.nan
    global_min_right = np.nan
    global_max_right = np.nan
    
    if left_img is not None:
        global_min_left, global_max_left = get_minmax(left_img, 'gifti')
        timepoints = list(range(len(left_img.darrays)))
        
    if right_img is not None:
        global_min_right, global_max_right = get_minmax(right_img, 'gifti')
        if timepoints is None:
            timepoints = list(range(len(right_img.darrays)))

    metadata['global_min'] = float(np.nanmin([global_min_left, global_min_right]))
    metadata['global_max'] = float(np.nanmax([global_max_left, global_max_right]))
    metadata['timepoints'] = timepoints or []
    
    return metadata


def package_nii_metadata(
    nii_img: Nifti1Image
) -> Dict[str, Union[float, List[int], Dict[str, int]]]:
    """Package metadata for NIFTI visualization.
    
    Args:
        nii_img: NIFTI image object
    
    Returns:
        Dictionary containing:
            - global_min: Global minimum value
            - global_max: Global maximum value
            - timepoints: List of timepoint indices
            - slice_len: Dictionary of x,y,z dimensions
    """
    data = nii_img.get_fdata()
    data_min, data_max = get_minmax(data, 'nifti')
    
    metadata: Dict[str, Union[float, List[int], Dict[str, int]]] = {
        'global_min': float(data_min),
        'global_max': float(data_max),
        'timepoints': list(range(data.shape[3])) if len(data.shape) > 3 else [0],
        'slice_len': {
            'x': int(data.shape[0]),
            'y': int(data.shape[1]),
            'z': int(data.shape[2])
        }
    }
    
    return metadata

