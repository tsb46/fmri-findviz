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

from findviz.viz.viewer.types import SliceIndexDict
from findviz.logger_config import setup_logger

logger = setup_logger(__name__)

# define slice containers for nifti visualization
slices_containers = ['slice1', 'slice2', 'slice3']

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


def get_ortho_slice_coords(
    ortho_slice_idx: Dict[str, int]
) -> Dict[str, Dict[str, int]]:
    """Get initial orthogonal view slice coordinates for 
    NIFTI data as middle of x,y,z dimensions

    Parameters:
    -----------
    ortho_slice_idx: Dictionary containing x,y,z slice indices
    
    Returns:
    --------
    Dictionary containing x,y,z slice coordinates
    """
    ortho_slice_coords = {}
    for slice in slices_containers:
        # saggital slice
        if slice == 'slice1':
            ortho_slice_coords[slice] = {
                'x': ortho_slice_idx['z'],
                'y': ortho_slice_idx['x'],
            }
        # coronal slice
        elif slice == 'slice2':
            ortho_slice_coords[slice] = {
                'x': ortho_slice_idx['x'],
                'y': ortho_slice_idx['z']
            }
        # axial slice
        elif slice == 'slice3':
            ortho_slice_coords[slice] = {
                'x': ortho_slice_idx['x'],
                'y': ortho_slice_idx['y']
            }
    return ortho_slice_coords

def get_ortho_slice_idx(slice_len: Dict[str, int]) -> Dict[str, int]:
    """Get orthogonal view slice indices for NIFTI data. Set as middle of x,y,z dimensions
    
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

def get_montage_slice_coords(
    ortho_slice_coords: Dict[str, Dict[str, int]],
    montage_slice_dir: Literal['x', 'y', 'z']
) -> Dict[str, Dict[str, int]]:
    """Get montage slice coordinates for NIFTI data for a given montage slice direction 
    from orthogonal slice coordinates. Initialize montage click coordinates with 
    orthogonal slice coordinates for the corresponding slice direction.

    Parameters:
    -----------
    ortho_slice_coords: Dictionary containing x, y slice coordinates for orthogonal view
    montage_slice_dir: Direction of montage slices

    Returns:
    --------
    Dictionary containing x, y click coordinates for montage view
    """
    if montage_slice_dir == 'x':
        montage_slice_coords = {
            'x': ortho_slice_coords['slice1']['x'],
            'y': ortho_slice_coords['slice1']['y'],
        }
    elif montage_slice_dir == 'y':
        montage_slice_coords = {
            'x': ortho_slice_coords['slice2']['x'],
            'y': ortho_slice_coords['slice2']['y'],
        }
    elif montage_slice_dir == 'z':
        montage_slice_coords = {
            'x': ortho_slice_coords['slice3']['x'],
            'y': ortho_slice_coords['slice3']['y'],
        }
    return montage_slice_coords

def get_montage_slice_idx(
    slice_len: Dict[str, int],
    montage_slice_dir: Literal['x', 'y', 'z'],
    ortho_slice_idx: Dict[str, int]
) -> SliceIndexDict:
    """Get initial montage slice indices for NIFTI data as 
    equally distributed across the slice direction (montage_slice_dir). 
    The montage slice indices are initialized with the slice indices
    for each slice direction, and placed at 33%, 50%, and 66% of the slice length
    in the montage slice direction.

    Parameters:
    -----------
    slice_len: Dictionary containing x,y,z dimensions
    montage_slice_dir: Direction of montage slices
    ortho_slice_idx: Dictionary containing x,y,z slice indices

    Returns:
    --------
    Dictionary containing montage slice indices
    """
    # percentage of slice length to start montage slice at
    slice_len_dir = slice_len[montage_slice_dir]
    montage_slice_perc = [0.33, 0.5, 0.66]
    montage_slice_idx = {}
    for perc, slice in zip(montage_slice_perc, slices_containers):
        slice_idx_dir = int(slice_len_dir * perc)
        # initialize montage slice indices with orthogonal slice indices
        montage_slice_idx[slice] = {
            'x': ortho_slice_idx['x'],
            'y': ortho_slice_idx['y'],
            'z': ortho_slice_idx['z']
        }
        # set montage slice index for current slice direction
        montage_slice_idx[slice][montage_slice_dir] = slice_idx_dir

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


def package_distance_metadata(
    distance_data: np.ndarray,
    slider_steps: int = 100,
    precision: int = 6
) -> Dict[str, Union[float, List[int]]]:
    """Package metadata for distance visualization.
    
    Parameters:
    -----------
    distance_data: Distance data
    slider_steps: Number of steps in slider
    precision: Precision of step size
    
    Returns:
    --------
    Dictionary containing:
        - color_min: Minimum value for color mapping
        - color_max: Maximum value for color mapping
        - color_range: Color range for color mapping
        - precision: Precision of the color mapping
        - slider_step_size: Stepsize of the sliders
    """
    # Calculate precision for slider step size
    precision = get_precision(
        data_range=distance_data.max() - distance_data.min()
    )
    metadata: Dict[str, Union[float, List[int]]] = {
        'color_min': distance_data.min(),
        'color_max': distance_data.max(),
        'color_range': extend_color_range(
            distance_data.min(),
            distance_data.max()
        ),
        'precision': precision,
    }
    metadata['slider_step_size'] = get_slider_step_size(
        metadata['color_range'][1] - metadata['color_range'][0],
        slider_steps,
        metadata['precision']
    )
    return metadata


def package_gii_metadata(
    left_img: Optional[GiftiImage],
    right_img: Optional[GiftiImage],
    slider_steps: int = 100,
    precision: int = 6
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
        - color_min: Minimum value for color mapping
        - color_max: Maximum value for color mapping
        - color_range: Color range for color mapping
        - precision: Precision of the color mapping
        - slider_step_size: Stepsize of the sliders
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
    slider_steps: int = 100,
    precision: int = 6
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
        - ortho_slice_idx: Dictionary of x,y,z slice indices for orthogonal view
        - ortho_slice_coords: Dictionary of x,y,z slice coordinates for orthogonal view
        - montage_slice_idx: Dictionary of x,y,z slice indices for montage view
        - montage_slice_coords: Dictionary of x,y,z slice coordinates for montage view
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
    # Get initial orthogonal view slice indices
    ortho_slice_idx = get_ortho_slice_idx(slice_len)
    # Get initial orthogonal view slice coordinates
    ortho_slice_coords = get_ortho_slice_coords(ortho_slice_idx)
    # Get initial montage slice indices
    montage_slice_idx_x = get_montage_slice_idx(slice_len, 'x', ortho_slice_idx)
    montage_slice_idx_y = get_montage_slice_idx(slice_len, 'y', ortho_slice_idx)
    montage_slice_idx_z = get_montage_slice_idx(slice_len, 'z', ortho_slice_idx)
    montage_slice_idx = {
        'x': montage_slice_idx_x,
        'y': montage_slice_idx_y,
        'z': montage_slice_idx_z
    }
    # Get initial montage slice coordinates
    montage_slice_coords_x = get_montage_slice_coords(ortho_slice_coords, 'x')
    montage_slice_coords_y = get_montage_slice_coords(ortho_slice_coords, 'y')
    montage_slice_coords_z = get_montage_slice_coords(ortho_slice_coords, 'z')
    montage_slice_coords = {
        'x': montage_slice_coords_x,
        'y': montage_slice_coords_y,
        'z': montage_slice_coords_z
    }

    metadata: Dict[str, Union[float, List[int], Dict[str, int]]] = {
        'global_min': float(data_min),
        'global_max': float(data_max),
        'color_min': data_min,
        'color_max': data_max,
        'color_range': extend_color_range(data_min, data_max),
        'timepoints': list(range(data.shape[3])) if len(data.shape) > 3 else [0],
        'slice_len': slice_len,
        'ortho_slice_idx': ortho_slice_idx,
        'ortho_slice_coords': ortho_slice_coords,
        'montage_slice_idx': montage_slice_idx,
        'montage_slice_coords': montage_slice_coords,
        'threshold_range': extend_color_range(data_min, data_max),
        'precision': precision,
        'slider_step_size': get_slider_step_size(
            data_max - data_min,
            slider_steps,
            precision
        )
    }
    
    return metadata


def requires_state(func):
    """Decorator to check if state exists before executing method.
    
    Checks if self._state has been initialized before executing the decorated method.
    If no state exists, logs an error and returns None.
    """
    def wrapper(self, *args, **kwargs):
        if not self._state:
            logger.error(f"No state exists. Must call create_nifti_state or create_gifti_state before {func.__name__}")
            return None
        return func(self, *args, **kwargs)
    return wrapper

