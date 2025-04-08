"""
Tests for findviz.viz.analysis.peak_finder module
"""

import pytest
import numpy as np
from findviz.viz.analysis.peak_finder import PeakFinder
from findviz.viz.exception import PeakFinderNoPeaksFoundError


class TestPeakFinder:
    """Test cases for PeakFinder class"""
    
    @pytest.fixture
    def simple_signal(self):
        """Fixture providing a simple signal with clear peaks"""
        # Create a signal with peaks at indices 1, 5, and 9
        return np.array([0.0, 3.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 2.0, 0.0])
    
    @pytest.fixture
    def noisy_signal(self):
        """Fixture providing a noisy signal with peaks"""
        # Base signal
        base = np.zeros(100)
        # Add peaks
        peak_indices = [10, 30, 50, 70, 90]
        peak_heights = [5.0, 3.0, 8.0, 4.0, 6.0]
        for idx, height in zip(peak_indices, peak_heights):
            base[idx] = height
        # Add noise
        np.random.seed(42)  # For reproducibility
        noise = np.random.normal(0, 0.5, 100)
        return base + noise
    
    @pytest.fixture
    def flat_signal(self):
        """Fixture providing a flat signal with no peaks"""
        return np.zeros(50)
    
    def test_initialization_default_parameters(self):
        """Test initialization with default parameters"""
        peak_finder = PeakFinder()
        
        assert peak_finder.zscore is False
        assert peak_finder.peak_distance == 1.0
        assert peak_finder.peak_height is None
        assert peak_finder.peak_prominence is None
        assert peak_finder.peak_width is None
        assert peak_finder.peak_threshold is None
    
    def test_initialization_custom_parameters(self):
        """Test initialization with custom parameters"""
        peak_finder = PeakFinder(
            zscore=True,
            peak_distance=2.0,
            peak_height=1.0,
            peak_prominence=0.5,
            peak_width=1.0,
            peak_threshold=0.2
        )
        
        assert peak_finder.zscore is True
        assert peak_finder.peak_distance == 2.0
        assert peak_finder.peak_height == 1.0
        assert peak_finder.peak_prominence == 0.5
        assert peak_finder.peak_width == 1.0
        assert peak_finder.peak_threshold == 0.2
    
    def test_find_peaks_simple_signal(self, simple_signal):
        """Test finding peaks in a simple signal"""
        peak_finder = PeakFinder()
        peaks = peak_finder.find_peaks(simple_signal)
        
        # Expected peaks at indices 1, 5, and 9
        expected_peaks = np.array([1, 5, 9])
        
        assert np.array_equal(peaks, expected_peaks)
    
    def test_find_peaks_with_minimum_height(self, simple_signal):
        """Test finding peaks with minimum height requirement"""
        # Only include peaks with height >= 3.0
        peak_finder = PeakFinder(peak_height=3.0)
        peaks = peak_finder.find_peaks(simple_signal)
        
        # Expected peaks at indices 1 and 5 (with heights 3.0 and 5.0)
        # Note: SciPy's find_peaks includes peaks that are >= the height parameter
        expected_peaks = np.array([1, 5])
        
        assert np.array_equal(peaks, expected_peaks)
    
    def test_find_peaks_with_minimum_distance(self, simple_signal):
        """Test finding peaks with minimum distance requirement"""
        # Require peaks to be at least 6 samples apart
        peak_finder = PeakFinder(peak_distance=6.0)
        peaks = peak_finder.find_peaks(simple_signal)
        
        # Expected peaks at indices 1 and 9, or 5 and some other index
        # Since the distance between peaks at indices 1 and 9 is 8 (> 6),
        # but the distance between 1 and 5 is only 4 (< 6)
        
        # Check that we have at most 2 peaks
        assert len(peaks) <= 2
        # Check that the distance between any two peaks is at least 6
        if len(peaks) == 2:
            assert abs(peaks[1] - peaks[0]) >= 6
    
    def test_find_peaks_with_zscore(self, noisy_signal):
        """Test finding peaks with z-score normalization"""
        # Without z-score normalization
        peak_finder_no_zscore = PeakFinder(peak_height=4.0)
        peaks_no_zscore = peak_finder_no_zscore.find_peaks(noisy_signal)
        
        # With z-score normalization
        peak_finder_with_zscore = PeakFinder(zscore=True, peak_height=2.0)  # Higher z-scores
        peaks_with_zscore = peak_finder_with_zscore.find_peaks(noisy_signal)
        
        # The specific peaks found might differ, but both should find some peaks
        assert len(peaks_no_zscore) > 0
        assert len(peaks_with_zscore) > 0
    
    def test_find_peaks_with_prominence(self, simple_signal):
        """Test finding peaks with prominence requirement"""
        # Only include peaks with prominence > 4.0
        peak_finder = PeakFinder(peak_prominence=4.0)
        peaks = peak_finder.find_peaks(simple_signal)
        
        # Expected peak at index 5 (height = 5.0, prominence = 5.0)
        expected_peaks = np.array([5])
        
        assert np.array_equal(peaks, expected_peaks)
    
    def test_find_peaks_with_width(self, noisy_signal):
        """Test finding peaks with width requirement"""
        # Create a wider peak
        wide_signal = noisy_signal.copy()
        wide_signal[45:55] = 6.0  # Create a wide peak
        
        # Only include peaks with some width
        peak_finder = PeakFinder(peak_width=3.0)
        peaks = peak_finder.find_peaks(wide_signal)
        
        # Should find the wide peak
        assert any(p in range(45, 55) for p in peaks)
    
    def test_find_peaks_with_threshold(self, simple_signal):
        """Test finding peaks with threshold requirement"""
        # Only include peaks with threshold > 2.0
        peak_finder = PeakFinder(peak_threshold=2.0)
        peaks = peak_finder.find_peaks(simple_signal)
        
        # All peaks (1, 5, 9) are still found because threshold parameter
        # controls vertical distance to neighboring samples, not absolute height
        expected_peaks = np.array([1, 5, 9])
        
        assert np.array_equal(peaks, expected_peaks)
    
    def test_no_peaks_found_error(self, flat_signal):
        """Test that error is raised when no peaks are found"""
        peak_finder = PeakFinder()
        
        with pytest.raises(PeakFinderNoPeaksFoundError):
            peak_finder.find_peaks(flat_signal)
    
    def test_find_peaks_with_combination_of_parameters(self, noisy_signal):
        """Test finding peaks with a combination of parameters"""
        # Use multiple parameters to filter peaks
        peak_finder = PeakFinder(
            zscore=True,
            peak_distance=15.0,
            peak_height=2.0,
            peak_prominence=1.0
        )
        
        peaks = peak_finder.find_peaks(noisy_signal)
        
        # Check that peaks are at least 15 samples apart
        if len(peaks) >= 2:
            peak_distances = np.diff(peaks)
            assert np.all(peak_distances >= 15.0)


