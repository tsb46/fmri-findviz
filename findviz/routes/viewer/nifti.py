"""
Nifti data handling
"""
from typing import Literal, Optional, TypedDict, List, Tuple

import nibabel as nib
import numpy as np

from nilearn.image import index_img

class SliceData(TypedDict):
    x: np.ndarray
    y: np.ndarray 
    z: np.ndarray

class VoxelCoords(TypedDict):
    x: List[List[Tuple[int, int, int]]]
    y: List[List[Tuple[int, int, int]]]
    z: List[List[Tuple[int, int, int]]]

class TimePointData(TypedDict):
    func: SliceData
    anat: SliceData
    mask: SliceData
    coords: VoxelCoords


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


def get_nifti_timepoint_data(
    time_point: int,
    func_img: nib.Nifti1Image, 
    x_slice: int,
    y_slice: int,
    z_slice: int,
    view_state: Literal['montage', 'ortho'],
    montage_slice_dir: Literal['x', 'y', 'z'],
    anat_img: Optional[nib.Nifti1Image] = None,
    mask_img: Optional[nib.Nifti1Image] = None,
    update_voxel_coord: bool = False
) -> TimePointData:
    """Get slice data for a specific timepoint from functional, anatomical and mask images.

    Parameters
    ----------
    time_point : int
        Index of the timepoint to extract from functional image
    func_img : nib.Nifti1Image
        4D functional image
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
    mask_img : Optional[nib.Nifti1Image], optional
        3D mask image, by default None
    update_voxel_coord : bool, optional
        Whether to include voxel coordinates in output, by default False

    Returns
    -------
    Dict[str, Dict[str, Union[np.ndarray, List[List[Tuple[int, int, int]]]]]]
        Dictionary containing slice data for each image type and axis:
        {
            'func': {'x': array, 'y': array, 'z': array},
            'anat': {'x': array, 'y': array, 'z': array},
            'mask': {'x': array, 'y': array, 'z': array},
            'coords': {'x': [[(i,j,k)]], 'y': [[(i,j,k)]], 'z': [[(i,j,k)]]}
        }
    """
    # Select time point
    func_img_t = index_img(func_img, time_point)
    # initialize output
    slice_out = {
        'func': {},
        'anat': {},
        'mask': {},
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
            func_img_t, slice_int, axis=nifti_axis
        )
        if anat_img:
            slice_out['anat'][axis] = get_slice_data(
                anat_img, slice_int, axis=nifti_axis
            )
        if mask_img:
            slice_out['mask'][axis] = get_slice_data(
                mask_img, slice_int, axis=nifti_axis
            )
        if update_voxel_coord:
            slice_out['coords'][axis] = [
                [(slice_int, j, i)
                for j in range(slice_out['func'][axis].shape[1])]
                for i in range(slice_out['func'][axis].shape[0])
            ]
    return slice_out


# Helper function to generate Plotly slice data
def get_slice_data(
    nifti_img: nib.Nifti1Image,
    slice_index: int, 
    axis: Literal['x', 'y', 'z']
) -> List[List[float]]:
    """Extract a 2D slice from a NIfTI image along a specified axis.

    Args:
        nifti_img: Input NIfTI image object
        slice_index: Index of the slice to extract
        axis: Axis along which to take the slice ('x', 'y', or 'z')

    Returns:
        2D numpy array containing the slice data, transposed for display
    """
    # Extract the slice data
    if axis == 'x':
        slice_data = np.squeeze(
            nifti_img.get_fdata()[slice_index, :, :]
        ).transpose()
    elif axis == 'y':
        slice_data = np.squeeze(
            nifti_img.get_fdata()[:, slice_index, :]
        ).transpose()
        # flip for radiological
        # slice_data = np.flip(slice_data, axis=1)
    elif axis == 'z':
        slice_data = np.squeeze(
            nifti_img.get_fdata()[:, :, slice_index]
        ).transpose()

    return slice_data.tolist()
