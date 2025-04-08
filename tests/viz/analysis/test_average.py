"""
Tests for findviz.viz.analysis.average module
"""

import pytest
import numpy as np
from findviz.viz.analysis.average import WindowAverage
from findviz.viz.exception import ParameterInputError


class TestWindowAverage:
    """Test cases for WindowAverage class"""
    
    @pytest.fixture
    def sample_fmri_data(self):
        """Fixture providing sample fMRI data for testing"""
        # Create a 20x3 array simulating fMRI data with 20 timepoints and 3 voxels/regions
        return np.array([
            [1.0, 2.0, 3.0],     # t=0
            [1.5, 2.5, 3.5],     # t=1
            [2.0, 3.0, 4.0],     # t=2
            [2.5, 3.5, 4.5],     # t=3
            [3.0, 4.0, 5.0],     # t=4
            [3.5, 4.5, 5.5],     # t=5
            [4.0, 5.0, 6.0],     # t=6
            [4.5, 5.5, 6.5],     # t=7
            [5.0, 6.0, 7.0],     # t=8
            [5.5, 6.5, 7.5],     # t=9
            [6.0, 7.0, 8.0],     # t=10
            [6.5, 7.5, 8.5],     # t=11
            [7.0, 8.0, 9.0],     # t=12
            [7.5, 8.5, 9.5],     # t=13
            [8.0, 9.0, 10.0],    # t=14
            [8.5, 9.5, 10.5],    # t=15
            [9.0, 10.0, 11.0],   # t=16
            [9.5, 10.5, 11.5],   # t=17
            [10.0, 11.0, 12.0],  # t=18
            [10.5, 11.5, 12.5],  # t=19
        ])
    
    def test_valid_initialization(self):
        """Test valid initialization of WindowAverage"""
        window_avg = WindowAverage(left_edge=-2, right_edge=2, n_timepoints=20)
        
        assert window_avg.left_edge == -2
        assert window_avg.right_edge == 2
        assert window_avg.n_timepoints == 20
    
    def test_initialization_invalid_left_edge(self):
        """Test initialization with invalid left edge (positive value)"""
        with pytest.raises(ParameterInputError, match="Left edge must be negative"):
            WindowAverage(left_edge=2, right_edge=2, n_timepoints=20)
    
    def test_initialization_invalid_right_edge(self):
        """Test initialization with invalid right edge (negative value)"""
        with pytest.raises(ParameterInputError, match="Right edge must be positive"):
            WindowAverage(left_edge=-2, right_edge=-2, n_timepoints=20)
    
    def test_initialization_left_edge_too_large(self):
        """Test initialization with left edge too large for time length"""
        with pytest.raises(ParameterInputError, match="Left edge must be less than half the time length"):
            WindowAverage(left_edge=-11, right_edge=2, n_timepoints=20)
    
    def test_initialization_right_edge_too_large(self):
        """Test initialization with right edge too large for time length"""
        with pytest.raises(ParameterInputError, match="Right edge must be less than half the time length"):
            WindowAverage(left_edge=-2, right_edge=11, n_timepoints=20)
    
    def test_average_single_marker(self, sample_fmri_data):
        """Test averaging around a single marker"""
        window_avg = WindowAverage(left_edge=-2, right_edge=2, n_timepoints=20)
        result = window_avg.average(sample_fmri_data, annotation_markers=[10])
        
        # Expected: 5 timepoints centered at index 10
        expected = np.array([
            [5.0, 6.0, 7.0],    # t=8 (10-2)
            [5.5, 6.5, 7.5],    # t=9 (10-1)
            [6.0, 7.0, 8.0],    # t=10 (center)
            [6.5, 7.5, 8.5],    # t=11 (10+1)
            [7.0, 8.0, 9.0],    # t=12 (10+2)
        ])
        
        assert result.shape == (5, 3)
        assert np.allclose(result, expected)
    
    def test_average_multiple_markers(self, sample_fmri_data):
        """Test averaging around multiple markers"""
        window_avg = WindowAverage(left_edge=-2, right_edge=2, n_timepoints=20)
        result = window_avg.average(sample_fmri_data, annotation_markers=[5, 10, 15])
        
        # Expected: average of 3 windows centered at indices 5, 10, and 15
        window1 = np.array([
            [2.0, 3.0, 4.0],    # t=3 (5-2)
            [2.5, 3.5, 4.5],    # t=4 (5-1)
            [3.0, 4.0, 5.0],    # t=5 (center)
            [3.5, 4.5, 5.5],    # t=6 (5+1)
            [4.0, 5.0, 6.0],    # t=7 (5+2)
        ])
        window2 = np.array([
            [5.0, 6.0, 7.0],    # t=8 (10-2)
            [5.5, 6.5, 7.5],    # t=9 (10-1)
            [6.0, 7.0, 8.0],    # t=10 (center)
            [6.5, 7.5, 8.5],    # t=11 (10+1)
            [7.0, 8.0, 9.0],    # t=12 (10+2)
        ])
        window3 = np.array([
            [8.0, 9.0, 10.0],   # t=13 (15-2)
            [8.5, 9.5, 10.5],   # t=14 (15-1)
            [9.0, 10.0, 11.0],  # t=15 (center)
            [9.5, 10.5, 11.5],  # t=16 (15+1)
            [10.0, 11.0, 12.0], # t=17 (15+2)
        ])
        expected = (window1 + window2 + window3) / 3
        
        assert result.shape == (5, 3)
        assert np.allclose(result, expected)
    
    def test_average_marker_near_edge(self, sample_fmri_data):
        """Test averaging with marker near the edge of the data"""
        window_avg = WindowAverage(left_edge=-2, right_edge=2, n_timepoints=20)
        result = window_avg.average(sample_fmri_data, annotation_markers=[1])
        
        # Expected: 5 timepoints centered at index 1, with NaN padding for out-of-bounds
        expected = np.array([
            [np.nan, np.nan, np.nan],  # t=-1 (out of bounds)
            [1.0, 2.0, 3.0],           # t=0 (1-1)
            [1.5, 2.5, 3.5],           # t=1 (center)
            [2.0, 3.0, 4.0],           # t=2 (1+1)
            [2.5, 3.5, 4.5],           # t=3 (1+2)
        ])
        
        assert result.shape == (5, 3)
        assert np.allclose(result, expected, equal_nan=True)
    
    def test_average_asymmetric_window(self, sample_fmri_data):
        """Test averaging with asymmetric window (left_edge != -right_edge)"""
        window_avg = WindowAverage(left_edge=-1, right_edge=3, n_timepoints=20)
        result = window_avg.average(sample_fmri_data, annotation_markers=[10])
        
        # Expected: 5 timepoints from index 9 to 13
        expected = np.array([
            [5.5, 6.5, 7.5],    # t=9 (10-1)
            [6.0, 7.0, 8.0],    # t=10 (center)
            [6.5, 7.5, 8.5],    # t=11 (10+1)
            [7.0, 8.0, 9.0],    # t=12 (10+2)
            [7.5, 8.5, 9.5],    # t=13 (10+3)
        ])
        
        assert result.shape == (5, 3)
        assert np.allclose(result, expected)
    
    def test_average_zero_width_window(self, sample_fmri_data):
        """Test averaging with zero-width window (left_edge=right_edge=0)"""
        window_avg = WindowAverage(left_edge=0, right_edge=0, n_timepoints=20)
        result = window_avg.average(sample_fmri_data, annotation_markers=[10])
        
        # Expected: Just the center point
        expected = np.array([[6.0, 7.0, 8.0]])  # t=10
        
        assert result.shape == (1, 3)
        assert np.allclose(result, expected)
    
    def test_average_multiple_markers_with_nan(self, sample_fmri_data):
        """Test averaging with multiple markers where some windows contain NaN values"""
        window_avg = WindowAverage(left_edge=-2, right_edge=2, n_timepoints=20)
        result = window_avg.average(sample_fmri_data, annotation_markers=[1, 10, 18])
        
        # Windows will have NaN values for the first and last markers
        # nanmean should properly average, ignoring NaN values
        window1 = np.array([
            [np.nan, np.nan, np.nan],  # t=-1 (out of bounds)
            [1.0, 2.0, 3.0],           # t=0
            [1.5, 2.5, 3.5],           # t=1 (center)
            [2.0, 3.0, 4.0],           # t=2
            [2.5, 3.5, 4.5],           # t=3
        ])
        window2 = np.array([
            [5.0, 6.0, 7.0],           # t=8
            [5.5, 6.5, 7.5],           # t=9
            [6.0, 7.0, 8.0],           # t=10 (center)
            [6.5, 7.5, 8.5],           # t=11
            [7.0, 8.0, 9.0],           # t=12
        ])
        window3 = np.array([
            [9.0, 10.0, 11.0],         # t=16
            [9.5, 10.5, 11.5],         # t=17
            [10.0, 11.0, 12.0],        # t=18 (center)
            [10.5, 11.5, 12.5],        # t=19
            [np.nan, np.nan, np.nan],  # t=20 (out of bounds)
        ])
        
        # Calculate expected result manually for each element
        expected = np.zeros((5, 3))
        for i in range(5):
            for j in range(3):
                values = [window1[i, j], window2[i, j], window3[i, j]]
                valid_values = [v for v in values if not np.isnan(v)]
                expected[i, j] = sum(valid_values) / len(valid_values)
        
        assert result.shape == (5, 3)
        assert np.allclose(result, expected, equal_nan=True)
    
    def test_get_timepoints(self):
        """Test getting timepoints for the window"""
        window_avg = WindowAverage(left_edge=-2, right_edge=2, n_timepoints=20)
        timepoints = window_avg.get_timepoints()
        
        expected = [-2, -1, 0, 1, 2]
        
        assert timepoints == expected
    
    def test_get_timepoints_asymmetric(self):
        """Test getting timepoints for asymmetric window"""
        window_avg = WindowAverage(left_edge=-1, right_edge=3, n_timepoints=20)
        timepoints = window_avg.get_timepoints()
        
        expected = [-1, 0, 1, 2, 3]
        
        assert timepoints == expected
    
    def test_get_timepoints_zero_width(self):
        """Test getting timepoints for zero-width window"""
        window_avg = WindowAverage(left_edge=0, right_edge=0, n_timepoints=20)
        timepoints = window_avg.get_timepoints()
        
        expected = [0]
        
        assert timepoints == expected

