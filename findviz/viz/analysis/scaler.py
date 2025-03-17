# Classes for scaling time courses via a constant or scale shift
from typing import List, Union

import numpy as np

class SignalScaler:
    """Class for scaling time courses via a scale shift. Tracks 
    history of transformations and allows for reversing the transformation."""
    def __init__(self):
        self.scale_history = []  # Store scaling factors

    def clear_history(self) -> None:
        """Clears the scale history."""
        self.scale_history = []
    
    def set_history(self, history: List[float]) -> None:
        """Sets the scale history directly"""
        self.scale_history = history

    def scale(
        self, 
        signals: List[List[float]], 
        scale_unit: float
    ) -> List[List[float]]:
        """Scales multiple signals' variance while preserving their means and stores the transformation.
        
        Arguments:
            signals: List of signals to scale
            scale_unit: Amount to scale the signals by
            
        Returns:
            List of scaled signals in same order as input
        """
        # Convert scale_unit to multiplicative factor
        # For increase: multiply by (1 + scale_unit)
        # For decrease: multiply by 1/(1 + scale_unit)
        scale_factor = 1 + scale_unit if scale_unit >= 0 else 1/(1 + abs(scale_unit))
        
        scaled_signals = []
        for signal in signals:
            mean = np.mean(signal)
            scaled_signal = [scale_factor * (s - mean) + mean for s in signal]
            scaled_signals.append(scaled_signal)
            
        self.scale_history.append(scale_factor)
        return scaled_signals

    def reverse(
        self, 
        signals: List[List[float]]
    ) -> List[List[float]]:
        """Reverses the last scaling transformation."""
        if not self.scale_history:
            print("No transformations to reverse.")
            return signals
        
        last_scale = self.scale_history.pop()  # Get the last applied scale
        reversed_signals = []
        for signal in signals:
            mean = np.mean(signal)
            reversed_signal = [(s - mean) / last_scale + mean for s in signal]
            reversed_signals.append(reversed_signal)

        return reversed_signals

    def reset(
        self, 
        signals: List[List[float]]
    ) -> List[List[float]]:
        """Resets the signal back to the original state."""
        # If no scale history, return original signals
        if not self.scale_history:
            return signals
        
        # reverse all scale transformations
        for _ in range(len(self.scale_history)):
            signals = self.reverse(signals)
        
        # check scale history is empty
        if self.scale_history:
            raise ValueError("Scale history is not empty after resetting.")
        
        return signals


class SignalShifter:
    """
    Class for shifting time courses via a constant shift. Tracks 
    history of transformations and allows for reversing the transformation.
    """
    def __init__(self):
        self.shift_history = []
    
    def clear_history(self) -> None:
        """Clears the shift history."""
        self.shift_history = []
    
    def set_history(self, history: List[float]) -> None:
        """Sets the shift history directly"""
        self.shift_history = history

    def shift(
        self, 
        signals: List[List[float]], 
        shift_amount: float
    ) -> List[List[float]]:
        """Shifts the signal by a constant amount and stores the transformation."""
        shifted_signals = []
        for signal in signals:
            shifted_signal = [s + shift_amount for s in signal]
            shifted_signals.append(shifted_signal)
        self.shift_history.append(shift_amount)
        return shifted_signals

    def reverse(
        self, 
        signals: List[List[float]]
    ) -> List[List[float]]:
        """Reverses the last shift transformation."""
        if not self.shift_history:
            print("No transformations to reverse.")
            return signals
        
        last_shift = self.shift_history.pop()  # Get the last applied shift
        reversed_signals = []
        for signal in signals:
            reversed_signal = [s - last_shift for s in signal]
            reversed_signals.append(reversed_signal)
        return reversed_signals

    def reset(
        self, 
        signals: List[List[float]]
    ) -> List[List[float]]:
        """Resets the signal back to the original state."""
        # reverse all shift transformations
        for _ in range(len(self.shift_history)):
            signals = self.reverse(signals)
        
        # check shift history is empty
        if self.shift_history:
            raise ValueError("Shift history is not empty after resetting.")
        
        return signals
