"""Tests for viewer utility functions"""
import pytest
import numpy as np
import nibabel as nib
from nibabel.gifti import GiftiImage, GiftiDataArray

from findviz.viz.viewer.utils import (
    get_minmax,
    package_gii_metadata,
    package_nii_metadata,
    apply_mask_nifti,
    get_coord_labels
)

def test_get_minmax_nifti():
    """Test getting min/max values from NIFTI data"""
    # Create test data with known min/max
    data = np.array([[-1.0, 0.0], [1.0, 2.0]])
    min_val, max_val = get_minmax(data, 'nifti')
    
    assert min_val == -1.0
    assert max_val == 2.0

def test_get_minmax_nifti_with_nan():
    """Test getting min/max values from NIFTI data with NaN values"""
    data = np.array([[-1.0, np.nan], [1.0, 2.0]])
    min_val, max_val = get_minmax(data, 'nifti')
    
    assert min_val == -1.0
    assert max_val == 2.0

def test_get_minmax_gifti(mock_gifti_func):
    """Test getting min/max values from GIFTI data"""
    min_val, max_val = get_minmax(mock_gifti_func, 'gifti')
    
    # Values should be within expected range (0 to 1 from random data)
    assert 0 <= min_val <= 1
    assert 0 <= max_val <= 1
    assert min_val <= max_val

def test_get_minmax_invalid_type():
    """Test get_minmax with invalid file type"""
    data = np.array([1, 2, 3])
    with pytest.raises(ValueError, match="file_type must be 'gifti' or 'nifti'"):
        get_minmax(data, 'invalid')

def test_get_minmax_invalid_data_type():
    """Test get_minmax with invalid data type"""
    with pytest.raises(TypeError, match="NIFTI data must be numpy array"):
        get_minmax("not an array", 'nifti')
    
    with pytest.raises(TypeError, match="GIFTI data must be GiftiImage"):
        get_minmax(np.array([1, 2, 3]), 'gifti')

def test_package_gii_metadata_both_hemispheres(mock_gifti_func):
    """Test packaging GIFTI metadata with both hemispheres"""
    metadata = package_gii_metadata(mock_gifti_func, mock_gifti_func)
    
    assert 'global_min' in metadata
    assert 'global_max' in metadata
    assert 'timepoints' in metadata
    assert len(metadata['timepoints']) == 5  # From mock data
    assert isinstance(metadata['global_min'], float)
    assert isinstance(metadata['global_max'], float)
    assert metadata['global_min'] <= metadata['global_max']

def test_package_gii_metadata_single_hemisphere(mock_gifti_func):
    """Test packaging GIFTI metadata with single hemisphere"""
    # Test left only
    left_metadata = package_gii_metadata(mock_gifti_func, None)
    assert len(left_metadata['timepoints']) == 5
    
    # Test right only
    right_metadata = package_gii_metadata(None, mock_gifti_func)
    assert len(right_metadata['timepoints']) == 5

def test_package_gii_metadata_empty():
    """Test packaging GIFTI metadata with no data"""
    # Suppress expected RuntimeWarnings for NaN operations
    with pytest.warns(RuntimeWarning) as warning_records:
        metadata = package_gii_metadata(None, None)
        
        # Verify the structure of returned metadata
        assert metadata['timepoints'] == []
        assert np.isnan(metadata['global_min'])
        assert np.isnan(metadata['global_max'])
        
        # Verify we got the expected warnings
        assert len(warning_records) == 2
        assert "All-NaN axis encountered" in str(warning_records[0].message)
        assert "All-NaN axis encountered" in str(warning_records[1].message)

def test_package_nii_metadata_4d(mock_nifti_4d):
    """Test packaging NIFTI metadata for 4D image"""
    metadata = package_nii_metadata(mock_nifti_4d)
    
    assert 'global_min' in metadata
    assert 'global_max' in metadata
    assert 'timepoints' in metadata
    assert 'slice_len' in metadata
    
    assert len(metadata['timepoints']) == 5  # From mock data
    assert isinstance(metadata['slice_len'], dict)
    assert all(k in metadata['slice_len'] for k in ['x', 'y', 'z'])
    assert all(metadata['slice_len'][k] == 10 for k in ['x', 'y', 'z'])

def test_package_nii_metadata_3d(mock_nifti_3d):
    """Test packaging NIFTI metadata for 3D image"""
    metadata = package_nii_metadata(mock_nifti_3d)
    
    assert len(metadata['timepoints']) == 1
    assert metadata['timepoints'] == [0]
    assert all(metadata['slice_len'][k] == 10 for k in ['x', 'y', 'z'])

def test_apply_mask_nifti(mock_nifti_3d):
    """Test applying mask to NIFTI image"""
    # Create mask (zeros with a block of ones)
    mask = np.zeros((10, 10, 10))
    mask[2:8, 2:8, 2:8] = 1
    mask_img = nib.Nifti1Image(mask, np.eye(4))
    
    # Apply mask
    masked_img = apply_mask_nifti(mock_nifti_3d, mask_img)
    
    # Verify output
    assert isinstance(masked_img, nib.Nifti1Image)
    assert masked_img.shape == mock_nifti_3d.shape
    
    # Check that values outside mask are zero
    masked_data = masked_img.get_fdata()
    assert np.all(masked_data[mask == 0] == 0)
    assert np.any(masked_data[mask == 1] != 0)

def test_apply_mask_nifti_4d(mock_nifti_4d):
    """Test applying mask to 4D NIFTI image"""
    # Create mask
    mask = np.zeros((10, 10, 10))
    mask[2:8, 2:8, 2:8] = 1
    mask_img = nib.Nifti1Image(mask, np.eye(4))
    
    # Apply mask
    masked_img = apply_mask_nifti(mock_nifti_4d, mask_img)
    
    # Verify output
    assert isinstance(masked_img, nib.Nifti1Image)
    assert masked_img.shape == mock_nifti_4d.shape
    
    # Check masking for each timepoint
    masked_data = masked_img.get_fdata()
    for t in range(mock_nifti_4d.shape[3]):
        assert np.all(masked_data[..., t][mask == 0] == 0)
        assert np.any(masked_data[..., t][mask == 1] != 0)

def test_apply_mask_shape_mismatch(mock_nifti_3d):
    """Test error handling for shape mismatch between image and mask"""
    # Create mask with different shape
    mask = np.zeros((8, 8, 8))
    mask_img = nib.Nifti1Image(mask, np.eye(4))
    
    # Should raise ValueError due to shape mismatch
    with pytest.raises(ValueError):
        apply_mask_nifti(mock_nifti_3d, mask_img)
