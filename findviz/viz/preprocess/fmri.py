"""
Preprocessing functions for functional MRI data
"""

from typing import Literal, Optional, TypedDict

import nibabel as nib

from findviz.viz.preprocess import utils

class PreprocessFMRIInputs(TypedDict):
    """
    Inputs for preprocess_fmri
    """
    detrend: bool
    zscore: bool
    filter: bool
    smooth: bool
    tr: float
    lowpass: float
    highpass: float
    order: int
    fwhm: float


def preprocess_fmri(
        file_type: Literal['nifti', 'gifti'],
        inputs: PreprocessFMRIInputs,
        func_img: Optional[nib.Nifti1Image] = None,
        left_img: Optional[nib.GiftiImage] = None,
        right_img: Optional[nib.GiftiImage] = None,
) -> nib.Nifti1Image:
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
        left_img: nib.GiftiImage
            Gifti image containing left hemisphere functional data. Only required if file_type is 'gifti'
        right_img: nib.GiftiImage
            Gifti image containing right hemisphere functional data. Only required if file_type is 'gifti'
    """
    if file_type == 'nifti' and func_img is None:
        raise ValueError("func_img is required if file_type is 'nifti'")
    elif file_type == 'gifti' and (left_img is None or right_img is None):
        raise ValueError("left_img and right_img are required if file_type is 'gifti'")

    if inputs['detrend']:
        func_img = utils.detrend(func_img)

    if inputs['zscore']:
        func_img = utils.zscore(func_img)

    if inputs['filter']:
        # convert tr to hz
        tr_hz = utils.tr_to_hz(inputs['tr'])
        func_img = utils.butterworth_filter(
            func_img, 
            tr_hz, 
            inputs['lowpass'], 
            inputs['highpass'], 
            inputs['order']
        )

    if inputs['smooth']:
        if file_type == 'nifti':
            func_img = utils.nifti_smooth(func_img, inputs['fwhm'])
        elif file_type == 'gifti':
            raise NotImplementedError("Smoothing is not supported for Gifti files")
    
