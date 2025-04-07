"""
Tests for findviz.viz.analysis.correlate module
"""

import pytest
import numpy as np
from findviz.viz.analysis.correlate import Correlate
from findviz.viz.exception import ParameterInputError


class TestCorrelate:
    """Test cases for Correlate class"""
    
    @pytest.fixture
    def sample_fmri_data(self):
        """Fixture providing sample fMRI data for testing"""
        # Create a sample fMRI data array (10 timepoints, 3 voxels)
        return np.array([
            [1.0, 2.0, 3.0],    # t=0
            [2.0, 3.0, 4.0],    # t=1
            [3.0, 4.0, 5.0],    # t=2
            [4.0, 5.0, 6.0],    # t=3
            [5.0, 6.0, 7.0],    # t=4
            [6.0, 7.0, 8.0],    # t=5
            [7.0, 8.0, 9.0],    # t=6
            [8.0, 9.0, 10.0],   # t=7
            [9.0, 10.0, 11.0],  # t=8
            [10.0, 11.0, 12.0], # t=9
        ])
    
    @pytest.fixture
    def sample_timecourse(self):
        """Fixture providing a sample time course for testing"""
        # Create a sample time course that correlates well with the sample_fmri_data
        return [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    
    @pytest.fixture
    def sample_delayed_timecourse(self):
        """Fixture providing a delayed sample time course for testing lag effects"""
        # Create a sample time course delayed by 2 time points
        return [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    
    def test_initialization_valid_parameters(self):
        """Test initialization with valid parameters"""
        # Test initialization with valid parameters
        correlate = Correlate(negative_lag=-2, positive_lag=2, time_length=20)
        
        assert correlate.negative_lag == -2
        assert correlate.positive_lag == 2
        assert correlate.time_length == 20
        assert np.array_equal(correlate.lags, np.array([-2, -1, 0, 1, 2]))
    
    def test_initialization_invalid_negative_lag(self):
        """Test initialization with invalid negative lag (positive value)"""
        with pytest.raises(ParameterInputError, match="Negative lag must be negative"):
            Correlate(negative_lag=2, positive_lag=2, time_length=20)
    
    def test_initialization_invalid_positive_lag(self):
        """Test initialization with invalid positive lag (negative value)"""
        with pytest.raises(ParameterInputError, match="Positive lag must be positive"):
            Correlate(negative_lag=-2, positive_lag=-2, time_length=20)
    
    def test_initialization_negative_lag_too_large(self):
        """Test initialization with negative lag too large for time length"""
        with pytest.raises(ParameterInputError, match="Negative lag must be less than half the time length"):
            Correlate(negative_lag=-11, positive_lag=2, time_length=20)
    
    def test_initialization_positive_lag_too_large(self):
        """Test initialization with positive lag too large for time length"""
        with pytest.raises(ParameterInputError, match="Positive lag must be less than half the time length"):
            Correlate(negative_lag=-2, positive_lag=11, time_length=20)
    
    def test_correlate_no_lag(self, sample_fmri_data, sample_timecourse):
        """Test correlation with no lag (only lag 0)"""
        correlate = Correlate(negative_lag=0, positive_lag=0, time_length=10)
        result = correlate.correlate(sample_fmri_data, sample_timecourse)
        
        # Expected: 1 lag × 3 voxels correlation matrix
        # With perfectly linear increasing data, we should get high correlations
        assert result.shape == (1, 3)
        assert np.all(result > 0.99)  # Should be very high correlations
        assert np.all(result <= 1.0)  # Correlation should not exceed 1.0
    
    def test_correlate_positive_lags(self, sample_fmri_data, sample_timecourse):
        """Test correlation with positive lags"""
        correlate = Correlate(negative_lag=0, positive_lag=2, time_length=10)
        result = correlate.correlate(sample_fmri_data, sample_timecourse)
        
        # Expected: 3 lags × 3 voxels correlation matrix
        assert result.shape == (3, 3)
        
        # With this dataset, lag 0 will have highest correlation
        # Since our data is perfectly correlated, we can't guarantee strict inequality
        # Instead, we check that lag 0 has correlation very close to 1
        assert np.all(result[0, :] > 0.99)  # Lag 0 should have very high correlation
        assert np.all(result <= 1.0)  # Correlations should not exceed 1.0
        assert np.all(result >= -1.0)  # Correlations should not be less than -1.0
    
    def test_correlate_negative_lags(self, sample_fmri_data, sample_timecourse):
        """Test correlation with negative lags"""
        correlate = Correlate(negative_lag=-2, positive_lag=0, time_length=10)
        result = correlate.correlate(sample_fmri_data, sample_timecourse)
        
        # Expected: 3 lags × 3 voxels correlation matrix
        assert result.shape == (3, 3)
        
        # With this dataset, lag 0 will have highest correlation
        # Since our data is perfectly correlated, we check appropriate values
        assert np.all(result[2, :] > 0.99)  # Lag 0 should have very high correlation
        assert np.all(result <= 1.0)  # Correlations should not exceed 1.0
        assert np.all(result >= -1.0)  # Correlations should not be less than -1.0
    
    def test_correlate_mixed_lags(self, sample_fmri_data, sample_timecourse):
        """Test correlation with both negative and positive lags"""
        correlate = Correlate(negative_lag=-2, positive_lag=2, time_length=10)
        result = correlate.correlate(sample_fmri_data, sample_timecourse)
        
        # Expected: 5 lags × 3 voxels correlation matrix
        assert result.shape == (5, 3)
        
        # Lag 0 should have highest correlation
        # Each row represents a lag: [-2, -1, 0, 1, 2]
        lag_0_idx = 2  # Index of lag 0 in the result array
        
        # Check that lag 0 has very high correlation (close to 1)
        assert np.all(result[lag_0_idx, :] > 0.99)
        # Ensure all correlations are within valid range
        assert np.all(result <= 1.0)
        assert np.all(result >= -1.0)
    
    def test_correlate_with_delayed_timecourse(self, sample_fmri_data, sample_delayed_timecourse):
        """Test correlation with delayed time course to verify lag detection"""
        correlate = Correlate(negative_lag=-3, positive_lag=3, time_length=10)
        result = correlate.correlate(sample_fmri_data, sample_delayed_timecourse)
        
        # Expected: 7 lags × 3 voxels correlation matrix
        assert result.shape == (7, 3)
        
        # Since the time course is delayed by 2 time points, 
        # we expect higher correlation at positive lags (lag 0 or greater)
        
        # For each voxel, find the lag with maximum correlation
        for col in range(3):
            # Find the lag with the maximum correlation for this voxel
            max_lag_idx = np.argmax(result[:, col])
            
            # The max correlation should be at a non-negative lag (index >= 3)
            # where index 3 corresponds to lag 0
            assert max_lag_idx >= 3
            
        # Ensure all correlations are within valid range
        assert np.all(result <= 1.0)
        assert np.all(result >= -1.0)
    
    def test_correlate_with_anticorrelated_timecourse(self, sample_fmri_data):
        """Test correlation with anticorrelated time course"""
        # Create an anticorrelated time course
        anticorrelated_timecourse = [10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
        
        correlate = Correlate(negative_lag=0, positive_lag=0, time_length=10)
        result = correlate.correlate(sample_fmri_data, anticorrelated_timecourse)
        
        # Expected: 1 lag × 3 voxels correlation matrix with strong negative correlations
        assert result.shape == (1, 3)
        assert np.all(result < -0.99)  # Should be very strong negative correlations
        assert np.all(result >= -1.0)  # Correlations should not be less than -1.0
    
    def test_correlate_edge_case_empty_fmri_data(self, sample_timecourse):
        """Test correlation with empty fMRI data"""
        # Create empty fMRI data (0 voxels)
        empty_fmri_data = np.zeros((10, 0))
        
        correlate = Correlate(negative_lag=-1, positive_lag=1, time_length=10)
        result = correlate.correlate(empty_fmri_data, sample_timecourse)
        
        # Expected: 3 lags × 0 voxels correlation matrix
        assert result.shape == (3, 0)
    
    def test_validate_edge_cases(self):
        """Test edge cases for parameter validation"""
        # Test with lag exactly at half time length
        correlate = Correlate(negative_lag=-5, positive_lag=5, time_length=10)
        assert correlate.negative_lag == -5
        assert correlate.positive_lag == 5
        
        # Test with zero lags
        correlate = Correlate(negative_lag=0, positive_lag=0, time_length=10)
        assert np.array_equal(correlate.lags, np.array([0]))


