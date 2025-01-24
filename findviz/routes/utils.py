"""Utility Modules for route input handling"""
from enum import Enum
from typing import Union

import numpy as np

from nilearn import signal

class Routes(Enum):
    ADD_ANNOTATION_MARKER='/add_annotation_marker'
    CLEAR_ANNOTATION_MARKERS='/clear_annotation_markers'
    GET_ANNOTATION_MARKERS='/get_annotation_markers'
    GET_FUNCTIONAL_TIMECOURSE='/get_functional_timecourse'
    GET_PLOT_OPTIONS='/get_plot_options'
    GET_TIMECOURSE_PLOT_OPTIONS='/get_timecourse_plot_options'
    GET_PREPROCESSED_FMRI='/get_preprocessed_fmri'
    GET_PREPROCESSED_TIMECOURSE='/get_preprocessed_timecourse'
    RESET_COLOR_OPTIONS='/reset_color_options'
    RESET_FMRI_PREPROCESS='/reset_fmri_preprocess'
    RESET_TIMECOURSE_PREPROCESS='/reset_timecourse_preprocess'
    UNDO_ANNOTATION_MARKER='/undo_annotation_marker'
    UPDATE_TIMEPOINT='/update_timepoint'
    UPDATE_LOCATION='/update_location'
    UPDATE_PLOT_OPTIONS='/update_plot_options'


# Convert values from json
def convert_value(value: str) -> Union[str, int, float, None]:
    """
    Convert values from form data to Python types 

    Args:
        value (str): string value from web browser 

    Returns:
        Union[str, int, float, None]: converted value
    """
    # Check for booleans
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
    # Check for None
    if value.lower() == 'null' or value.lower() == 'none' or value == '':
        return None
    # Try to convert to integer
    try:
        return int(value)
    except ValueError:
        pass
    # Try to convert to float
    try:
        return float(value)
    except ValueError:
        pass
    # Return the value as-is if no conversion happened
    return value


# Function to apply conversion to all values in a dictionary
def convert_params(params):
    return {key: convert_value(value) for key, value in params.items()}

# Function to convert strings (passed via fetch) to list of floats
def str_to_float_list(string):
    return list(map(float, string.split(',')))


# check string is numeric
def is_numeric(value):
    try:
        float(value)  # Try to convert to a number
        return True
    except ValueError:
        return False


# temporal filtering with nilearn
def filter(data, lowCut, highCut, tr):
    # compute sampling frequency
    sf = 1/tr
    # perform filtering
    data_filtered = signal.butterworth(
        data, sampling_rate=sf, low_pass=highCut,
        high_pass=lowCut
    )
    return data_filtered

# Normalize time courses based on file type (gifti vs nifti)
def normalize(data, norm, axis):
    # z-score normalization
    if norm == 'z_score':
        data_norm = data - data.mean(axis=axis, keepdims=True)
        data_norm = data_norm / data_norm.std(axis=axis, keepdims=True)
        # handle constant values that return nan
        data_norm = np.nan_to_num(data_norm, copy=False, nan=0.0)
    elif norm == 'mean_center':
        data_norm = data - data.mean(axis=axis, keepdims=True)

    return data_norm


