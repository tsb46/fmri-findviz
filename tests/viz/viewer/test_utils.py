"""Tests for viewer utility functions"""
import pytest
import numpy as np
import nibabel as nib
from nibabel.gifti import GiftiImage, GiftiDataArray

from findviz.viz.viewer.utils import (
    get_fmri_minmax,
    package_gii_metadata,
    package_nii_metadata,
    apply_mask_nifti,
    get_coord_labels_gifti,
    get_coord_labels_nifti,
    extend_color_range,
    get_precision,
    get_slider_step_size,
    get_ts_minmax,
    transform_to_world_coords
)

def test_get_minmax_nifti():
    """Test getting min/max values from NIFTI data"""
    # Create test data with known min/max
    data = np.array([[-1.0, 0.0], [1.0, 2.0]])
    min_val, max_val = get_fmri_minmax(data, 'nifti')
    
    assert min_val == -1.0
    assert max_val == 2.0

def test_get_minmax_nifti_with_nan():
    """Test getting min/max values from NIFTI data with NaN values"""
    data = np.array([[-1.0, np.nan], [1.0, 2.0]])
    min_val, max_val = get_fmri_minmax(data, 'nifti')
    
    assert min_val == -1.0
    assert max_val == 2.0

def test_get_minmax_gifti(mock_gifti_func):
    """Test getting min/max values from GIFTI data"""
    min_val, max_val = get_fmri_minmax(mock_gifti_func, 'gifti')
    
    # Values should be within expected range (0 to 1 from random data)
    assert 0 <= min_val <= 1
    assert 0 <= max_val <= 1
    assert min_val <= max_val

def test_get_minmax_invalid_type():
    """Test get_minmax with invalid file type"""
    data = np.array([1, 2, 3])
    with pytest.raises(ValueError, match="file_type must be 'gifti' or 'nifti'"):
        get_fmri_minmax(data, 'invalid')

def test_get_minmax_invalid_data_type():
    """Test get_minmax with invalid data type"""
    with pytest.raises(TypeError, match="NIFTI data must be numpy array"):
        get_fmri_minmax("not an array", 'nifti')
    
    with pytest.raises(TypeError, match="GIFTI data must be GiftiImage"):
        get_fmri_minmax(np.array([1, 2, 3]), 'gifti')

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

def test_apply_mask_nifti(mock_nifti_4d):
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
        # check is nan
        assert np.all(np.isnan(masked_data[..., t][mask == 0]))
        assert not np.any(np.isnan(masked_data[..., t][mask == 1]))

def test_apply_mask_shape_mismatch(mock_nifti_4d):
    """Test error handling for shape mismatch between image and mask"""
    # Create mask with different shape
    mask = np.zeros((8, 8, 8))
    mask_img = nib.Nifti1Image(mask, np.eye(4))
    
    # Should raise IndexError due to shape mismatch
    with pytest.raises(IndexError):
        apply_mask_nifti(mock_nifti_4d, mask_img)

def test_extend_color_range():
    """Test extending color range by percentage"""
    min_val, max_val = extend_color_range(-1.0, 2.0, 0.25)
    assert min_val == -1.25  # -1.0 - (0.25 * |-1.0|)
    assert max_val == 2.5    # 2.0 + (0.25 * |2.0|)

def test_get_coord_labels_gifti():
    """Test getting coordinate labels for GIFTI data"""
    # Test with None input
    assert get_coord_labels_gifti(None, 'left') is None
    
    # Test with mock GIFTI data
    mock_data = np.array([1, 2, 3], dtype=np.float32)
    mock_darray = GiftiDataArray(mock_data)
    mock_gifti = GiftiImage(darrays=[mock_darray])
    
    labels = get_coord_labels_gifti(mock_gifti, 'left')
    assert len(labels) == 3
    assert labels[0] == (0, 'left')
    assert labels[1] == (1, 'left')
    assert labels[2] == (2, 'left')

def test_get_coord_labels_nifti(mock_nifti_3d):
    """Test getting coordinate labels for NIFTI data"""
    labels = get_coord_labels_nifti(mock_nifti_3d)
    
    # Check shape matches input data
    assert labels.shape == mock_nifti_3d.shape[:3]
    
    # Check format of coordinate labels
    assert labels[0, 0, 0] == "Voxel: 0, 0, 0"
    assert labels[1, 2, 3] == "Voxel: 1, 2, 3"

def test_get_precision():
    """Test precision calculation for slider step size"""
    assert get_precision(100) == 0
    assert get_precision(100.0) == 1
    assert get_precision(10.5) == 1
    assert get_precision(0.001) == 3
    assert get_precision(0.0000001) == 6  # Should be capped at max_precision=6
    assert get_precision(np.nan) == 0     # Should handle NaN values

def test_get_slider_step_size():
    """Test slider step size calculation"""
    step = get_slider_step_size(data_range=10.0, slider_steps=100, precision=2)
    assert step == 0.1
    
    step = get_slider_step_size(data_range=1.0, slider_steps=10, precision=3)
    assert step == 0.1

def test_get_ts_minmax():
    """Test getting min/max values for time series data"""
    # Test with no data
    min_val, max_val = get_ts_minmax(-1.0, 1.0)
    assert min_val == -1.0
    assert max_val == 1.0
    
    # Test with ts_data only
    ts_data = {'ts1': np.array([-2, 0, 2]), 'ts2': np.array([-1, 0, 1])}
    min_val, max_val = get_ts_minmax(-1.0, 1.0, ts_data=ts_data)
    assert min_val == -2.0
    assert max_val == 2.0
    
    # Test with both ts_data and task_data
    task_data = {'task1': np.array([-3, 0, 3])}
    min_val, max_val = get_ts_minmax(-1.0, 1.0, ts_data=ts_data, task_data=task_data)
    assert min_val == -3.0
    assert max_val == 3.0

def test_transform_to_world_coords():
    """Test transformation from voxel to world coordinates"""
    # Create simple affine matrix (identity in this case)
    affine = np.eye(4)
    
    # Test with simple coordinates
    voxel_coords = {'x': 1, 'y': 2, 'z': 3}
    world_coords = transform_to_world_coords(voxel_coords, affine)
    
    assert np.array_equal(world_coords, np.array([1.0, 2.0, 3.0]))
    
    # Test with non-identity affine
    affine = np.array([
        [2, 0, 0, 10],
        [0, 2, 0, 20],
        [0, 0, 2, 30],
        [0, 0, 0, 1]
    ])
    world_coords = transform_to_world_coords(voxel_coords, affine)
    assert np.array_equal(world_coords, np.array([12.0, 24.0, 36.0]))
