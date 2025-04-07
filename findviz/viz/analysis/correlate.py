"""
Correlate fmri time courses with time course
"""
from typing import List

import numpy as np

from findviz.viz.analysis.utils import get_lag_mat
from findviz.viz.analysis.validate import (
    validate_less_than_or_equal_to_zero,
    validate_greater_than_or_equal_to_zero,
    validate_less_than_half_time_length
)
from findviz.viz.exception import ParameterInputError

class Correlate:
    def __init__(
        self, 
        negative_lag: int,
        positive_lag: int,
        time_length: int
    ):
        """
        Initialize Correlate class

        Parameters
        ----------
        negative_lag : int
            negative lag, should be zero or negative
        positive_lag : int
            positive lag, should be zero or positive
        time_length : int
            time length of fMRI data
        """
        self.negative_lag = negative_lag
        self.positive_lag = positive_lag
        self.time_length = time_length
        # validate parameters
        self._validate()
        # get array of lags
        self.lags = np.arange(
            self.negative_lag, self.positive_lag + 1
        )

    def correlate(self, fmri_data: np.ndarray, time_course: List[float]):
        """
        Correlate fmri data with time course

        Parameters
        ----------
        fmri_data : np.ndarray
            fmri data (n_timepoints, n_voxels)
        time_course : List[float]
            time course (n_timepoints)

        Returns
        -------
        corr : np.ndarray
            correlation map (n_lags, n_voxels)

        """
        # Convert time course to numpy array
        time_course = np.array(time_course)
        
        # Get lag matrix - shape (n_timepoints, n_lags)
        lag_mat = get_lag_mat(time_course[:, np.newaxis], self.lags)
        
        # Initialize correlation map
        n_lags = len(self.lags)
        n_voxels = fmri_data.shape[1]
        
        # Handle the case where fmri_data has 0 voxels
        if n_voxels == 0:
            return np.zeros((n_lags, 0))
        
        correlation_map = np.zeros((n_lags, n_voxels))
        
        # Compute correlations for each lag
        for i in range(n_lags):
            # Get the current lagged time course
            lagged_tc = lag_mat[:, i]
            
            # Find valid data points (not NaN)
            mask = ~np.isnan(lagged_tc)
            
            # Skip if not enough valid data points
            if np.sum(mask) <= 1:
                correlation_map[i, :] = np.nan
                continue
                
            # Use masked arrays to handle NaN values
            valid_lagged_tc = lagged_tc[mask]
            valid_fmri = fmri_data[mask, :]
                
            # Calculate correlation between lagged time course and all voxels at once
            # np.corrcoef returns a correlation matrix where:
            # - First row/column corresponds to the lagged time course
            # - Other rows/columns correspond to the voxels
            if valid_fmri.shape[1] > 0:  # Only if we have voxels
                corr_matrix = np.corrcoef(valid_lagged_tc, valid_fmri.T)
                # Extract correlations between lagged time course and each voxel
                # The first row (after the first element) contains these correlations
                correlation_map[i, :] = corr_matrix[0, 1:]
        
        return correlation_map

    def _validate(self):
        """
        Validate parameters

        Raises
        ------
        ParameterInputError
            if the parameters are not valid
        """
        # check lags are valid
        if not validate_less_than_or_equal_to_zero(self.negative_lag):
            raise ParameterInputError(
                message="Negative lag must be negative",
                parameters=["negative_lag"]
            )
        if not validate_greater_than_or_equal_to_zero(self.positive_lag):
            raise ParameterInputError(
                message="Positive lag must be positive",
                parameters=["positive_lag"]
            )
        if not validate_less_than_half_time_length(
            self.negative_lag, 
            self.time_length
        ):
            raise ParameterInputError(
                message="Negative lag must be less than half the time length",
                parameters=["negative_lag"]
            )
        if not validate_less_than_half_time_length(
            self.positive_lag, 
            self.time_length
        ):
            raise ParameterInputError(
                message="Positive lag must be less than half the time length",
                parameters=["positive_lag"]
            )



