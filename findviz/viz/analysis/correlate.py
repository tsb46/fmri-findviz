"""
Correlate fmri time courses with time course
"""
from typing import List

import numpy as np

from scipy.stats import zscore

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
        # convert time course to numpy array with one colume
        time_course = np.array(time_course)[:, np.newaxis]
        # get lag matrix
        lag_mat = get_lag_mat(time_course, self.lags)

        # standardize data
        fmri_data = zscore(fmri_data, axis=0)
        time_course = zscore(time_course)

        # compute correlation map
        correlation_map = (
            np.dot(fmri_data.T, lag_mat) / len(time_course)
        )
        return correlation_map.T

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



