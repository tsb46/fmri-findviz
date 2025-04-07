"""
Tests for findviz.viz.analysis.distance module
"""

import pytest
import numpy as np
from findviz.viz.analysis.distance import Distance


class TestDistance:
    """Test cases for Distance class"""
    
    @pytest.fixture
    def sample_fmri_data(self):
        """Fixture providing sample fMRI data for testing"""
        # Create a 10x5 array simulating fMRI data with 10 timepoints and 5 voxels/regions
        return np.array([
            [1.0, 2.0, 3.0, 4.0, 5.0],    # t=0
            [1.5, 2.5, 3.5, 4.5, 5.5],    # t=1
            [2.0, 3.0, 4.0, 5.0, 6.0],    # t=2
            [2.5, 3.5, 4.5, 5.5, 6.5],    # t=3
            [3.0, 4.0, 5.0, 6.0, 7.0],    # t=4
            [3.5, 4.5, 5.5, 6.5, 7.5],    # t=5
            [4.0, 5.0, 6.0, 7.0, 8.0],    # t=6
            [4.5, 5.5, 6.5, 7.5, 8.5],    # t=7
            [5.0, 6.0, 7.0, 8.0, 9.0],    # t=8
            [5.5, 6.5, 7.5, 8.5, 9.5],    # t=9
        ])
    
    def test_initialization(self):
        """Test initialization with different distance metrics"""
        metrics = ['euclidean', 'cosine', 'correlation', 'cityblock', 'chebyshev']
        
        for metric in metrics:
            distance = Distance(distance_metric=metric)
            assert distance.distance_metric == metric
    
    def test_euclidean_distance(self, sample_fmri_data):
        """Test calculation of Euclidean distance"""
        distance = Distance(distance_metric='euclidean')
        
        # Calculate distance between the first time point and all others
        time_point = 0
        result = distance.calculate_distance(time_point, sample_fmri_data)
        
        # Manually calculate expected distances
        expected = np.array([
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[0]),  # t0 vs t0
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[1]),  # t0 vs t1
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[2]),  # t0 vs t2
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[3]),  # t0 vs t3
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[4]),  # t0 vs t4
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[5]),  # t0 vs t5
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[6]),  # t0 vs t6
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[7]),  # t0 vs t7
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[8]),  # t0 vs t8
            np.linalg.norm(sample_fmri_data[0] - sample_fmri_data[9]),  # t0 vs t9
        ])
        
        assert result.shape == (10,)
        assert np.allclose(result, expected)
    
    def test_cosine_distance(self, sample_fmri_data):
        """Test calculation of cosine distance"""
        distance = Distance(distance_metric='cosine')
        
        # Calculate distance between the middle time point and all others
        time_point = 5
        result = distance.calculate_distance(time_point, sample_fmri_data)
        
        # Expected shape and basic properties
        assert result.shape == (10,)
        # Cosine distance between a point and itself should be 0
        assert np.isclose(result[time_point], 0)
        # Cosine distances should be between 0 and 2
        assert np.all(result >= 0)
        assert np.all(result <= 2)
        
        # Distances should generally increase as we move away from the reference point
        # Test this by checking adjacent pairs of distances
        for i in range(time_point - 1):
            assert result[i] >= result[i + 1]
        
        for i in range(time_point + 1, len(result) - 1):
            assert result[i] <= result[i + 1]
    
    def test_correlation_distance(self, sample_fmri_data):
        """Test calculation of correlation distance"""
        distance = Distance(distance_metric='correlation')
        
        # Calculate distance between the last time point and all others
        time_point = 9
        result = distance.calculate_distance(time_point, sample_fmri_data)
        
        # Expected shape and basic properties
        assert result.shape == (10,)
        # Correlation distance between a point and itself should be 0
        assert np.isclose(result[time_point], 0)
        # Correlation distances should be between 0 and 2
        assert np.all(result >= 0)
        assert np.all(result <= 2)
    
    def test_cityblock_distance(self, sample_fmri_data):
        """Test calculation of Manhattan (cityblock) distance"""
        distance = Distance(distance_metric='cityblock')
        
        # Calculate distance between time point 3 and all others
        time_point = 3
        result = distance.calculate_distance(time_point, sample_fmri_data)
        
        # Manually calculate expected distances
        expected = np.zeros(10)
        for i in range(10):
            expected[i] = np.sum(np.abs(sample_fmri_data[time_point] - sample_fmri_data[i]))
        
        assert result.shape == (10,)
        assert np.allclose(result, expected)
    
    def test_chebyshev_distance(self, sample_fmri_data):
        """Test calculation of Chebyshev distance"""
        distance = Distance(distance_metric='chebyshev')
        
        # Calculate distance between time point 7 and all others
        time_point = 7
        result = distance.calculate_distance(time_point, sample_fmri_data)
        
        # Manually calculate expected distances
        expected = np.zeros(10)
        for i in range(10):
            expected[i] = np.max(np.abs(sample_fmri_data[time_point] - sample_fmri_data[i]))
        
        assert result.shape == (10,)
        assert np.allclose(result, expected)
    
    def test_distance_with_varying_dimensionality(self):
        """Test distance calculation with different array shapes"""
        # Test with different numbers of voxels/regions
        test_cases = [
            np.random.rand(5, 2),   # 5 timepoints, 2 voxels
            np.random.rand(10, 50),  # 10 timepoints, 50 voxels
            np.random.rand(20, 100),  # 20 timepoints, 100 voxels
        ]
        
        distance = Distance(distance_metric='euclidean')
        
        for data in test_cases:
            n_timepoints = data.shape[0]
            time_point = n_timepoints // 2  # Use middle time point
            
            result = distance.calculate_distance(time_point, data)
            
            # Check shape and self-distance
            assert result.shape == (n_timepoints,)
            assert np.isclose(result[time_point], 0)
    
    def test_distance_trends(self, sample_fmri_data):
        """Test that distance increases with time separation"""
        distance = Distance(distance_metric='euclidean')
        
        # Calculate distances from time point 0 to all others
        result = distance.calculate_distance(0, sample_fmri_data)
        
        # Distances should generally increase as we move away from the reference point
        # This is true for our synthetic data where values increase linearly
        assert np.all(result[1:] > result[:-1])
    
    def test_symmetry_property(self, sample_fmri_data):
        """Test that distance is symmetric: d(a,b) = d(b,a)"""
        distance = Distance(distance_metric='euclidean')
        
        # Calculate distance from point 2 to all others
        forward_distances = distance.calculate_distance(2, sample_fmri_data)
        
        # Calculate distance from point 6 to all others
        backward_distances = distance.calculate_distance(6, sample_fmri_data)
        
        # The distance from 2 to 6 should equal the distance from 6 to 2
        assert np.isclose(forward_distances[6], backward_distances[2])

