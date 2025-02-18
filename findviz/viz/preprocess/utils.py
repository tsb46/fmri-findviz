"""
Utility functions for preprocessing
"""

from typing import List

import nibabel as nib
import numpy as np

from nilearn.image import smooth_img
from nilearn.signal import butterworth
from scipy.signal import detrend


def butterworth_filter(
    data: np.ndarray, 
    sf: float,
    low_cutoff: float, 
    high_cutoff: float, 
    order: int = 5
) -> np.ndarray:
    """
    Butterworth filter

    Arguments:
        data: np.ndarray
            Data to filter
        sf: float
            Sampling frequency
        low_cutoff: float
            Low cutoff frequency
        high_cutoff: float
            High cutoff frequency
        order: int
            Filter order. Default is 5
        axis: int
            Axis to filter along. Default is 0

    Returns:
        np.ndarray
            Filtered data
    """
    return butterworth(
        data, 
        sampling_rate=sf, 
        low_pass=high_cutoff, 
        high_pass=low_cutoff, 
        order=order
    )


def tr_to_hz(tr: float) -> float:
    """
    Convert TR to Hz

    Arguments:
        tr: float
            TR
    Returns:
        float
            Hz
    """
    return 1 / tr


def linear_detrend(data: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Linear detrending

    Arguments:
        data: np.ndarray
            Data to detrend
        axis: int
            Axis to detrend along. Default is 0
    Returns:
        np.ndarray
            Detrended data
    """
    return detrend(data, type='linear', axis=axis)


def mean_center(data: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Mean centering

    Arguments:
        data: np.ndarray
            Data to mean center
        axis: int
            Axis to mean center along. Default is 0
    Returns:
        np.ndarray
            Mean centered data
    """
    data_norm = data - data.mean(axis=axis, keepdims=True)
    return data_norm


def nifti_smooth(data: nib.Nifti1Image, fwhm: float) -> nib.Nifti1Image:
    """
    Smooth NIfTI image

    Arguments:
        data: nib.Nifti1Image
            NIfTI image to smooth
        fwhm: float
            FWHM
    Returns:
        nib.Nifti1Image
            Smoothed NIfTI image
    """
    return smooth_img(data, fwhm=fwhm)


def z_score(data: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Z-score normalization

    Arguments:
        data: np.ndarray
            Data to z-score normalize
        axis: int
            Axis to normalize along. Default is 0
    Returns:
        np.ndarray
            Z-score normalized data
    """
    data_norm = data - data.mean(axis=axis, keepdims=True)
    data_norm = data_norm / data_norm.std(axis=axis, keepdims=True)
    # handle constant values that return nan
    data_norm = np.nan_to_num(data_norm, copy=False, nan=0.0)
    return data_norm
