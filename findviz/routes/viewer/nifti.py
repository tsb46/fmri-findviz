"""
Nifti data handling
"""
from typing import Literal, Optional, TypedDict, List, Tuple

import nibabel as nib
import numpy as np

from nilearn.image import index_img

class SliceData(TypedDict):
    x: List[List[float]]
    y: List[List[float]]
    z: List[List[float]]

class CoordLabels(TypedDict):
    x: List[Tuple[int, int, int]]
    y: List[Tuple[int, int, int]]
    z: List[Tuple[int, int, int]]

class TimePointData(TypedDict):
    func: SliceData
    anat: Optional[SliceData]
    coord_labels: Optional[CoordLabels]


def get_nifti_data(
    time_point: int,
    func_img: nib.Nifti1Image,
    coord_labels: np.ndarray,
    x_slice: int,
    y_slice: int,
    z_slice: int,
    view_state: Literal['montage', 'ortho'],
    montage_slice_dir: Literal['x', 'y', 'z'],
    threshold_min: float = 0,
    threshold_max: float = 0,
    anat_img: Optional[nib.Nifti1Image] = None,
) -> TimePointData:
    """Get slice data for a specific timepoint from functional, anatomical and mask images.

    Parameters
    ----------
    time_point : int
        Index of the timepoint to extract from functional image
    func_img : nib.Nifti1Image
        4D functional image
    coord_labels : np.ndarray
        Array of voxel coordinates
    x_slice : int 
        Index for sagittal slice
    y_slice : int
        Index for coronal slice 
    z_slice : int
        Index for axial slice
    view_state : Literal['montage', 'ortho']
        Current view state of the viewer
    montage_slice_dir : Literal['x', 'y', 'z']
        Slice direction when in montage view
    anat_img : Optional[nib.Nifti1Image], optional
        3D anatomical image, by default None

    Returns
    -------
    Dict[str, Dict[str, List[List[float]]]]
        Dictionary containing slice data for each image type and axis:
        {
            'func': {'x': List[List[float]], 'y': List[List[float]], 'z': List[List[float]]},
            'anat': {'x': List[List[float]], 'y': List[List[float]], 'z': List[List[float]]},
            'mask': {'x': List[List[float]], 'y': List[List[float]], 'z': List[List[float]]},
            'coords': List[Tuple[int, int, int]]
        }
    """
    # Select time point
    func_data = index_img(func_img, time_point).get_fdata()
    
    # threshold data if threshold_min or threshold_max are provided
    if (threshold_min != 0) or (threshold_max != 0):
        func_data = threshold_nifti_data(
            func_data, threshold_min, threshold_max
        )

    # get anatomical data if present
    anat_data = anat_img.get_fdata() if anat_img else None
    
    # initialize output
    slice_out = {
        'func': {},
        'anat': {},
        'coords': {}
    }
    # Loop through axes and update
    for axis, slice_i in zip(['x', 'y', 'z'], [x_slice, y_slice, z_slice]):
        # set axis to all same direction, if montage
        if view_state == 'montage':
            nifti_axis = montage_slice_dir
        else:
            nifti_axis = axis
        slice_int = int(slice_i)
        slice_out['func'][axis] = get_slice_data(
            func_data, slice_int, axis=nifti_axis
        )
        if anat_data:
            slice_out['anat'][axis] = get_slice_data(
                anat_data, slice_int, axis=nifti_axis
            )
        # get coord labels
        slice_out['coords'][axis] = get_slice_data(
            coord_labels, slice_int, axis=nifti_axis
        )

    return slice_out


# Helper function to generate Plotly slice data
def get_slice_data(
    nifti_data: np.ndarray,
    slice_index: int, 
    axis: Literal['x', 'y', 'z']
) -> List[List[float]]:
    """Extract a 2D slice from a NIfTI image along a specified axis.

    Parameters
    ----------
    nifti_data : np.ndarray
        Input NIfTI data
    slice_index : int
        Index of the slice to extract
    axis : Literal['x', 'y', 'z']
        Axis along which to take the slice

    Returns
    -------
    2D numpy array containing the slice data, transposed for display
    """
    # Extract the slice data
    if axis == 'x':
        slice_data = np.squeeze(
            nifti_data[slice_index, :, :]
        ).transpose()
    elif axis == 'y':
        slice_data = np.squeeze(
            nifti_data[:, slice_index, :]
        ).transpose()
    elif axis == 'z':
        slice_data = np.squeeze(
            nifti_data[:, :, slice_index]
        ).transpose()

    return slice_data.tolist()


def get_timecourse_nifti(
    func_img: nib.Nifti1Image,
    x: int,
    y: int,
    z: int,
) -> Tuple[List[float], str]:
    """
    Get timecourse data and voxel label for a specific voxel 
    from a functional NIFTI file.

    Parameters
    ----------
    func_img : nib.Nifti1Image
        Functional NIFTI image
    x : int
        X-coordinate of the voxel
    y : int
        Y-coordinate of the voxel
    z : int
        Z-coordinate of the voxel
    """
    # create time course label
    time_course_label = f'Voxel: (x={x}, y={y}, z={z})'
    time_course = func_img.get_fdata()[x, y, z, :].tolist()
    return time_course, time_course_label


def threshold_nifti_data(
    nifti_data: np.ndarray,
    threshold_min: float,
    threshold_max: float,
) -> np.ndarray: 
    """Threshold a NIfTI 3d array

    Parameters
    ----------
    nifti_data : np.ndarray
        Nifti 3d array to threshold
    threshold_min : float
        Minimum threshold value
    threshold_max : float
        Maximum threshold value

    Returns
    -------
    np.ndarray
        Thresholded array. Voxels with values outside 
        the threshold range are set to 0.
    """
    # create mask
    mask = (nifti_data > threshold_min) & (nifti_data < threshold_max)
    # apply mask
    nifti_data[~mask] = 0
    return nifti_data

