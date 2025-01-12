"""
Preprocessing functions for functional MRI data
"""

from typing import Literal, Optional, TypedDict, Tuple

import nibabel as nib

from findviz.viz.transforms import (
    array_to_gifti, gifti_to_array, 
    nifti_to_array_masked, array_to_nifti_masked,
)
from findviz.viz.preprocess import utils
from findviz.viz.exception import NiftiMaskError


class PreprocessFMRIInputs(TypedDict):
    """
    Inputs for preprocess_fmri
    """
    detrend: bool
    mean_center: bool
    zscore: bool
    filter: bool
    smooth: bool
    tr: float
    lowpass: float
    highpass: float
    fwhm: float


def preprocess_fmri(
    file_type: Literal['nifti', 'gifti'],
    inputs: PreprocessFMRIInputs,
    func_img: Optional[nib.Nifti1Image] = None,
    mask_img: Optional[nib.Nifti1Image] = None,
    left_func_img: Optional[nib.GiftiImage] = None,
    right_func_img: Optional[nib.GiftiImage] = None,
) -> nib.Nifti1Image | Tuple[nib.GiftiImage, nib.GiftiImage]:
    """
    Preprocess functional MRI data

    Arguments:
    ----------
        file_type: Literal['nifti', 'gifti']
            Type of file to preprocess
        inputs: PreprocessFMRIInputs
            Inputs for preprocess_fmri
        func_img: nib.Nifti1Image
            NIfTI image to preprocess. Only required if file_type is 'nifti'
        mask_img: nib.Nifti1Image
            Mask image to use for preprocessing. 
            Only required if file_type is 'nifti'
        left_img: nib.GiftiImage
            Gifti image containing left hemisphere functional data. 
            Only required if file_type is 'gifti'
        right_img: nib.GiftiImage
            Gifti image containing right hemisphere functional data. 
            Only required if file_type is 'gifti'
        
    Returns:
    --------
        nib.Nifti1Image | Tuple[nib.GiftiImage, nib.GiftiImage]
            Preprocessed functional MRI data. Either a single nib.Nifti1Image, 
            or a tuple of nib.GiftiImage objects (left and right hemispheres).
    """
    if file_type == 'nifti' and func_img is None:
        raise ValueError("func_img is required if file_type is 'nifti'")
    elif file_type == 'gifti' and (left_func_img is None or right_func_img is None):
        raise ValueError(
            "left_func_img or right_func_img are required if file_type is 'gifti'"
        )

    # check if mask is provided for nifti processing
    if file_type == 'nifti' and mask_img is None:
        raise NiftiMaskError(
            message="Mask is required for nifti preprocessing",
        )

    # convert functional image to array
    if file_type == 'nifti':
        func_array = nifti_to_array_masked(func_img, mask_img)
    elif file_type == 'gifti':
        if left_func_img is not None and right_func_img is not None:
            both_hemispheres = True
        else:
            both_hemispheres = False
        func_array, split_index = gifti_to_array(
            left_func_img, right_func_img
        )

    # linear detrend
    if inputs['detrend']:
        func_array = utils.linear_detrend(func_array)

     # butterworth filter
    if inputs['filter']:
        # convert tr to hz
        tr_hz = utils.tr_to_hz(inputs['tr'])
        func_array = utils.butterworth_filter(
            func_array, 
            tr_hz, 
            inputs['lowpass'], 
            inputs['highpass'], 
        )

    # mean center
    if inputs['mean_center']:
        func_array = utils.mean_center(func_array)

    # zscore
    if inputs['zscore']:
        func_array = utils.z_score(func_array)

    # 3d gaussian smooth (only for nifti)
    if inputs['smooth']:
        if file_type == 'nifti':
            func_array = utils.nifti_smooth(func_array, inputs['fwhm'])
        elif file_type == 'gifti':
            raise NotImplementedError("Smoothing is not supported for Gifti files")

    # convert array back to nifti or gifti
    if file_type == 'nifti':
        func_img_prep = array_to_nifti_masked(func_array, mask_img)
        return func_img_prep
    elif file_type == 'gifti':
        left_func_img_prep = None
        right_func_img_prep = None
        # if both hemispheres are provided, split the array
        left_gii, right_gii = array_to_gifti(func_array, both_hemispheres, split_index)        
        # if only one hemisphere is provided, assign the array to left or right
        if left_func_img is not None:
            left_func_img_prep = left_gii
        elif right_func_img is not None:
            right_func_img_prep = right_gii

        return left_func_img_prep, right_func_img_prep


