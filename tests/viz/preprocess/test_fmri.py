"""Tests for fMRI preprocessing utilities"""
import pytest
import numpy as np
import nibabel as nib
from nibabel.gifti import GiftiImage, GiftiDataArray

from findviz.viz.preprocess.fmri import (
    preprocess_fmri,
    PreprocessFMRIInputs
)
from findviz.viz.exception import NiftiMaskError


@pytest.fixture
def mock_nifti_4d():
    """Create a mock 4D NIFTI image for testing"""
    # Create random 4D data (5x5x5x100)
    data = np.random.rand(5, 5, 5, 100)
    return nib.Nifti1Image(data, np.eye(4))


@pytest.fixture
def mock_nifti_mask():
    """Create a mock NIFTI mask for testing"""
    # Create binary mask (5x5x5)
    mask = np.ones((5, 5, 5))
    mask[0:2, 0:2, 0:2] = 0  # Set half the voxels to 0
    return nib.Nifti1Image(mask, np.eye(4))


@pytest.fixture
def mock_gifti_func():
    """Create a mock GIFTI functional image for testing"""
    # Create 100 random arrays of length 100
    data_arrays = []
    for _ in range(100):
        data = np.random.rand(100).astype(np.float32)
        darray = GiftiDataArray(data)
        data_arrays.append(darray)
    return GiftiImage(darrays=data_arrays)


@pytest.fixture
def default_inputs():
    """Create default preprocessing inputs"""
    return PreprocessFMRIInputs(
        normalize=False,
        filter=True,
        smooth=False,
        detrend=True,
        mean_center=True,
        zscore=True,
        tr=2.0,
        low_cut=0.01,
        high_cut=0.1,
        fwhm=6.0
    )


def test_preprocess_nifti_basic(mock_nifti_4d, mock_nifti_mask, default_inputs):
    """Test basic NIFTI preprocessing with default parameters"""
    processed_img = preprocess_fmri(
        file_type='nifti',
        inputs=default_inputs,
        func_img=mock_nifti_4d,
        mask_img=mock_nifti_mask
    )
    
    assert isinstance(processed_img, nib.Nifti1Image)
    assert processed_img.shape == mock_nifti_4d.shape


def test_preprocess_gifti_basic(mock_gifti_func, default_inputs):
    """Test basic GIFTI preprocessing with default parameters"""
    left_processed, right_processed = preprocess_fmri(
        file_type='gifti',
        inputs=default_inputs,
        left_func_img=mock_gifti_func,
        right_func_img=mock_gifti_func
    )
    
    assert isinstance(left_processed, GiftiImage)
    assert isinstance(right_processed, GiftiImage)
    assert len(left_processed.darrays) == len(mock_gifti_func.darrays)
    assert len(right_processed.darrays) == len(mock_gifti_func.darrays)


def test_preprocess_nifti_no_mask(mock_nifti_4d, default_inputs):
    """Test NIFTI preprocessing fails without mask"""
    with pytest.raises(NiftiMaskError):
        preprocess_fmri(
            file_type='nifti',
            inputs=default_inputs,
            func_img=mock_nifti_4d,
            mask_img=None
        )


def test_preprocess_gifti_single_hemisphere(mock_gifti_func, default_inputs):
    """Test GIFTI preprocessing with single hemisphere"""
    # Test left hemisphere only
    left_processed, right_processed = preprocess_fmri(
        file_type='gifti',
        inputs=default_inputs,
        left_func_img=mock_gifti_func,
        right_func_img=None
    )
    
    assert isinstance(left_processed, GiftiImage)
    assert right_processed is None
    
    # Test right hemisphere only
    left_processed, right_processed = preprocess_fmri(
        file_type='gifti',
        inputs=default_inputs,
        left_func_img=None,
        right_func_img=mock_gifti_func
    )
    
    assert left_processed is None
    assert isinstance(right_processed, GiftiImage)


def test_preprocess_gifti_with_smoothing(mock_gifti_func, default_inputs):
    """Test GIFTI preprocessing with smoothing raises NotImplementedError"""
    inputs = default_inputs.copy()
    inputs['smooth'] = True
    
    with pytest.raises(NotImplementedError):
        preprocess_fmri(
            file_type='gifti',
            inputs=inputs,
            left_func_img=mock_gifti_func,
            right_func_img=mock_gifti_func
        )


def test_preprocess_nifti_with_smoothing(mock_nifti_4d, mock_nifti_mask):
    """Test NIFTI preprocessing with smoothing"""
    inputs = PreprocessFMRIInputs(
        normalize=False,
        filter=False,
        smooth=True,
        detrend=False,
        mean_center=False,
        zscore=False,
        tr=2.0,
        low_cut=0.01,
        high_cut=0.1,
        fwhm=6.0
    )
    
    processed_img = preprocess_fmri(
        file_type='nifti',
        inputs=inputs,
        func_img=mock_nifti_4d,
        mask_img=mock_nifti_mask
    )
    
    assert isinstance(processed_img, nib.Nifti1Image)
    assert processed_img.shape == mock_nifti_4d.shape
