"""
Distance analysis of fmri time points
"""
from typing import List, Tuple

import numpy as np

from scipy.spatial.distance import cdist


class Distance:
    """Distance analysis of fmri time points"""

    def __init__(
        self,
        distance_metric: str,
    ):
        self.distance_metric = distance_metric
    
    def calculate_distance(self, time_point: int, fmri_data: np.ndarray) -> np.ndarray:
        """Calculate distance between fmri time point and rest of time points"""
        dist = cdist(
            fmri_data[time_point,:][np.newaxis,:], 
            fmri_data, 
            metric=self.distance_metric
        )
        return np.squeeze(dist)
