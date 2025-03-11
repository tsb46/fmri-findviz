"""
Window average fmri time courses around annotation markers
"""
from typing import List

import numpy as np

from findviz.viz.analysis.utils import extract_range
from findviz.viz.analysis.validate import (
    validate_less_than_or_equal_to_zero,
    validate_greater_than_or_equal_to_zero,
    validate_less_than_half_time_length
)
from findviz.viz.exception import ParameterInputError


class WindowAverage:
    """
    Window average fmri time courses around annotation markers

    Parameters
    ----------
    left_edge : int
        left edge of window, should be zero or negative
    right_edge : int
        right edge of window, should be positive or zero
    """
    def __init__(
        self, 
        left_edge: int, 
        right_edge: int,
        n_timepoints: int
    ):
        self.left_edge = left_edge
        self.right_edge = right_edge
        self.n_timepoints = n_timepoints
        self._validate()

    def average(
        self, 
        fmri_data: np.ndarray, 
        annotation_markers: list
    ) -> np.ndarray:
        """
        Average fmri time courses around annotation markers

        Parameters
        ----------
        fmri_data : np.ndarray
            fmri data to average
        annotation_markers : list
            list of annotation markers

        Returns
        -------
        np.ndarray
            averaged fmri data
        """
        # index windows for each marker
        windows = []
        for center in annotation_markers:
            windows.append(
                extract_range(fmri_data, center, self.left_edge, self.right_edge)
            )
        # convert to 3d array
        windows = np.stack(windows, axis=0)

        # average all windows
        w_avg = np.nanmean(windows, axis=0)

        return w_avg

    def get_timepoints(self) -> List[float]:
        """
        Get timepoints for the window average

        Returns
        -------
        np.ndarray
            timepoints for the window average
        """
        return np.arange(
            self.left_edge,
            self.right_edge + 1
        ).tolist()

    def _validate(self) -> None:
        """
        Validate input parameters
        """
         # check lags are valid
        if not validate_less_than_or_equal_to_zero(self.left_edge):
            raise ParameterInputError(
                message="Left edge must be negative",
                parameters=["left_edge"]
            )
        if not validate_greater_than_or_equal_to_zero(self.right_edge):
            raise ParameterInputError(
                message="Right edge must be positive",
                parameters=["right_edge"]
            )
        if not validate_less_than_half_time_length(
            self.left_edge, 
            self.n_timepoints
        ):
            raise ParameterInputError(
                message="Left edge must be less than half the time length",
                parameters=["left_edge"]
            )
        if not validate_less_than_half_time_length(
            self.right_edge, 
            self.n_timepoints
        ):
            raise ParameterInputError(
                message="Right edge must be less than half the time length",
                parameters=["right_edge"]
            )