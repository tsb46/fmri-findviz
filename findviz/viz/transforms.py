"""
FMRI Data Transforms

Includes conversions between nifti/gifti image formats and numpy arrays and vice versa.

"""

from typing import Optional, Tuple

import nibabel as nib
import numpy as np

from nilearn import masking
from nibabel.gifti import GiftiDataArray

def array_to_nifti(
    array: np.ndarray, 
    affine: np.ndarray, 
    header: nib.Nifti1Header
) -> nib.Nifti1Image:
    """
    Convert numpy array to nibabel image

    Arguments:
    ----------
        array: numpy array
        affine: affine matrix
        header: nifti header
    
    Returns:
    --------
        nifti_img: nibabel image
    """
    return nib.Nifti1Image(array, affine, header)


def array_to_nifti_masked(array: np.ndarray, mask_img: nib.Nifti1Image) -> nib.Nifti1Image:
    """
    Convert 2d numpy array to nifti image

    Arguments:
    ----------
        array: 2d numpy array
        mask_img: mask nifti image (0 = exclude, 1 = include)
    
    Returns:
    --------
        nifti_img: nibabel image
    """
    nifti_img = masking.unmask(array, mask_img)
    return nifti_img


def nifti_to_array(nifti_img: nib.Nifti1Image) -> np.ndarray:
    """
    Convert nifti image to 3d or 4d numpy array

    Arguments:
    ----------
        nifti_img: nibabel image
    
    Returns:
    --------
        array: numpy array
    """ 
    return nifti_img.get_fdata()


def nifti_to_array_masked(nifti_img: nib.Nifti1Image, mask_img: nib.Nifti1Image) -> np.ndarray:
    """
    Convert nifti image to 2d numpy array. Voxels are arranged along columns 
    and time points along rows.

    Arguments:
    ----------
        nifti_img: nifti image
        mask_img: mask nifti image (0 = exclude, 1 = include)
    
    Returns:
    --------
        array: 2d numpy array
    """
    nifti_2d = masking.apply_mask(nifti_img, mask_img)
    return nifti_2d


def gifti_to_array(
    left_gifti: Optional[nib.GiftiImage] = None, 
    right_gifti: Optional[nib.GiftiImage] = None
) -> Tuple[np.ndarray, int]:
    """
    Convert gifti image to 2d numpy array. If both hemispheres are provided, 
    they are concatenated along the columns with left hemisphere first.
    The split index is returned as the second argument.
    """
    split_index = None
    if left_gifti is None and right_gifti is None:
        raise ValueError("No gifti images provided")
    
    if left_gifti is None:
        return _gifti_extract_data(right_gifti), split_index
    if right_gifti is None:
        return _gifti_extract_data(left_gifti), split_index
    
    # Get the length of left hemisphere data
    split_index = len(left_gifti.darrays[0].data)
    # Concatenate the data from both hemispheres
    concat_data = np.hstack([
        _gifti_extract_data(left_gifti),
        _gifti_extract_data(right_gifti)
    ])
    return concat_data, split_index


def array_to_gifti(
    array: np.ndarray,
    both_hemispheres: bool = False,
    split_index: Optional[int] = None
) -> Tuple[nib.GiftiImage, nib.GiftiImage] | nib.GiftiImage:
    """
    Convert 2d numpy array to gifti image. If both hemispheres are provided, 
    the array is split along the columns with left hemisphere first. If 
    both_hemispheres is False, the array is added to a single gifti image. If
    both_hemispheres is True, the split index is required.

    Arguments:
    ----------
        array: 2d numpy array (concatenated if both_hemispheres is True)
        both_hemispheres: whether to return both hemispheres
        split_index: split index. Required if both_hemispheres is True.
    
    Returns:
    --------
        gifti_img: nibabel gifti image (left or right) or both hemispheres - with
        left hemisphere first.

    """
    if both_hemispheres and split_index is None:
        raise ValueError("Split index is required for concatenated array")
    
    # create gifti images
    gifti_img = nib.GiftiImage()
    left_gifti = nib.GiftiImage()
    right_gifti = nib.GiftiImage()

    # loop over rows of array (row = time point)
    for row_i in range(array.shape[0]):
        if both_hemispheres:
            # split array into left and right hemispheres
            left_gifti.add_gifti_data_array(
                GiftiDataArray(array[row_i, :split_index], datatype=16)
            )
            right_gifti.add_gifti_data_array(
                GiftiDataArray(array[row_i, split_index:], datatype=16)
            )
        else:
            # add all rows to gifti image
            gifti_img.add_gifti_data_array(
                GiftiDataArray(array[row_i,:], datatype=16)
            )

    if both_hemispheres:
        return left_gifti, right_gifti
    else:
        return gifti_img


def _gifti_extract_data(gifti_img: nib.GiftiImage) -> np.ndarray:
    """
    Extract data from gifti image
    """
    gifti_data = np.vstack([darray.data for darray in gifti_img.darrays])
    return gifti_data


