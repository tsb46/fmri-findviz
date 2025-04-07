"""Tests for preprocessing utility functions"""
import pytest
import numpy as np
import nibabel as nib

from findviz.viz.preprocess.utils import (
    butterworth_filter,
    tr_to_hz,
    linear_detrend,
    mean_center,
    nifti_smooth,
    z_score
)


@pytest.fixture
def sample_timeseries():
    """Create a sample timeseries for testing"""
    # Create a simple sinusoidal signal with noise
    t = np.linspace(0, 5, 500)
    signal = np.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz signal
    noise = np.random.normal(0, 0.3, len(t))
    return signal + noise


@pytest.fixture
def sample_nifti():
    """Create a sample 4D NIFTI image for testing"""
    # Create random 4D data (10x10x10x500)
    data = np.random.rand(10, 10, 10, 500)
    return nib.Nifti1Image(data, np.eye(4))


def test_butterworth_filter(sample_timeseries):
    """Test Butterworth filter functionality"""
    # Test with typical parameters
    # butterworth filter operates on time course in place, create copy
    sample_timeseries_copy = sample_timeseries.copy()
    filtered = butterworth_filter(
        sample_timeseries_copy,
        sf=5.0,  # 1 Hz sampling frequency
        low_cutoff=0.1,
        high_cutoff=1.0
    )
    
    assert filtered.shape == sample_timeseries.shape
    assert not np.array_equal(filtered, sample_timeseries)  # Should modify signal
    
    # Test with different filter order
    filtered_higher_order = butterworth_filter(
        sample_timeseries,
        sf=10.0,
        low_cutoff=0.1,
        high_cutoff=1.0,
        order=8
    )
    assert filtered_higher_order.shape == sample_timeseries.shape
    assert not np.array_equal(filtered_higher_order, filtered)  # Should be different


def test_tr_to_hz():
    """Test TR to Hz conversion"""
    assert tr_to_hz(2.0) == 0.5  # 2s TR = 0.5 Hz
    assert tr_to_hz(1.0) == 1.0  # 1s TR = 1 Hz
    assert tr_to_hz(0.5) == 2.0  # 0.5s TR = 2 Hz


def test_linear_detrend(sample_timeseries):
    """Test linear detrending"""
    # Add linear trend to data
    trend = np.linspace(0, 5, len(sample_timeseries))
    data_with_trend = sample_timeseries + trend
    
    # Detrend
    detrended = linear_detrend(data_with_trend)
    
    assert detrended.shape == data_with_trend.shape
    assert not np.array_equal(detrended, data_with_trend)
    
    # Check if trend is removed (mean should be close to zero)
    assert np.abs(detrended.mean()) < 0.1
    
    # Test with different axis
    data_2d = np.vstack([data_with_trend, data_with_trend])
    detrended_2d = linear_detrend(data_2d, axis=1)
    assert detrended_2d.shape == data_2d.shape


def test_mean_center():
    """Test mean centering"""
    # Test 1D array
    data_1d = np.array([1, 2, 3, 4, 5])
    centered_1d = mean_center(data_1d)
    assert np.allclose(centered_1d.mean(), 0)
    assert centered_1d.shape == data_1d.shape
    
    # Test 2D array
    data_2d = np.array([[1, 2, 3], [4, 5, 6]])
    
    # Test along axis 0
    centered_2d_0 = mean_center(data_2d, axis=0)
    assert np.allclose(centered_2d_0.mean(axis=0), 0)
    
    # Test along axis 1
    centered_2d_1 = mean_center(data_2d, axis=1)
    assert np.allclose(centered_2d_1.mean(axis=1), 0)


def test_nifti_smooth(sample_nifti):
    """Test NIFTI smoothing"""
    # Test with typical FWHM
    smoothed = nifti_smooth(sample_nifti, fwhm=6.0)
    
    assert isinstance(smoothed, nib.Nifti1Image)
    assert smoothed.shape == sample_nifti.shape
    assert not np.array_equal(
        smoothed.get_fdata(),
        sample_nifti.get_fdata()
    )  # Should modify data
    
    # Test with different FWHM
    smoothed_more = nifti_smooth(sample_nifti, fwhm=8.0)
    assert not np.array_equal(
        smoothed_more.get_fdata(),
        smoothed.get_fdata()
    )  # Should be different


def test_z_score():
    """Test z-score normalization"""
    # Test 1D array
    data_1d = np.array([1, 2, 3, 4, 5])
    z_scored_1d = z_score(data_1d)
    assert np.allclose(z_scored_1d.mean(), 0)
    assert np.allclose(z_scored_1d.std(), 1)
    
    # Test 2D array
    data_2d = np.array([[1, 2, 3], [4, 5, 6]])
    
    # Test along axis 0
    z_scored_2d_0 = z_score(data_2d, axis=0)
    assert np.allclose(z_scored_2d_0.mean(axis=0), 0)
    assert np.allclose(z_scored_2d_0.std(axis=0), 1)
    
    # Test along axis 1
    z_scored_2d_1 = z_score(data_2d, axis=1)
    assert np.allclose(z_scored_2d_1.mean(axis=1), 0)
    assert np.allclose(z_scored_2d_1.std(axis=1), 1)
    
    # Test with constant values
    constant_data = np.ones(10)
    z_scored_constant = z_score(constant_data)
    assert np.allclose(z_scored_constant, 0)  # Should handle constant values


def test_edge_cases():
    """Test edge cases for preprocessing functions"""
    # Test empty array
    empty = np.array([])
    # should raise RuntimeWarning due to division by zero
    with pytest.warns(RuntimeWarning):
        z_score(empty)
    
    # Test single value
    single = np.array([1.0])
    z_scored_single = z_score(single)
    assert np.isclose(z_scored_single[0], 0.0)
    
    # Test NaN handling
    data_with_nan = np.array([1, 2, np.nan, 4, 5])
    z_scored_nan = z_score(data_with_nan)
    assert not np.any(np.isnan(z_scored_nan))
