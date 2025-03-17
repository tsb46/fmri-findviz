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
    

def preprocess_timecourse(
    timecourse_data: List[float],
    inputs: PreprocessTimecourseInputs
) -> List[float]:
    """
    Preprocess time course data

    Parameters
    ----------
    timecourse_data: List[float]
        time course data
    inputs: PreprocessTimecourseInputs
        inputs for preprocess_timecourse

    Returns
    -------
    List[float]
        preprocessed time course data  
    """
    # convert to 2D numpy array with one column
    timecourse_data = np.array(timecourse_data)[:, np.newaxis]

    # Detrend the data
    if inputs['detrend']:
        timecourse_data = utils.linear_detrend(timecourse_data)
    
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
        timecourse_data = utils.z_score(timecourse_data)

    # return to list
    return timecourse_data.flatten().tolist()

