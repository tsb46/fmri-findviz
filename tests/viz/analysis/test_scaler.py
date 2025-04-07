"""
Tests for findviz.viz.analysis.scaler module
"""

import pytest
import numpy as np
from findviz.viz.analysis.scaler import SignalScaler, SignalShifter


class TestSignalScaler:
    """Test cases for SignalScaler class"""
    
    @pytest.fixture
    def sample_signals(self):
        """Fixture providing sample signals for testing"""
        return [
            [1.0, 2.0, 3.0, 4.0, 5.0],  # mean = 3.0
            [10.0, 20.0, 30.0, 40.0, 50.0],  # mean = 30.0
            [0.0, 0.0, 0.0, 0.0, 0.0],  # mean = 0.0
        ]
    
    @pytest.fixture
    def scaler(self):
        """Fixture providing a SignalScaler instance"""
        return SignalScaler()
    
    def test_init(self, scaler):
        """Test initialization of SignalScaler"""
        assert scaler.scale_history == []
    
    def test_clear_history(self, scaler):
        """Test clearing scale history"""
        # Add some history
        scaler.scale_history = [1.5, 2.0, 0.5]
        scaler.clear_history()
        assert scaler.scale_history == []
    
    def test_set_history(self, scaler):
        """Test setting scale history directly"""
        history = [1.5, 2.0, 0.5]
        scaler.set_history(history)
        assert scaler.scale_history == history
    
    def test_scale_positive_unit(self, scaler, sample_signals):
        """Test scaling with positive scale unit"""
        scale_unit = 0.5  # Should result in scale_factor = 1.5
        scaled_signals = scaler.scale(sample_signals, scale_unit)
        
        # Check scale history updated
        assert len(scaler.scale_history) == 1
        assert scaler.scale_history[0] == 1.5
        
        # Check each signal was scaled correctly
        for i, (original, scaled) in enumerate(zip(sample_signals, scaled_signals)):
            mean = np.mean(original)
            # Check the mean is preserved
            assert np.isclose(np.mean(scaled), mean)
            # Check the scaling was applied correctly
            for orig_val, scaled_val in zip(original, scaled):
                expected = 1.5 * (orig_val - mean) + mean
                assert np.isclose(scaled_val, expected)
    
    def test_scale_negative_unit(self, scaler, sample_signals):
        """Test scaling with negative scale unit"""
        scale_unit = -0.5  # Should result in scale_factor = 1/(1+0.5) = 2/3
        scaled_signals = scaler.scale(sample_signals, scale_unit)
        
        # Check scale history updated
        assert len(scaler.scale_history) == 1
        assert np.isclose(scaler.scale_history[0], 2/3)
        
        # Check each signal was scaled correctly
        for i, (original, scaled) in enumerate(zip(sample_signals, scaled_signals)):
            mean = np.mean(original)
            # Check the mean is preserved
            assert np.isclose(np.mean(scaled), mean)
            # Check the scaling was applied correctly
            for orig_val, scaled_val in zip(original, scaled):
                expected = (2/3) * (orig_val - mean) + mean
                assert np.isclose(scaled_val, expected)
    
    def test_scale_zero_unit(self, scaler, sample_signals):
        """Test scaling with zero scale unit (no change)"""
        scale_unit = 0.0  # Should result in scale_factor = 1.0
        scaled_signals = scaler.scale(sample_signals, scale_unit)
        
        # Check scale history updated
        assert len(scaler.scale_history) == 1
        assert scaler.scale_history[0] == 1.0
        
        # Check signals remain unchanged
        for i, (original, scaled) in enumerate(zip(sample_signals, scaled_signals)):
            assert np.allclose(original, scaled)
    
    def test_reverse_single_scaling(self, scaler, sample_signals):
        """Test reversing a single scaling operation"""
        # First scale the signals
        scale_unit = 0.5  # scale_factor = 1.5
        scaled_signals = scaler.scale(sample_signals, scale_unit)
        
        # Now reverse the scaling
        reversed_signals = scaler.reverse(scaled_signals)
        
        # Check scale history got updated
        assert len(scaler.scale_history) == 0
        
        # Check signals are back to original
        for original, reversed_signal in zip(sample_signals, reversed_signals):
            assert np.allclose(original, reversed_signal, rtol=1e-10, atol=1e-10)
    
    def test_reverse_no_history(self, scaler, sample_signals, capfd):
        """Test reversing when no scaling has been applied"""
        # Try to reverse when no scaling has been done
        reversed_signals = scaler.reverse(sample_signals)
        
        # Check warning message
        out, _ = capfd.readouterr()
        assert "No transformations to reverse" in out
        
        # Check signals remain unchanged
        for original, reversed_signal in zip(sample_signals, reversed_signals):
            assert np.array_equal(original, reversed_signal)
    
    def test_reset_multiple_scalings(self, scaler, sample_signals):
        """Test resetting after multiple scaling operations"""
        # Apply multiple scalings
        scaled1 = scaler.scale(sample_signals, 0.5)  # scale_factor = 1.5
        scaled2 = scaler.scale(scaled1, -0.2)  # scale_factor = 1/(1+0.2) = 0.833...
        
        # Reset to original
        reset_signals = scaler.reset(scaled2)
        
        # Check scale history is empty
        assert len(scaler.scale_history) == 0
        
        # Check signals are back to original
        for original, reset_signal in zip(sample_signals, reset_signals):
            assert np.allclose(original, reset_signal, rtol=1e-10, atol=1e-10)
    
    def test_reset_no_history(self, scaler, sample_signals):
        """Test resetting when no scaling has been applied"""
        # Try to reset when no scaling has been done
        reset_signals = scaler.reset(sample_signals)
        
        # Check signals remain unchanged
        for original, reset_signal in zip(sample_signals, reset_signals):
            assert np.array_equal(original, reset_signal)
    
    def test_reset_error_handling(self, scaler, sample_signals):
        """Test error handling in reset if history isn't properly cleared"""
        # Mock a situation where history isn't properly cleared
        def mock_reverse(signals):
            # Don't pop from history, simulating a bug
            return signals
        
        # Apply scaling
        scaled = scaler.scale(sample_signals, 0.5)
        
        # Save original reverse method and replace with mock
        original_reverse = scaler.reverse
        scaler.reverse = mock_reverse
        
        # Reset should raise ValueError
        with pytest.raises(ValueError, match="Scale history is not empty after resetting"):
            scaler.reset(scaled)
        
        # Restore original method
        scaler.reverse = original_reverse


class TestSignalShifter:
    """Test cases for SignalShifter class"""
    
    @pytest.fixture
    def sample_signals(self):
        """Fixture providing sample signals for testing"""
        return [
            [1.0, 2.0, 3.0, 4.0, 5.0],
            [10.0, 20.0, 30.0, 40.0, 50.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    
    @pytest.fixture
    def shifter(self):
        """Fixture providing a SignalShifter instance"""
        return SignalShifter()
    
    def test_init(self, shifter):
        """Test initialization of SignalShifter"""
        assert shifter.shift_history == []
    
    def test_clear_history(self, shifter):
        """Test clearing shift history"""
        # Add some history
        shifter.shift_history = [5.0, -3.0, 2.5]
        shifter.clear_history()
        assert shifter.shift_history == []
    
    def test_set_history(self, shifter):
        """Test setting shift history directly"""
        history = [5.0, -3.0, 2.5]
        shifter.set_history(history)
        assert shifter.shift_history == history
    
    def test_shift_positive_amount(self, shifter, sample_signals):
        """Test shifting with positive amount"""
        shift_amount = 10.0
        shifted_signals = shifter.shift(sample_signals, shift_amount)
        
        # Check shift history updated
        assert len(shifter.shift_history) == 1
        assert shifter.shift_history[0] == 10.0
        
        # Check each signal was shifted correctly
        for original, shifted in zip(sample_signals, shifted_signals):
            for orig_val, shifted_val in zip(original, shifted):
                assert shifted_val == orig_val + 10.0
    
    def test_shift_negative_amount(self, shifter, sample_signals):
        """Test shifting with negative amount"""
        shift_amount = -5.0
        shifted_signals = shifter.shift(sample_signals, shift_amount)
        
        # Check shift history updated
        assert len(shifter.shift_history) == 1
        assert shifter.shift_history[0] == -5.0
        
        # Check each signal was shifted correctly
        for original, shifted in zip(sample_signals, shifted_signals):
            for orig_val, shifted_val in zip(original, shifted):
                assert shifted_val == orig_val - 5.0
    
    def test_shift_zero_amount(self, shifter, sample_signals):
        """Test shifting with zero amount (no change)"""
        shift_amount = 0.0
        shifted_signals = shifter.shift(sample_signals, shift_amount)
        
        # Check shift history updated
        assert len(shifter.shift_history) == 1
        assert shifter.shift_history[0] == 0.0
        
        # Check signals remain unchanged
        for original, shifted in zip(sample_signals, shifted_signals):
            assert np.array_equal(original, shifted)
    
    def test_reverse_single_shifting(self, shifter, sample_signals):
        """Test reversing a single shifting operation"""
        # First shift the signals
        shift_amount = 7.5
        shifted_signals = shifter.shift(sample_signals, shift_amount)
        
        # Now reverse the shifting
        reversed_signals = shifter.reverse(shifted_signals)
        
        # Check shift history got updated
        assert len(shifter.shift_history) == 0
        
        # Check signals are back to original
        for original, reversed_signal in zip(sample_signals, reversed_signals):
            assert np.array_equal(original, reversed_signal)
    
    def test_reverse_no_history(self, shifter, sample_signals, capfd):
        """Test reversing when no shifting has been applied"""
        # Try to reverse when no shifting has been done
        reversed_signals = shifter.reverse(sample_signals)
        
        # Check warning message
        out, _ = capfd.readouterr()
        assert "No transformations to reverse" in out
        
        # Check signals remain unchanged
        for original, reversed_signal in zip(sample_signals, reversed_signals):
            assert np.array_equal(original, reversed_signal)
    
    def test_reset_multiple_shiftings(self, shifter, sample_signals):
        """Test resetting after multiple shifting operations"""
        # Apply multiple shiftings
        shifted1 = shifter.shift(sample_signals, 5.0)
        shifted2 = shifter.shift(shifted1, -2.0)
        
        # Reset to original
        reset_signals = shifter.reset(shifted2)
        
        # Check shift history is empty
        assert len(shifter.shift_history) == 0
        
        # Check signals are back to original
        for original, reset_signal in zip(sample_signals, reset_signals):
            assert np.array_equal(original, reset_signal)
    
    def test_reset_no_history(self, shifter, sample_signals):
        """Test resetting when no shifting has been applied"""
        # Try to reset when no shifting has been done
        reset_signals = shifter.reset(sample_signals)
        
        # Check signals remain unchanged
        for original, reset_signal in zip(sample_signals, reset_signals):
            assert np.array_equal(original, reset_signal)
    
    def test_reset_error_handling(self, shifter, sample_signals):
        """Test error handling in reset if history isn't properly cleared"""
        # Mock a situation where history isn't properly cleared
        def mock_reverse(signals):
            # Don't pop from history, simulating a bug
            return signals
        
        # Apply shifting
        shifted = shifter.shift(sample_signals, 5.0)
        
        # Save original reverse method and replace with mock
        original_reverse = shifter.reverse
        shifter.reverse = mock_reverse
        
        # Reset should raise ValueError
        with pytest.raises(ValueError, match="Shift history is not empty after resetting"):
            shifter.reset(shifted)
        
        # Restore original method
        shifter.reverse = original_reverse

