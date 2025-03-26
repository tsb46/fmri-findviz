"""Tests for neuroimaging data format transformations"""
import pytest
import numpy as np
import nibabel as nib
from unittest.mock import MagicMock

from nibabel.gifti import GiftiImage

from findviz.viz.transforms import (
    array_to_nifti,
    array_to_nifti_masked,
    nifti_to_array,
    nifti_to_array_masked,
    gifti_to_array,
    array_to_gifti
)

def test_array_to_nifti():
    """Test converting numpy array to NIFTI image"""
    # Create test data
    array = np.random.rand(10, 10, 10)
    affine = np.eye(4)
    header = nib.Nifti1Header()
    
    # Convert to NIFTI
    nifti_img = array_to_nifti(array, affine, header)
    
    assert isinstance(nifti_img, nib.Nifti1Image)
    np.testing.assert_array_equal(nifti_img.get_fdata(), array)
    np.testing.assert_array_equal(nifti_img.affine, affine)

def test_array_to_nifti_masked(mock_nifti_3d):
    """Test converting 2D array to masked NIFTI image"""
    # Create mask and apply it to get 2D array
    mask = np.zeros((10, 10, 10))
    mask[2:8, 2:8, 2:8] = 1
    mask_img = nib.Nifti1Image(mask, np.eye(4))
    
    # Create 2D array that matches mask size
    n_voxels = int(mask.sum())
    array_2d = np.random.rand(n_voxels)
    
    # Convert back to 3D NIFTI
    nifti_img = array_to_nifti_masked(array_2d, mask_img)
    
    assert isinstance(nifti_img, nib.Nifti1Image)
    assert nifti_img.shape == mask_img.shape

def test_nifti_to_array(mock_nifti_4d):
    """Test converting NIFTI image to numpy array"""
    array = nifti_to_array(mock_nifti_4d)
    
    assert isinstance(array, np.ndarray)
    assert array.shape == mock_nifti_4d.shape
    np.testing.assert_array_equal(array, mock_nifti_4d.get_fdata())

def test_nifti_to_array_masked(mock_nifti_4d):
    """Test converting NIFTI image to masked 2D array"""
    # Create mask
    mask = np.zeros(mock_nifti_4d.shape[:3])
    mask[2:8, 2:8, 2:8] = 1
    mask_img = nib.Nifti1Image(mask, mock_nifti_4d.affine)
    
    # Convert to 2D array
    array_2d = nifti_to_array_masked(mock_nifti_4d, mask_img)
    
    assert isinstance(array_2d, np.ndarray)
    assert len(array_2d.shape) == 2
    assert array_2d.shape[0] == mock_nifti_4d.shape[3]  # Time points
    assert array_2d.shape[1] == int(mask.sum())  # Masked voxels

def test_gifti_to_array_single_hemisphere(mock_gifti_func):
    """Test converting single hemisphere GIFTI to array"""
    # Create mock data array
    mock_darray = MagicMock()
    mock_darray.data = np.random.rand(100)  # 100 vertices
    mock_gifti_func.darrays = [mock_darray]
    
    # Test left hemisphere only
    array_left, split_idx = gifti_to_array(left_gifti=mock_gifti_func)
    assert isinstance(array_left, np.ndarray)
    assert array_left.shape == (1, 100)  # Should be 2D: 1 timepoint x 100 vertices
    assert split_idx is None
    
    # Test right hemisphere only
    array_right, split_idx = gifti_to_array(right_gifti=mock_gifti_func)
    assert isinstance(array_right, np.ndarray)
    assert array_right.shape == (1, 100)
    assert split_idx is None

def test_gifti_to_array_both_hemispheres(mock_gifti_func):
    """Test converting both hemisphere GIFTIs to array"""
    # Create mock data arrays
    mock_darray_left = MagicMock()
    mock_darray_left.data = np.random.rand(100)  # 100 vertices
    mock_gifti_left = MagicMock(spec=GiftiImage)
    mock_gifti_left.darrays = [mock_darray_left]
    
    mock_darray_right = MagicMock()
    mock_darray_right.data = np.random.rand(100)  # 100 vertices
    mock_gifti_right = MagicMock(spec=GiftiImage)
    mock_gifti_right.darrays = [mock_darray_right]
    
    array, split_idx = gifti_to_array(
        left_gifti=mock_gifti_left,
        right_gifti=mock_gifti_right
    )
    
    assert isinstance(array, np.ndarray)
    assert array.shape == (1, 200)  # 1 timepoint x 200 combined vertices
    assert isinstance(split_idx, int)
    assert split_idx == 100  # Split at 100 vertices

def test_gifti_to_array_no_input():
    """Test gifti_to_array with no input"""
    with pytest.raises(ValueError, match="No gifti images provided"):
        gifti_to_array()

def test_array_to_gifti_single():
    """Test converting array to single GIFTI image"""
    array = np.random.rand(5, 100)  # 5 timepoints, 100 vertices
    
    gifti_img = array_to_gifti(array, both_hemispheres=False)
    
    assert isinstance(gifti_img, GiftiImage)
    assert len(gifti_img.darrays) == array.shape[0]  # One darray per timepoint
    for i in range(array.shape[0]):
        np.testing.assert_array_equal(
            gifti_img.darrays[i].data,
            array[i,:]
        )

def test_array_to_gifti_both_hemispheres():
    """Test converting array to both hemisphere GIFTI images"""
    array = np.random.rand(5, 200)  # 5 timepoints, 200 vertices total
    split_idx = 100  # Split at midpoint
    
    left_gifti, right_gifti = array_to_gifti(
        array,
        both_hemispheres=True,
        split_index=split_idx
    )
    
    assert isinstance(left_gifti, GiftiImage)
    assert isinstance(right_gifti, GiftiImage)
    
    # Check number of time points
    assert len(left_gifti.darrays) == array.shape[0]
    assert len(right_gifti.darrays) == array.shape[0]
    
    # Check data was split correctly for each timepoint
    for i in range(array.shape[0]):
        np.testing.assert_array_equal(
            left_gifti.darrays[i].data,
            array[i,:split_idx]
        )
        np.testing.assert_array_equal(
            right_gifti.darrays[i].data,
            array[i,split_idx:]
        )

def test_array_to_gifti_missing_split_index():
    """Test array_to_gifti with missing split index"""
    array = np.random.rand(5, 100)
    
    with pytest.raises(ValueError, match="Split index is required"):
        array_to_gifti(array, both_hemispheres=True)
