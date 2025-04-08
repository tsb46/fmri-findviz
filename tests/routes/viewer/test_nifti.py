"""
Tests for nifti.py module
"""
import numpy as np
import nibabel as nib
import pytest
from unittest.mock import patch, MagicMock

from findviz.routes.viewer.nifti import (
    get_nifti_data,
    get_slice_data,
    get_timecourse_nifti,
    threshold_nifti_data
)


@pytest.fixture
def mock_functional_image():
    """Create a mock 4D functional NIfTI image."""
    # Create a small 4D array (x, y, z, time)
    data = np.ones((10, 12, 8, 5), dtype=np.float32)
    
    # Add some varying values for testing
    for t in range(5):
        data[..., t] = data[..., t] * (t + 1)
    
    # Create specific values at test coordinates
    data[5, 6, 3, :] = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
    
    affine = np.eye(4)
    return nib.Nifti1Image(data, affine)


@pytest.fixture
def mock_anatomical_image():
    """Create a mock 3D anatomical NIfTI image."""
    # Create a small 3D array
    data = np.ones((10, 12, 8), dtype=np.float32) * 10
    affine = np.eye(4)
    return nib.Nifti1Image(data, affine)


@pytest.fixture
def mock_coord_labels():
    """Create mock coordinate labels."""
    # Create an array of the same first 3 dimensions as the functional data but with coordinate values
    coords = np.empty((10, 12, 8), dtype=object)
    
    for x in range(10):
        for y in range(12):
            for z in range(8):
                coords[x, y, z] = f"Voxel: {x}, {y}, {z}"
                
    return coords


@pytest.fixture
def mock_ortho_slice_index():
    """Mock orthogonal slice index dictionary."""
    return {
        'x': 5,
        'y': 6,
        'z': 3
    }


@pytest.fixture
def mock_montage_slice_index():
    """Mock montage slice index dictionary."""
    return {
        'slice_1': {'x': 3, 'y': 6, 'z': 3},
        'slice_2': {'x': 5, 'y': 6, 'z': 3},
        'slice_3': {'x': 7, 'y': 6, 'z': 3}
    }


def test_get_slice_data_x_axis(mock_functional_image):
    """Test getting slice data along the x-axis."""
    # Get data from the first timepoint
    data = mock_functional_image.get_fdata()[..., 0]
    
    # Get a slice along the x-axis
    slice_data = get_slice_data(data, slice_index=5, axis='x')
    
    # Check the shape and contents
    assert isinstance(slice_data, list)
    assert len(slice_data) == 8  # z dimension
    assert len(slice_data[0]) == 12  # y dimension
    
    # Create expected data - ones with special value at [6, 3]
    expected = np.ones((8, 12))
    expected[3, 6] = 0.5  # The transposed position of our special value
    
    # Test values match expected
    assert np.allclose(np.array(slice_data), expected, atol=1e-6)


def test_get_slice_data_y_axis(mock_functional_image):
    """Test getting slice data along the y-axis."""
    # Get data from the first timepoint
    data = mock_functional_image.get_fdata()[..., 0]
    
    # Get a slice along the y-axis
    slice_data = get_slice_data(data, slice_index=6, axis='y')
    
    # Check the shape and contents
    assert isinstance(slice_data, list)
    assert len(slice_data) == 8  # z dimension
    assert len(slice_data[0]) == 10  # x dimension
    
    # Create expected data - ones with special value at [5, 3]
    expected = np.ones((8, 10))
    expected[3, 5] = 0.5  # The transposed position of our special value
    
    # Test values match expected
    assert np.allclose(np.array(slice_data), expected, atol=1e-6)


def test_get_slice_data_z_axis(mock_functional_image):
    """Test getting slice data along the z-axis."""
    # Get data from the first timepoint
    data = mock_functional_image.get_fdata()[..., 0]
    
    # Get a slice along the z-axis
    slice_data = get_slice_data(data, slice_index=3, axis='z')
    
    # Check the shape and contents
    assert isinstance(slice_data, list)
    assert len(slice_data) == 12  # y dimension
    assert len(slice_data[0]) == 10  # x dimension
    
    # Create expected data - ones with special value at [5, 6]
    expected = np.ones((12, 10))
    expected[6, 5] = 0.5  # The transposed position of our special value
    
    # Test values match expected
    assert np.allclose(np.array(slice_data), expected, atol=1e-6)


def test_get_slice_data_string_type(mock_coord_labels):
    """Test getting slice data with string array type."""
    # Get a slice of coordinate labels
    slice_data = get_slice_data(mock_coord_labels, slice_index=5, axis='x', array_type='string')
    
    # Check that the result is a list (not sanitized numpy array)
    assert isinstance(slice_data, list)
    assert isinstance(slice_data[0], list)
    # The output should contain the coordinates
    assert slice_data[1][2] == "Voxel: 5, 2, 1"  # x coordinate at [5, 2, 1]
    assert slice_data[3][6] == "Voxel: 5, 6, 3"  # y coordinate at [5, 6, 3]
    assert slice_data[2][5] == "Voxel: 5, 5, 2"  # z coordinate at [5, 5, 2]


def test_threshold_nifti_data():
    """Test thresholding NIfTI data."""
    # Create test data
    data = np.arange(27).reshape(3, 3, 3).astype(np.float32)
    
    # Apply threshold (applied in place)
    thresholded = data.copy()
    threshold_nifti_data(thresholded, threshold_min=5, threshold_max=15)
    
    # Check that values inside the threshold are preserved, and values outside are NaN
    for x in range(3):
        for y in range(3):
            for z in range(3):
                value = data[x, y, z]
                if value >= 5 and value <= 15:
                    assert np.isnan(thresholded[x, y, z])
                else:
                    assert thresholded[x, y, z] == value


def test_get_timecourse_nifti(mock_functional_image):
    """Test getting timecourse data for a specific voxel."""
    timecourse, label = get_timecourse_nifti(
        func_img=mock_functional_image,
        x=5, y=6, z=3
    )
    
    # Check the timecourse data
    assert len(timecourse) == 5
    assert np.allclose(timecourse, [0.5, 1.5, 2.5, 3.5, 4.5], atol=1e-6)
    
    # Check the label
    assert label == "Voxel: (x=5, y=6, z=3)"


@patch('findviz.routes.viewer.nifti.get_slice_data')
def test_get_nifti_data_ortho_view(mock_get_slice_data, mock_functional_image, mock_coord_labels, mock_ortho_slice_index):
    """Test getting NIfTI data in orthogonal view."""
    # Mock the get_slice_data function to return predictable data
    mock_get_slice_data.side_effect = lambda *args, **kwargs: [[1.0]] if kwargs.get('array_type') != 'string' else [["coords"]]
    
    # Call the function with ortho view state
    result = get_nifti_data(
        time_point=0,
        func_img=mock_functional_image,
        coord_labels=mock_coord_labels,
        slice_idx=mock_ortho_slice_index,
        view_state='ortho',
        montage_slice_dir='x'
    )
    
    # Verify the structure of the result
    assert 'func' in result
    assert 'slice_1' in result['func']
    assert 'slice_2' in result['func']
    assert 'slice_3' in result['func']
    assert 'coords' in result
    
    # Verify the get_slice_data was called the right number of times
    assert mock_get_slice_data.call_count == 6  # 3 slices for func + 3 for coords


@patch('findviz.routes.viewer.nifti.get_slice_data')
def test_get_nifti_data_montage_view(mock_get_slice_data, mock_functional_image, mock_coord_labels, mock_montage_slice_index):
    """Test getting NIfTI data in montage view."""
    # Mock the get_slice_data function to return predictable data
    mock_get_slice_data.side_effect = lambda *args, **kwargs: [[1.0]] if kwargs.get('array_type') != 'string' else [["coords"]]
    
    # Call the function with montage view state
    result = get_nifti_data(
        time_point=0,
        func_img=mock_functional_image,
        coord_labels=mock_coord_labels,
        slice_idx=mock_montage_slice_index,
        view_state='montage',
        montage_slice_dir='x'
    )
    
    # Verify the structure of the result
    assert 'func' in result
    assert 'slice_1' in result['func']
    assert 'slice_2' in result['func']
    assert 'slice_3' in result['func']
    assert 'coords' in result
    
    # Verify the get_slice_data was called the right number of times and with the right parameters
    assert mock_get_slice_data.call_count == 6  # 3 slices for func + 3 for coords
    
    # In montage view, all slices should use the same axis (montage_slice_dir)
    for call_args in mock_get_slice_data.call_args_list:
        if 'axis' in call_args[1]:
            assert call_args[1]['axis'] == 'x'


@patch('findviz.routes.viewer.nifti.get_slice_data')
def test_get_nifti_data_with_anat(mock_get_slice_data, mock_functional_image, mock_anatomical_image, mock_coord_labels, mock_ortho_slice_index):
    """Test getting NIfTI data with anatomical image."""
    # Mock the get_slice_data function to return predictable data
    mock_get_slice_data.side_effect = lambda *args, **kwargs: [[1.0]] if kwargs.get('array_type') != 'string' else [["coords"]]
    
    # Call the function with ortho view state and anatomical image
    result = get_nifti_data(
        time_point=0,
        func_img=mock_functional_image,
        coord_labels=mock_coord_labels,
        slice_idx=mock_ortho_slice_index,
        view_state='ortho',
        montage_slice_dir='x',
        anat_img=mock_anatomical_image
    )
    
    # Verify the structure of the result
    assert 'func' in result
    assert 'anat' in result
    assert 'slice_1' in result['func']
    assert 'slice_1' in result['anat']
    assert 'coords' in result
    
    # Verify the get_slice_data was called the right number of times
    assert mock_get_slice_data.call_count == 9  # 3 slices for func + 3 for anat + 3 for coords


@patch('findviz.routes.viewer.nifti.threshold_nifti_data')
@patch('findviz.routes.viewer.nifti.get_slice_data')
def test_get_nifti_data_with_threshold(mock_get_slice_data, mock_threshold, mock_functional_image, mock_coord_labels, mock_ortho_slice_index):
    """Test getting NIfTI data with thresholds."""
    # Mock the functions to return predictable data
    mock_get_slice_data.side_effect = lambda *args, **kwargs: [[1.0]] if kwargs.get('array_type') != 'string' else [["coords"]]
    mock_threshold.return_value = np.ones((10, 12, 8))
    
    # Call the function with thresholds
    result = get_nifti_data(
        time_point=0,
        func_img=mock_functional_image,
        coord_labels=mock_coord_labels,
        slice_idx=mock_ortho_slice_index,
        view_state='ortho',
        montage_slice_dir='x',
        threshold_min=0.5,
        threshold_max=2.0,
        threshold_min_orig=0.0,
        threshold_max_orig=3.0
    )
    
    # Verify the structure of the result
    assert 'func' in result
    assert 'slice_1' in result['func']
    
    # Verify the threshold function was called with the right parameters
    mock_threshold.assert_called_once()
    args, kwargs = mock_threshold.call_args
    assert kwargs['threshold_min'] == 0.5
    assert kwargs['threshold_max'] == 2.0
