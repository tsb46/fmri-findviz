"""
Tests for gifti.py module
"""
import numpy as np
import nibabel as nib
import pytest
from unittest.mock import patch, MagicMock
from nibabel.gifti.gifti import GiftiDataArray

from findviz.routes.viewer.gifti import (
    get_gifti_data,
    get_timecourse_gifti,
    threshold_gifti_data
)


@pytest.fixture
def mock_left_functional_image():
    """Create a mock left hemisphere GiftiImage with functional data."""
    # Create 5 timepoints of data with 100 vertices each
    darrays = []
    for t in range(5):
        # Values increase with timepoint
        data = np.ones(100, dtype=np.float32) * (t + 1)
        # Set a specific value for testing at vertex 42
        data[42] = 0.5 + t
        darray = GiftiDataArray(data=data)
        darrays.append(darray)
    
    gifti_img = nib.gifti.GiftiImage(darrays=darrays)
    return gifti_img


@pytest.fixture
def mock_right_functional_image():
    """Create a mock right hemisphere GiftiImage with functional data."""
    # Create 5 timepoints of data with 100 vertices each
    darrays = []
    for t in range(5):
        # Values increase with timepoint
        data = np.ones(100, dtype=np.float32) * (t + 1) + 0.1
        # Set a specific value for testing at vertex 57
        data[57] = 0.7 + t
        darray = GiftiDataArray(data=data)
        darrays.append(darray)
    
    gifti_img = nib.gifti.GiftiImage(darrays=darrays)
    return gifti_img


def test_threshold_gifti_data():
    """Test thresholding GIFTI data."""
    # Create test data
    data = np.linspace(0, 10, 100).astype(np.float32)
    
    # Apply threshold
    thresholded = threshold_gifti_data(data.copy(), threshold_min=2, threshold_max=8)
    
    # Check that values inside the threshold range are set to NaN
    for i, value in enumerate(data):
        if 2 <= value <= 8:
            assert np.isnan(thresholded[i])
        else:
            assert thresholded[i] == value


def test_get_gifti_data_left_only(mock_left_functional_image):
    """Test getting GIFTI data with only left hemisphere data."""
    # Test for timepoint 0
    result = get_gifti_data(
        time_point=0,
        left_func_img=mock_left_functional_image,
        right_func_img=None
    )
    
    # Check structure of result
    assert 'left_hemisphere' in result
    assert 'right_hemisphere' in result
    assert result['left_hemisphere'] is not None
    assert result['right_hemisphere'] is None
    
    # Check content of left hemisphere data
    left_data = result['left_hemisphere']
    assert len(left_data) == 100  # Number of vertices
    assert np.isclose(left_data[0], 1.0, atol=1e-6)    # Regular vertex value at timepoint 0
    assert np.isclose(left_data[42], 0.5, atol=1e-6)   # Special vertex value


def test_get_gifti_data_right_only(mock_right_functional_image):
    """Test getting GIFTI data with only right hemisphere data."""
    # Test for timepoint 2
    result = get_gifti_data(
        time_point=2,
        left_func_img=None,
        right_func_img=mock_right_functional_image
    )
    
    # Check structure of result
    assert 'left_hemisphere' in result
    assert 'right_hemisphere' in result
    assert result['left_hemisphere'] is None
    assert result['right_hemisphere'] is not None
    
    # Check content of right hemisphere data
    right_data = result['right_hemisphere']
    assert len(right_data) == 100  # Number of vertices
    assert np.isclose(right_data[0], 3.1, atol=1e-6)    # Regular vertex value at timepoint 2
    assert np.isclose(right_data[57], 2.7, atol=1e-6)   # Special vertex value


def test_get_gifti_data_both_hemispheres(mock_left_functional_image, mock_right_functional_image):
    """Test getting GIFTI data with both hemisphere data."""
    # Test for timepoint 3
    result = get_gifti_data(
        time_point=3,
        left_func_img=mock_left_functional_image,
        right_func_img=mock_right_functional_image
    )
    
    # Check structure of result
    assert 'left_hemisphere' in result
    assert 'right_hemisphere' in result
    assert result['left_hemisphere'] is not None
    assert result['right_hemisphere'] is not None
    
    # Check content of both hemisphere data
    left_data = result['left_hemisphere']
    right_data = result['right_hemisphere']
    
    assert len(left_data) == 100   # Number of vertices
    assert len(right_data) == 100  # Number of vertices
    
    assert np.isclose(left_data[0], 4.0, atol=1e-6)     # Regular vertex value at timepoint 3
    assert np.isclose(right_data[0], 4.1, atol=1e-6)    # Regular vertex value at timepoint 3
    
    assert np.isclose(left_data[42], 3.5, atol=1e-6)    # Special left vertex value
    assert np.isclose(right_data[57], 3.7, atol=1e-6)   # Special right vertex value


@patch('findviz.routes.viewer.gifti.threshold_gifti_data')
def test_get_gifti_data_with_threshold(mock_threshold, mock_left_functional_image, mock_right_functional_image):
    """Test getting GIFTI data with thresholding."""
    # Set up mock threshold function
    mock_threshold.side_effect = lambda data, min_val, max_val: data  # Just return the input data
    
    # Call function with thresholds that differ from originals
    result = get_gifti_data(
        time_point=0,
        left_func_img=mock_left_functional_image,
        right_func_img=mock_right_functional_image,
        threshold_min=0.5,
        threshold_max=2.0,
        threshold_min_orig=0.0,
        threshold_max_orig=3.0
    )
    
    # Verify threshold was called for both hemispheres
    assert mock_threshold.call_count == 2
    
    # Verify threshold parameters
    calls = mock_threshold.call_args_list
    for call in calls:
        args, kwargs = call
        assert args[1] == 0.5  # threshold_min
        assert args[2] == 2.0  # threshold_max


def test_get_gifti_data_without_threshold(mock_left_functional_image, mock_right_functional_image):
    """Test getting GIFTI data without thresholding (same min/max)."""
    with patch('findviz.routes.viewer.gifti.threshold_gifti_data') as mock_threshold:
        # Call function with thresholds that are the same as originals
        result = get_gifti_data(
            time_point=0,
            left_func_img=mock_left_functional_image,
            right_func_img=mock_right_functional_image,
            threshold_min=0.5,
            threshold_max=2.0,
            threshold_min_orig=0.5,
            threshold_max_orig=2.0
        )
        
        # Threshold should not be called because threshold values haven't changed
        assert mock_threshold.call_count == 0


def test_get_timecourse_gifti_left(mock_left_functional_image):
    """Test getting timecourse data from left hemisphere."""
    timecourse, label = get_timecourse_gifti(
        left_func_img=mock_left_functional_image,
        right_func_img=None,
        vertex_index=42,
        hemisphere='left'
    )
    
    # Check timecourse data
    assert len(timecourse) == 5  # 5 timepoints
    assert np.allclose(timecourse, [0.5, 1.5, 2.5, 3.5, 4.5], atol=1e-6)
    
    # Check label
    assert label == "Vertex: 42 (left)"


def test_get_timecourse_gifti_right(mock_right_functional_image):
    """Test getting timecourse data from right hemisphere."""
    timecourse, label = get_timecourse_gifti(
        left_func_img=None,
        right_func_img=mock_right_functional_image,
        vertex_index=57,
        hemisphere='right'
    )
    
    # Check timecourse data
    assert len(timecourse) == 5  # 5 timepoints
    assert np.allclose(timecourse, [0.7, 1.7, 2.7, 3.7, 4.7], atol=1e-6)
    
    # Check label
    assert label == "Vertex: 57 (right)"


def test_get_timecourse_gifti_with_both_hemispheres(mock_left_functional_image, mock_right_functional_image):
    """Test getting timecourse data when both hemispheres are available."""
    # Test left hemisphere selection
    timecourse_left, label_left = get_timecourse_gifti(
        left_func_img=mock_left_functional_image,
        right_func_img=mock_right_functional_image,
        vertex_index=42,
        hemisphere='left'
    )
    
    # Check left hemisphere data
    assert len(timecourse_left) == 5
    assert np.allclose(timecourse_left, [0.5, 1.5, 2.5, 3.5, 4.5], atol=1e-6)
    assert label_left == "Vertex: 42 (left)"
    
    # Test right hemisphere selection
    timecourse_right, label_right = get_timecourse_gifti(
        left_func_img=mock_left_functional_image,
        right_func_img=mock_right_functional_image,
        vertex_index=57,
        hemisphere='right'
    )
    
    # Check right hemisphere data
    assert len(timecourse_right) == 5
    assert np.allclose(timecourse_right, [0.7, 1.7, 2.7, 3.7, 4.7], atol=1e-6)
    assert label_right == "Vertex: 57 (right)"
