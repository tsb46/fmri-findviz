"""Utility functions for processing neuroimaging data.

This module provides helper functions for processing NIFTI and GIFTI data,
including metadata extraction and value range calculations.

Functions:
    - apply_mask_nifti: Apply a mask to a NIfTI image
    - extend_color_range: Extend color range by a given percentage
    - get_coord_labels_gifti: Get coordinate labels for GIFTI data as a list of tuples
    - get_coord_labels_nifti: Get coordinate labels for NIFTI data as a 3D array
    - get_fmri_minmax: Calculate global minimum and maximum values for fmri data
    - get_ts_minmax: Calculate global minimum and maximum values for time series data
    - get_ortho_slice_coords: Get initial orthogonal view slice coordinates for NIFTI data
    - get_ortho_slice_idx: Get initial orthogonal view slice indices for NIFTI data
    - get_montage_slice_coords: Get initial montage slice coordinates for NIFTI data
    - get_montage_slice_idx: Get initial montage slice indices for NIFTI data
    - get_slider_step_size: Calculate slider step size
    - get_precision: Calculate precision for slider step size
    - package_distance_metadata: Package metadata for distance visualization
    - package_gii_metadata: Package metadata for GIFTI visualization
    - package_nii_metadata: Package metadata for NIFTI visualization
    - transform_to_world_coords: Transform voxel coordinates to world coordinates
    - requires_state: Decorator to check if state exists before executing method
"""
import decimal

from functools import wraps
from typing import Dict, Tuple, Union, Optional, List, Literal

import numpy as np
import nibabel as nib

from nibabel.gifti import GiftiImage
from nibabel.nifti1 import Nifti1Image

from findviz.logger_config import setup_logger

logger = setup_logger(__name__)

# define slice containers for nifti visualization
slices_containers = ['slice_1', 'slice_2', 'slice_3']

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
    nifti_data = nifti_img.get_fdata()
    mask_data = mask_img.get_fdata()
    nifti_data[mask_data == 0, :] = np.nan
    masked_img = nib.Nifti1Image(nifti_data, nifti_img.affine, nifti_img.header)
    return masked_img

def extend_color_range(
    color_min: float,
    color_max: float,
    extend_range: float = 0.25
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
    return color_min - (extend_range * abs(color_min)), color_max + (extend_range * abs(color_max))


def get_coord_labels_gifti(
    gifti_img: Optional[GiftiImage] = None,
    hemisphere: Optional[Literal['left', 'right']] = None
) -> List[Tuple[int, Literal['left', 'right']]]:
    """Get coordinate labels for GIFTI data as a list of tuples
    containing the vertex number and hemisphere for each vertex. If
    gifti_img is none, return None.

    Parameters
    ----------
    gifti_img : GiftiImage
        GIFTI image
    hemisphere : Literal['left', 'right']
        Hemisphere to get coordinate labels for

    Returns
    -------
    List[Tuple[int, Literal['left', 'right']]]
        List of tuples containing the vertex number and hemisphere for each vertex
    """
    if gifti_img is None:
        return None
    # get the vertex number and hemisphere for each vertex
    vertex_numbers = range(len(gifti_img.darrays[0].data))
    hemispheres = [hemisphere] * len(vertex_numbers)
    # create a list of tuples containing the vertex number and hemisphere for each vertex
    coord_labels = list(zip(vertex_numbers, hemispheres))
    return coord_labels


def get_coord_labels_nifti(
    nii_img: Nifti1Image
) -> np.ndarray:
    """Get coordinate labels for NIFTI data as a 3D array
    
    Parameters
    ----------
    nii_img : Nifti1Image
        Input NIFTI image
        
    Returns
    -------
    np.ndarray
        3D array of shape (X, Y, Z, 3) containing the coordinate indices
        for each voxel position
    """
    data = nii_img.get_fdata()
    shape = data.shape[:3]  # Get first 3 dimensions (X, Y, Z)
    
    # Create coordinate arrays for each dimension
    x_coords = np.arange(shape[0])[:, np.newaxis, np.newaxis]
    y_coords = np.arange(shape[1])[np.newaxis, :, np.newaxis]
    z_coords = np.arange(shape[2])[np.newaxis, np.newaxis, :]
    
    # Broadcast to full 3D arrays
    X = np.broadcast_to(x_coords, shape)
    Y = np.broadcast_to(y_coords, shape)
    Z = np.broadcast_to(z_coords, shape)
    
    # Stack the coordinates into a single array with shape (X, Y, Z, 3)
    coord_labels = np.stack([X, Y, Z], axis=-1)

    # Vectorize the string formatting function
    format_coord = np.vectorize(lambda x, y, z: f"Voxel: {x}, {y}, {z}")

    # Apply the formatting function to each coordinate
    coord_labels = format_coord(
        coord_labels[..., 0], 
        coord_labels[..., 1], 
        coord_labels[..., 2]
    )
    
    return coord_labels


def get_fmri_minmax(
    data: Union[np.ndarray, GiftiImage], 
    file_type: Literal['gifti', 'nifti']
) -> Tuple[float, float]:
    """Calculate global minimum and maximum values for fmri data.
    
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
        if slice == 'slice_1':
            ortho_slice_coords[slice] = {
                'x': ortho_slice_idx['y'],
                'y': ortho_slice_idx['z'],
            }
        # coronal slice
        elif slice == 'slice_2':
            ortho_slice_coords[slice] = {
                'x': ortho_slice_idx['x'],
                'y': ortho_slice_idx['z']
            }
        # axial slice
        elif slice == 'slice_3':
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
        x = ortho_slice_coords['slice_1']['x']
        y = ortho_slice_coords['slice_2']['y']
    elif montage_slice_dir == 'y':
        x = ortho_slice_coords['slice_2']['x']
        y = ortho_slice_coords['slice_3']['y']
    elif montage_slice_dir == 'z':
        x = ortho_slice_coords['slice_3']['x']
        y = ortho_slice_coords['slice_1']['y']

    montage_slice_coords = {}
    for slice in slices_containers:
        montage_slice_coords[slice] = {
            'x': x,
            'y': y,
        }
    return montage_slice_coords


def get_montage_slice_idx(
    slice_len: Dict[str, int],
    montage_slice_dir: Literal['x', 'y', 'z'],
    ortho_slice_idx: Dict[str, int]
) -> Dict[str, Dict[str, int]]:
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


def get_precision(
    data_range: float,
    max_precision: int = 6
) -> int:
    """Calculate precision for slider step size"""
    # Handle NaN values
    if np.isnan(data_range):
        return 0
        
    data_range_dec = decimal.Decimal(str(data_range))
    precision = abs(data_range_dec.as_tuple().exponent)
    if precision > max_precision:
        return max_precision
    return precision


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


def get_ts_minmax(
    default_min: float,
    default_max: float,
    ts_data: Optional[Dict[str, np.ndarray]] = None,
    task_data: Optional[Dict[str, np.ndarray]] = None
) -> Tuple[float, float]:
    """Calculate global minimum and maximum values for time series data. If 
    no ts data or task data is provided, return default_min and default_max.
    
    Parameters:
    -----------
    default_min: Default minimum value
    default_max: Default maximum value
    ts_data: Dictionary containing time series data
    task_data: Dictionary containing task data
    
    Returns:
    --------
    Tuple containing (global_minimum, global_maximum)
    """
    ts_min = np.nan
    ts_max = np.nan
    task_min = np.nan
    task_max = np.nan

    if ts_data is not None:
        ts_min = float(np.nanmin([ts_data[ts] for ts in ts_data]))
        ts_max = float(np.nanmax([ts_data[ts] for ts in ts_data]))

    if task_data is not None:
        task_min = float(np.nanmin([task_data[task] for task in task_data]))
        task_max = float(np.nanmax([task_data[task] for task in task_data]))

    global_min = float(np.nanmin([ts_min, task_min]))
    global_max = float(np.nanmax([ts_max, task_max]))

    if np.isnan(global_min):
        global_min = default_min
    if np.isnan(global_max):
        global_max = default_max

    return global_min, global_max


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
        global_min_left, global_max_left = get_fmri_minmax(left_img, 'gifti')
        timepoints = list(range(len(left_img.darrays)))
        
    if right_img is not None:
        global_min_right, global_max_right = get_fmri_minmax(right_img, 'gifti')
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
    data_min, data_max = get_fmri_minmax(data, 'nifti')
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


def transform_to_world_coords(
    voxel_coords: Dict[Literal['x', 'y', 'z'], int],
    affine: np.ndarray
) -> Tuple[float, float, float]:
    """Transform voxel coordinates to world coordinates.
    
    Parameters:
    -----------
    voxel_coords: Dictionary of x,y,z voxel coordinates
    affine: Affine matrix
    
    Returns:
    --------
    Tuple of x,y,z world coordinates
    """
    coords_array = np.array(
        [voxel_coords['x'], voxel_coords['y'], voxel_coords['z'], 1]
    )
    return np.dot(affine, coords_array)[:3]


def requires_state(func):
    """Decorator to check if state exists before executing method.
    
    Checks if self._state has been initialized before executing the decorated method.
    If no state exists, logs an error and returns None.
    """
    # For regular methods
    if not isinstance(func, property):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._state:
                logger.error(f"No state exists. Must call create_nifti_state or create_gifti_state before {func.__name__}")
                return None
            return func(self, *args, **kwargs)
        return wrapper
    
    # For properties
    else:
        @property
        @wraps(func)
        def wrapper(self):
            if not self._state:
                logger.error(f"No state exists. Must call create_nifti_state or create_gifti_state before {func.fget.__name__}")
                return None
            return func.fget(self)
        return wrapper



