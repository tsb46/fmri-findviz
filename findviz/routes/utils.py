"""Utility Modules for route input handling"""
from enum import Enum
from functools import wraps
from typing import Union, Callable, TypeVar, ParamSpec, Any
from flask import make_response

import numpy as np

from nilearn import signal

from findviz.viz.exception import DataRequestError
from findviz.logger_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Type variables for generic function signatures
P = ParamSpec('P')
R = TypeVar('R')

class Routes(Enum):
    ADD_ANNOTATION_MARKER='/add_annotation_marker'
    CHANGE_TIMECOURSE_SCALE='/change_timecourse_scale'
    CLEAR_ANNOTATION_MARKERS='/clear_annotation_markers'
    CORRELATE='/correlate'
    DISTANCE='/distance'
    GET_ANNOTATION_MARKERS='/get_annotation_markers'
    GET_CLICK_COORDS='/get_click_coords'
    GET_CROSSHAIR_COORDS='/get_crosshair_coords'
    GET_COLORMAPS='/get_colormaps'
    GET_DIRECTION_LABEL_COORDS='/get_direction_label_coords'
    GET_DISTANCE_DATA='/get_distance_data'
    GET_DISTANCE_PLOT_OPTIONS='/get_distance_plot_options'
    GET_FMRI_DATA='/get_fmri_data'
    GET_FMRI_PLOT_OPTIONS='/get_fmri_plot_options'
    GET_MONTAGE_DATA='/get_montage_data'
    GET_SELECTED_TIME_POINT='/get_selected_time_point'
    GET_SLICE_LENGTHS='/get_slice_lengths'
    GET_TASK_CONDITIONS='/get_task_conditions'
    GET_TASK_DESIGN_PLOT_OPTIONS='/get_task_design_plot_options'
    GET_TIMECOURSE_LABELS='/get_timecourse_labels'
    GET_TIMECOURSE_DATA='/get_timecourse_data'
    GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS='/get_timecourse_global_plot_options'
    GET_TIMECOURSE_SOURCE='/get_timecourse_source'
    GET_TIMECOURSE_PLOT_OPTIONS='/get_timecourse_plot_options'
    GET_TIMEMARKER_PLOT_OPTIONS='/get_timemarker_plot_options'
    GET_TIMEPOINT='/get_timepoint'
    GET_PREPROCESSED_FMRI='/get_preprocessed_fmri'
    GET_PREPROCESSED_TIMECOURSE='/get_preprocessed_timecourse'
    FIND_PEAKS='/find_peaks'
    MOVE_ANNOTATION_SELECTION='/move_annotation_selection'
    POP_FMRI_TIMECOURSE='/pop_fmri_timecourse'
    REMOVE_FMRI_TIMECOURSES='/remove_fmri_timecourses'
    RESET_FMRI_COLOR_OPTIONS='/reset_fmri_color_options'
    RESET_FMRI_PREPROCESS='/reset_fmri_preprocess'
    RESET_TIMECOURSE_PREPROCESS='/reset_timecourse_preprocess'
    UNDO_ANNOTATION_MARKER='/undo_annotation_marker'
    UPDATE_DISTANCE_PLOT_OPTIONS='/update_distance_plot_options'
    UPDATE_FMRI_PLOT_OPTIONS='/update_fmri_plot_options'
    UPDATE_MONTAGE_SLICE_DIR='/update_montage_slice_dir'
    UPDATE_MONTAGE_SLICE_IDX='/update_montage_slice_idx'
    UPDATE_TIMEPOINT='/update_timepoint'
    UPDATE_TIMECOURSE_PLOT_OPTIONS='/update_timecourse_plot_options'
    UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS='/update_timecourse_global_plot_options'
    UPDATE_TIMEMARKER_PLOT_OPTIONS='/update_timemarker_plot_options'
    UPDATE_LOCATION='/update_location'
    WINDOW_AVERAGE='/window_average'



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

def handle_route_errors(
    error_msg: str,
    log_msg: str = None,
    fmri_file_type: str = None,
    route: str = None,
) -> Callable[[Callable[P, R]], Callable[P, tuple[Union[R, str], int]]]:
    """
    Decorator to handle common route error patterns
    
    Args:
        error_msg (str): Base error message for the route
        log_msg (str, optional): Message to log on success. Defaults to None.
        fmri_file_type (str, optional): FMRI file type for DataRequestError. Defaults to None.
        route (str, optional): Route name for DataRequestError. Defaults to None.
    
    Returns:
        Callable: Decorated route function that handles errors consistently
    """
    def decorator(func: Callable[P, R]) -> Callable[P, tuple[Union[R, str], int]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[Union[R, str], int]:
            try:
                # Execute the route function
                result = func(*args, **kwargs)
                
                # Log success message if provided
                if log_msg:
                    logger.info(log_msg)
                
                # Handle different return types
                if isinstance(result, tuple):
                    return make_response(*result)
                return make_response(result, 200)

            except KeyError as e:
                # Handle missing required fields
                data_error = DataRequestError(
                    message=f'{error_msg}.',
                    fmri_file_type=fmri_file_type,
                    route=route,
                    input_field=e.args[0]
                )
                logger.error(data_error)
                return make_response(data_error.message, 400)

            except Exception as e:
                # Handle unexpected errors
                logger.critical(
                    f"{error_msg}: {str(e)}", 
                    exc_info=True
                )
                return make_response(error_msg, 500)

    return decorator


