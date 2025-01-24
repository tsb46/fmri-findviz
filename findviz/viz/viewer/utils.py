"""Utility functions for processing neuroimaging data.

This module provides helper functions for processing NIFTI and GIFTI data,
including metadata extraction and value range calculations.
"""
import decimal

from typing import Dict, Tuple, Union, Optional, List, Literal

import numpy as np
import nibabel as nib

from nibabel.gifti import GiftiImage
from nibabel.nifti1 import Nifti1Image
from nilearn.masking import apply_mask, unmask


def apply_mask_nifti(
    nifti_img: nib.Nifti1Image,
    mask_img: nib.Nifti1Image,
) -> nib.Nifti1Image:
    """Apply a mask to a NIfTI image

    Parameters
    ----------
    nifti_img : nib.Nifti1Image
        NIfTI image to mask
    mask_img : nib.Nifti1Image
        Mask image to apply

    Returns
    -------
    nib.Nifti1Image
        Masked NIfTI image
    """
    # apply mask
    masked_data = apply_mask(nifti_img, mask_img)
    # unmask data
    masked_img = unmask(masked_data, mask_img)
    return masked_img


def extend_color_range(
    color_min: float,
    color_max: float,
    extend_range: float = 0.05
) -> Tuple[float, float]:
    """Extend color range by a given percentage
    
    Parameters:
    -----------
    color_min: Minimum color value
    color_max: Maximum color value
    extend_range: Percentage to extend color range by
    
    Returns:
    --------
    Tuple containing (extended_color_min, extended_color_max)
    """
    return color_min - (extend_range * color_min), color_max + (extend_range * color_max)


def get_coord_labels(
    nii_img: Nifti1Image
) -> np.ndarray:
    """Get coordinate labels for NIFTI data"""
    data = nii_img.get_fdata()
    coord_labels = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(data.shape[2]):
                coord_labels.append((i, j, k))
    return np.array(coord_labels)


def get_minmax(
    data: Union[np.ndarray, GiftiImage], 
    file_type: Literal['gifti', 'nifti']
) -> Tuple[float, float]:
    """Calculate global minimum and maximum values for neuroimaging data.
    
    Parameters:
    -----------
    data : Union[np.ndarray, GiftiImage]
        Input data array or GiftiImage
    file_type : Literal['gifti', 'nifti']
        Type of neuroimaging data ('gifti' or 'nifti')
    
    Returns:
    --------
    Tuple containing (global_minimum, global_maximum)
    
    Raises:
    --------
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


def get_init_ortho_slice_idx(
    slice_len: Dict[str, int]
) -> Dict[str, int]:
    """Get initial orthogonal view slice indices for 
    NIFTI data as middle of x,y,z dimensions

    Parameters:
    -----------
    slice_len: Dictionary containing x,y,z dimensions
    
    Returns:
    --------
    Dictionary containing x,y,z slice indices
    """
    return {
        'x': int(slice_len['x'] / 2),
        'y': int(slice_len['y'] / 2),
        'z': int(slice_len['z'] / 2)
    }

def get_init_montage_slice_idx(
    slice_len: Dict[str, int],
    montage_slice_dir: Literal['x', 'y', 'z']
) -> List[int]:
    """Get initial montage slice indices for NIFTI data as 
    equally distributed across the slice direction

    Parameters:
    -----------
    slice_len: Dictionary containing x,y,z dimensions
    montage_slice_dir: Direction of montage slices
    
    Returns:
    --------
    List containing montage slice indices
    """
    # percentage of slice length to start montage slice at
    slice_len_dir = slice_len[montage_slice_dir]
    montage_slice_perc = [0.33, 0.5, 0.66]
    montage_slice_idx = []
    for perc in montage_slice_perc:
        slice_idx_dir = int(slice_len_dir * perc)
        montage_slice_idx.append(slice_idx_dir)

    return montage_slice_idx

def get_slider_step_size(
    data_range: float,
    slider_steps: int,
    precision: int
) -> float:
    """Calculate slider step size
    
    Parameters:
    -----------
    data_range: Range of data
    slider_steps: Number of steps in slider
    precision: Precision of step size
    
    Returns:
    --------
    Slider step size
    """
    return round(data_range/slider_steps, precision)


def get_precision(
    data_range: float,
    max_precision: int = 6
) -> int:
    """Calculate precision for slider step size"""
    data_range_dec = decimal.Decimal(data_range)
    precision = abs(data_range_dec.as_tuple().exponent)
    if precision > max_precision:
        return max_precision
    return precision


def package_gii_metadata(
    left_img: Optional[GiftiImage],
    right_img: Optional[GiftiImage],
    slider_steps: int,
    precision: int
) -> Dict[str, Union[float, List[int]]]:
    """Package metadata for GIFTI visualization.
    
    Parameters:
    -----------
    left_img: Left hemisphere GIFTI image
    right_img: Right hemisphere GIFTI image
    slider_steps: Number of steps in slider
    precision: Precision of step size
    
    Returns:
    --------
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
    # Calculate precision for slider step size
    precision = get_precision(
        data_range=metadata['global_max'] - metadata['global_min']
    )
    metadata['precision'] = precision
    metadata['timepoints'] = timepoints or []
    metadata['color_min'] = metadata['global_min']
    metadata['color_max'] = metadata['global_max']
    metadata['color_range'] = extend_color_range(
        metadata['color_min'], 
        metadata['color_max']
    )
    metadata['threshold_range'] = metadata['color_range']
    metadata['slider_step_size'] = get_slider_step_size(
        metadata['color_range'][1] - metadata['color_range'][0],
        slider_steps,
        metadata['precision']
    )
    
    return metadata


def package_nii_metadata(
    nii_img: Nifti1Image,
    slider_steps: int,
    precision: int
) -> Dict[str, Union[float, List[int], Dict[str, int]]]:
    """Package metadata for NIFTI visualization.
    
    Parameters:
    -----------
    nii_img: NIFTI image object
    
    Returns:
    --------
    Dictionary containing:
        - global_min: Global minimum value
        - global_max: Global maximum value
        - color_min: Minimum value for color mapping
        - color_max: Maximum value for color mapping
        - color_range: Color range for color mapping
        - timepoints: List of timepoint indices
        - slice_len: Dictionary of x,y,z dimensions
        - x_slice_idx: Initial x slice index
        - y_slice_idx: Initial y slice index
        - z_slice_idx: Initial z slice index
        - montage_slice_idx: Initial montage slice indices
        - threshold_range: Threshold range for threshold mapping
        - precision: Precision of the color mapping
        - slider_step_size: Stepsize of the sliders
    """
    data = nii_img.get_fdata()
    # Calculate global min and max
    data_min, data_max = get_minmax(data, 'nifti')
    # Calculate precision for slider step size
    precision = get_precision(data_range=data_max - data_min)
    # Get initial orthogonal view slice indices
    slice_len = {
        'x': int(data.shape[0]),
        'y': int(data.shape[1]),
        'z': int(data.shape[2])
    }
    ortho_slice_idx = get_init_ortho_slice_idx(slice_len)
    # Get initial montage slice indices
    montage_slice_idx_x = get_init_montage_slice_idx(slice_len, 'x')
    montage_slice_idx_y = get_init_montage_slice_idx(slice_len, 'y')
    montage_slice_idx_z = get_init_montage_slice_idx(slice_len, 'z')
    montage_slice_idx = {
        'x': montage_slice_idx_x,
        'y': montage_slice_idx_y,
        'z': montage_slice_idx_z
    }

    metadata: Dict[str, Union[float, List[int], Dict[str, int]]] = {
        'global_min': float(data_min),
        'global_max': float(data_max),
        'color_min': data_min,
        'color_max': data_max,
        'color_range': extend_color_range(data_min, data_max),
        'timepoints': list(range(data.shape[3])) if len(data.shape) > 3 else [0],
        'slice_len': slice_len,
        'x_slice_idx': ortho_slice_idx['x'],
        'y_slice_idx': ortho_slice_idx['y'],
        'z_slice_idx': ortho_slice_idx['z'],
        'montage_slice_idx': montage_slice_idx,
        'threshold_range': extend_color_range(data_min, data_max),
        'precision': precision,
        'slider_step_size': get_slider_step_size(
            metadata['color_range'][1] - metadata['color_range'][0],
            slider_steps,
            precision
        )
    }
    
    return metadata

