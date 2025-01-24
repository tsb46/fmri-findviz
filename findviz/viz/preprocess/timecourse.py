"""
Preprocess time course data
"""

from typing import Literal, TypedDict, Tuple, List

import numpy as np

from findviz.logger_config import setup_logger
from findviz.viz.preprocess import utils

# Set up a logger for the app
logger = setup_logger(__name__)

class PreprocessTimecourseInputs(TypedDict):
    """
    Inputs for preprocess_timecourse
    """
    normalize: bool
    detrend: bool
    filter: bool
    mean_center: bool
    zscore: bool
    tr: float
    low_cut: float
    high_cut: float
    order: int
    ts_labels: List[str]
    

def preprocess_timecourse(
    timecourse_data: np.ndarray,
    inputs: PreprocessTimecourseInputs,
) -> np.ndarray:
    """
    Preprocess time course data

    Arguments:
    ----------
        timecourse_data: time course data
        inputs: inputs for preprocess_timecourse

    Returns:
    --------
        timecourse_data: preprocessed time course data  
    """
    # if timecourse_data is 1D, add a new axis
    if timecourse_data.ndim == 1:
        timecourse_data = timecourse_data[:, np.newaxis]

    # Detrend the data
    if inputs['detrend']:
        timecourse_data = utils.detrend(timecourse_data)
    
    # Butterworth filter the data
    if inputs['filter']:
        # convert tr to hz
        tr_hz = utils.tr_to_hz(inputs['tr'])
        timecourse_data = utils.butterworth_filter(
            timecourse_data, 
            tr_hz,
            inputs['low_cut'], 
            inputs['high_cut'], 
        )

    # Mean center the data
    if inputs['mean_center']:
        timecourse_data = utils.mean_center(timecourse_data)
    
    # Z-score the data
    if inputs['zscore']:
        timecourse_data = utils.zscore(timecourse_data)

    return timecourse_data

