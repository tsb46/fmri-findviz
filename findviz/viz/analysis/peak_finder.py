"""
Peak finder for findviz viewer
"""

from typing import Optional

import numpy as np

from scipy.signal import find_peaks
from scipy.stats import zscore

from findviz.viz.exception import PeakFinderNoPeaksFoundError

class PeakFinder:
    """
    Peak finder for findviz viewer

    Attributes
    ----------
    zscore : bool
        whether to apply z-score normalization to the data. Default is False.
    peak_distance : float
        minimal horizontal distance (>= 1) in samples between neighbouring peaks. Default is 1.
    peak_height : Optional[float]
        optional height of peaks. Default is None.
    peak_prominence : Optional[float]
        optional prominence of peaks. Default is None.
    peak_width : Optional[float]
        optional width of peaks. Default is None.
    peak_threshold : Optional[float]
        optional threshold of peaks. Default is None.
    """
    def __init__(
        self,
        zscore: bool = False,
        peak_distance: float = 1.0,
        peak_height: Optional[float] = None,
        peak_prominence: Optional[float] = None,
        peak_width: Optional[float] = None,
        peak_threshold: Optional[float] = None,
    ):
        self.zscore = zscore
        self.peak_distance = peak_distance
        self.peak_height = peak_height
        self.peak_prominence = peak_prominence
        self.peak_width = peak_width
        self.peak_threshold = peak_threshold

    def find_peaks(self, data):
        if self.zscore:
            data = zscore(data)
        peaks, _ = find_peaks(
            data,
            distance=self.peak_distance,
            height=self.peak_height,
            prominence=self.peak_prominence,
            width=self.peak_width,
            threshold=self.peak_threshold,
        )
        if len(peaks) == 0:
            raise PeakFinderNoPeaksFoundError()
        return peaks
