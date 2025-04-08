"""
Tests for findviz.viz.analysis.utils module
"""

import pytest
import numpy as np
from findviz.viz.analysis.utils import extract_range, get_lag_mat


class TestExtractRange:
    """Test cases for extract_range function"""
    
    @pytest.fixture
    def sample_array(self):
        """Fixture providing a sample array for testing"""
        return np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
            [10.0, 11.0, 12.0],
            [13.0, 14.0, 15.0]
        ])
    
    def test_extract_within_bounds(self, sample_array):
        """Test extracting a range entirely within the array bounds"""
        center = 2  # Center at row index 2 (value [7.0, 8.0, 9.0])
        left_edge = -1  # One row before center
        right_edge = 1  # One row after center
        
        result = extract_range(sample_array, center, left_edge, right_edge)
        
        # Expected: 3 rows centered at index 2
        expected = np.array([
            [4.0, 5.0, 6.0],   # center-1
            [7.0, 8.0, 9.0],   # center
            [10.0, 11.0, 12.0] # center+1
        ])
        
        assert result.shape == (3, 3)
        assert np.array_equal(result, expected)
    
    def test_extract_left_out_of_bounds(self, sample_array):
        """Test extracting a range where left edge is out of bounds"""
        center = 1  # Center at row index 1 (value [4.0, 5.0, 6.0])
        left_edge = -2  # Two rows before center (out of bounds)
        right_edge = 1  # One row after center
        
        result = extract_range(sample_array, center, left_edge, right_edge)
        
        # Expected: 4 rows with first row as NaN (left edge out of bounds)
        expected = np.array([
            [np.nan, np.nan, np.nan],  # Out of bounds (padded with NaN)
            [1.0, 2.0, 3.0],           # center-1
            [4.0, 5.0, 6.0],           # center
            [7.0, 8.0, 9.0]            # center+1
        ])
        
        assert result.shape == (4, 3)
        assert np.array_equal(result, expected, equal_nan=True)
    
    def test_extract_right_out_of_bounds(self, sample_array):
        """Test extracting a range where right edge is out of bounds"""
        center = 3  # Center at row index 3 (value [10.0, 11.0, 12.0])
        left_edge = -1  # One row before center
        right_edge = 2  # Two rows after center (out of bounds)
        
        result = extract_range(sample_array, center, left_edge, right_edge)
        
        # Expected: 4 rows with last row as NaN (right edge out of bounds)
        expected = np.array([
            [7.0, 8.0, 9.0],           # center-1
            [10.0, 11.0, 12.0],        # center
            [13.0, 14.0, 15.0],        # center+1
            [np.nan, np.nan, np.nan]   # Out of bounds (padded with NaN)
        ])
        
        assert result.shape == (4, 3)
        assert np.array_equal(result, expected, equal_nan=True)
    
    def test_extract_both_out_of_bounds(self, sample_array):
        """Test extracting a range where both edges are out of bounds"""
        center = 0  # Center at row index 0 (value [1.0, 2.0, 3.0])
        left_edge = -2  # Two rows before center (out of bounds)
        right_edge = 2  # Two rows after center
        
        result = extract_range(sample_array, center, left_edge, right_edge)
        
        # Expected: 5 rows with first two rows as NaN (left edge out of bounds)
        expected = np.array([
            [np.nan, np.nan, np.nan],  # Out of bounds (padded with NaN)
            [np.nan, np.nan, np.nan],  # Out of bounds (padded with NaN)
            [1.0, 2.0, 3.0],           # center
            [4.0, 5.0, 6.0],           # center+1
            [7.0, 8.0, 9.0]            # center+2
        ])
        
        assert result.shape == (5, 3)
        assert np.array_equal(result, expected, equal_nan=True)
    
    def test_extract_center_out_of_bounds(self):
        """Test extracting with center outside the array bounds"""
        array = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ])
        
        center = 5  # Center beyond array bounds
        left_edge = -2
        right_edge = 2
        
        result = extract_range(array, center, left_edge, right_edge)
        
        # Everything should be NaN as center+left_edge is beyond array bounds
        expected = np.full((5, 3), np.nan)
        
        assert result.shape == (5, 3)
        assert np.array_equal(result, expected, equal_nan=True)
    
    def test_extract_zero_range(self, sample_array):
        """Test extracting just the center row (left_edge = right_edge = 0)"""
        center = 2  # Center at row index 2
        left_edge = 0
        right_edge = 0
        
        result = extract_range(sample_array, center, left_edge, right_edge)
        
        # Expected: just the center row
        expected = np.array([[7.0, 8.0, 9.0]])
        
        assert result.shape == (1, 3)
        assert np.array_equal(result, expected)
    
    def test_extract_empty_array(self):
        """Test extracting from an empty array"""
        array = np.empty((0, 3))
        center = 0
        left_edge = -1
        right_edge = 1
        
        result = extract_range(array, center, left_edge, right_edge)
        
        # Expected: 3x3 array filled with NaNs
        expected = np.full((3, 3), np.nan)
        
        assert result.shape == (3, 3)
        assert np.array_equal(result, expected, equal_nan=True)


class TestGetLagMat:
    """Test cases for get_lag_mat function"""
    
    @pytest.fixture
    def sample_timecourse(self):
        """Fixture providing a sample time course for testing"""
        # Create a 10x2 array representing a time course with 2 channels
        return np.array([
            [1.0, 2.0],
            [3.0, 4.0],
            [5.0, 6.0],
            [7.0, 8.0],
            [9.0, 10.0],
            [11.0, 12.0],
            [13.0, 14.0],
            [15.0, 16.0],
            [17.0, 18.0],
            [19.0, 20.0]
        ])
    
    def test_get_lag_mat_positive_lags(self, sample_timecourse):
        """Test creating lag matrix with positive lags"""
        lags = [0, 2, 4]  # No lag, lag 2, lag 4
        
        result = get_lag_mat(sample_timecourse, lags)
        
        # Expected: first 2 columns = original, next 2 = lag 2, next 2 = lag 4
        # For lag 2, first 2 rows should be zeros, then original values shifted
        # For lag 4, first 4 rows should be zeros, then original values shifted
        expected = np.zeros((10, 6))
        
        # No lag (first 2 columns)
        expected[:, 0:2] = sample_timecourse
        
        # Lag 2 (next 2 columns)
        expected[2:, 2:4] = sample_timecourse[:-2]
        
        # Lag 4 (last 2 columns)
        expected[4:, 4:6] = sample_timecourse[:-4]
        
        assert result.shape == (10, 6)
        assert np.array_equal(result, expected)
    
    def test_get_lag_mat_negative_lags(self, sample_timecourse):
        """Test creating lag matrix with negative lags"""
        lags = [-1, -3]  # Lag -1, lag -3
        
        result = get_lag_mat(sample_timecourse, lags)
        
        # Expected: first 2 columns = lag -1, next 2 = lag -3
        # For lag -1, last row should be zeros, then original values shifted forward
        # For lag -3, last 3 rows should be zeros, then original values shifted forward
        expected = np.zeros((10, 4))
        
        # Lag -1 (first 2 columns)
        expected[:-1, 0:2] = sample_timecourse[1:]
        
        # Lag -3 (next 2 columns)
        expected[:-3, 2:4] = sample_timecourse[3:]
        
        assert result.shape == (10, 4)
        assert np.array_equal(result, expected)
    
    def test_get_lag_mat_mixed_lags(self, sample_timecourse):
        """Test creating lag matrix with both positive and negative lags"""
        lags = [-2, 0, 2]  # Lag -2, no lag, lag 2
        
        result = get_lag_mat(sample_timecourse, lags)
        
        # Expected: first 2 columns = lag -2, next 2 = no lag, next 2 = lag 2
        expected = np.zeros((10, 6))
        
        # Lag -2 (first 2 columns)
        expected[:-2, 0:2] = sample_timecourse[2:]
        
        # No lag (next 2 columns)
        expected[:, 2:4] = sample_timecourse
        
        # Lag 2 (last 2 columns)
        expected[2:, 4:6] = sample_timecourse[:-2]
        
        assert result.shape == (10, 6)
        assert np.array_equal(result, expected)
    
    def test_get_lag_mat_empty_lags(self, sample_timecourse):
        """Test with empty lags list"""
        lags = []
        
        result = get_lag_mat(sample_timecourse, lags)
        
        # Should return the original time course
        assert np.array_equal(result, sample_timecourse)
    
    def test_get_lag_mat_single_row(self):
        """Test with a single row time course"""
        timecourse = np.array([[1.0, 2.0]])  # 1x2 array
        lags = [0, 1, 2]
        
        result = get_lag_mat(timecourse, lags)
        
        # Expected: zeros for all lags since there's only one row
        expected = np.zeros((1, 6))
        expected[:, 0:2] = timecourse  # Only the no-lag columns have values
        
        assert result.shape == (1, 6)
        assert np.array_equal(result, expected)
    
    def test_get_lag_mat_single_column(self):
        """Test with a single column time course"""
        timecourse = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])  # 5x1 array
        lags = [0, 1, 2]
        
        result = get_lag_mat(timecourse, lags)
        
        # Expected: first column = original, second = lag 1, third = lag 2
        expected = np.zeros((5, 3))
        expected[:, 0] = timecourse.flatten()
        expected[1:, 1] = timecourse[:-1].flatten()
        expected[2:, 2] = timecourse[:-2].flatten()
        
        assert result.shape == (5, 3)
        assert np.array_equal(result, expected)
    
    def test_get_lag_mat_large_lag(self, sample_timecourse):
        """Test with a lag larger than the time course length"""
        lags = [0, 11]  # lag 11 is larger than the 10-row time course
        
        result = get_lag_mat(sample_timecourse, lags)
        
        # Expected: first 2 columns = original, next 2 = all zeros (lag too large)
        expected = np.zeros((10, 4))
        expected[:, 0:2] = sample_timecourse
        # The lag 11 columns should remain zeros since the lag is out of bounds
        
        assert result.shape == (10, 4)
        assert np.array_equal(result, expected)
    
    def test_get_lag_mat_mixed_valid_invalid_lags(self, sample_timecourse):
        """Test with a mix of valid and invalid lags"""
        lags = [0, 5, 10, 15]  # Lags 10 and 15 are >= the 10-row time course length
        
        result = get_lag_mat(sample_timecourse, lags)
        
        # Expected: first 2 columns = original, next 2 = lag 5, next 4 = all zeros (lags too large)
        expected = np.zeros((10, 8))
        expected[:, 0:2] = sample_timecourse
        expected[5:, 2:4] = sample_timecourse[:-5]
        # Columns for lags 10 and 15 should remain zeros
        
        assert result.shape == (10, 8)
        assert np.array_equal(result, expected)
    
    def test_get_lag_mat_exactly_length_lag(self, sample_timecourse):
        """Test with a lag equal to the time course length"""
        lags = [0, 10]  # lag 10 is equal to the 10-row time course length
        
        result = get_lag_mat(sample_timecourse, lags)
        
        # Expected: first 2 columns = original, next 2 = all zeros (lag equal to length)
        expected = np.zeros((10, 4))
        expected[:, 0:2] = sample_timecourse
        # The lag 10 columns should remain zeros since the lag is out of bounds
        
        assert result.shape == (10, 4)
        assert np.array_equal(result, expected)
