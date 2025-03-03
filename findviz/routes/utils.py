"""Utility Modules for route input handling"""
from enum import Enum
from functools import wraps
from typing import Union, Callable, TypeVar, ParamSpec, List, Type


import numpy as np

from flask import make_response, request

from findviz.viz.exception import DataRequestError
from findviz.logger_config import setup_logger


# Set up logger
logger = setup_logger(__name__)

# Type variables for generic function signatures
P = ParamSpec('P')
R = TypeVar('R')

class Routes(Enum):
    ADD_ANNOTATION_MARKER='/add_annotation_marker'
    CHANGE_TASK_CONVOLUTION='/change_task_convolution'
    CHANGE_TIMECOURSE_SCALE='/change_timecourse_scale'
    CHECK_TS_PREPROCESSED='/check_ts_preprocessed'
    CLEAR_ANNOTATION_MARKERS='/clear_annotation_markers'
    CORRELATE='/correlate'
    DISTANCE='/distance'
    GET_ANNOTATION_MARKERS='/get_annotation_markers'
    GET_ANNOTATION_MARKER_PLOT_OPTIONS='/get_annotation_marker_plot_options'
    GET_CLICK_COORDS='/get_click_coords'
    GET_CROSSHAIR_COORDS='/get_crosshair_coords'
    GET_COLORMAPS='/get_colormaps'
    GET_DIRECTION_LABEL_COORDS='/get_direction_label_coords'
    GET_DISTANCE_DATA='/get_distance_data'
    GET_DISTANCE_PLOT_OPTIONS='/get_distance_plot_options'
    GET_FMRI_DATA='/get_fmri_data'
    GET_FMRI_PLOT_OPTIONS='/get_fmri_plot_options'
    GET_LAST_TIMECOURSE='/get_last_timecourse'
    GET_MONTAGE_DATA='/get_montage_data'
    GET_N_TIMEPOINTS='/get_n_timepoints'
    GET_NIFTI_VIEW_STATE='/get_nifti_view_state'
    GET_SELECTED_TIME_POINT='/get_selected_time_point'
    GET_TASK_CONDITIONS='/get_task_conditions'
    GET_TASK_DESIGN_PLOT_OPTIONS='/get_task_design_plot_options'
    GET_TIMECOURSE_LABELS='/get_timecourse_labels'
    GET_TIMECOURSE_LABELS_PREPROCESSED='/get_timecourse_labels_preprocessed'
    GET_TIMECOURSE_DATA='/get_timecourse_data'
    GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS='/get_timecourse_global_plot_options'
    GET_TIMECOURSE_SOURCE='/get_timecourse_source'
    GET_TIMECOURSE_PLOT_OPTIONS='/get_timecourse_plot_options'
    GET_TIMECOURSE_SHIFT_HISTORY='/get_timecourse_shift_history'
    GET_TIMEMARKER_PLOT_OPTIONS='/get_timemarker_plot_options'
    GET_TIMEPOINT='/get_timepoint'
    GET_PREPROCESSED_FMRI='/get_preprocessed_fmri'
    GET_PREPROCESSED_TIMECOURSE='/get_preprocessed_timecourse'
    GET_VIEWER_METADATA='/get_viewer_metadata'
    FIND_PEAKS='/find_peaks'
    MOVE_ANNOTATION_SELECTION='/move_annotation_selection'
    POP_FMRI_TIMECOURSE='/pop_fmri_timecourse'
    REMOVE_DISTANCE_PLOT='/remove_distance_plot'
    REMOVE_FMRI_TIMECOURSES='/remove_fmri_timecourses'
    RESET_FMRI_COLOR_OPTIONS='/reset_fmri_color_options'
    RESET_FMRI_PREPROCESS='/reset_fmri_preprocess'
    RESET_TIMECOURSE_PREPROCESS='/reset_timecourse_preprocess'
    RESET_TIMECOURSE_SHIFT='/reset_timecourse_shift'
    UNDO_ANNOTATION_MARKER='/undo_annotation_marker'
    UPDATE_ANNOTATION_MARKER_PLOT_OPTIONS='/update_annotation_marker_plot_options'
    UPDATE_DISTANCE_PLOT_OPTIONS='/update_distance_plot_options'
    UPDATE_FMRI_TIMECOURSE='/update_fmri_timecourse'
    UPDATE_FMRI_PLOT_OPTIONS='/update_fmri_plot_options'
    UPDATE_MONTAGE_SLICE_DIR='/update_montage_slice_dir'
    UPDATE_MONTAGE_SLICE_IDX='/update_montage_slice_idx'
    UPDATE_NIFTI_VIEW_STATE='/update_nifti_view_state'
    UPDATE_TASK_DESIGN_PLOT_OPTIONS='/update_task_design_plot_options'
    UPDATE_TIMEPOINT='/update_timepoint'
    UPDATE_TIMECOURSE_PLOT_OPTIONS='/update_timecourse_plot_options'
    UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS='/update_timecourse_global_plot_options'
    UPDATE_TIMEMARKER_PLOT_OPTIONS='/update_timemarker_plot_options'
    UPDATE_TIMECOURSE_SHIFT='/update_timecourse_shift'
    UPDATE_LOCATION='/update_location'
    WINDOWED_AVERAGE='/windowed_average'



# Convert values from json
def convert_value(
    value: Union[str, bool, int, float]
) -> Union[str, int, float, None]:
    """
    Convert values from form data to Python types 

    Args:
        value (Union[str, bool, int, float]): value from web browser

    Returns:
        Union[str, int, float, None]: converted value
    """
    # check if value is a boolean
    if isinstance(value, bool):
        return value
    # Check for booleans passed as strings
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


def handle_route_errors(
    error_msg: str,
    log_msg: str = None,
    fmri_file_type: Union[str, Callable[[], str]] = None,  # callable
    route: str = None,
    route_parameters: List[str] = None,
    custom_exceptions: List[Type[Exception]] = None,
) -> Callable[[Callable[P, R]], Callable[P, tuple[Union[R, str], int]]]:
    """
    Decorator to handle common route error patterns
    
    Args:
        error_msg (str): Base error message for the route
        log_msg (str, optional): Message to log on success. Defaults to None.
        fmri_file_type (Union[str, Callable[[], str]], optional): FMRI file type for DataRequestError.
          Defaults to None. Pass a callable to get the fmri file type dynamically.
        route (str, optional): Route name for DataRequestError. Defaults to None.
        custom_exceptions (List[Type[Exception]], optional): List of custom exceptions to handle. Defaults to None.
    Returns:
        Callable: Decorated route function that handles errors consistently
    """
    def decorator(func: Callable[P, R]) -> Callable[P, tuple[Union[R, str], int]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[Union[R, str], int]:
             # Get file type at runtime if it's a callable
            current_file_type = fmri_file_type() if callable(fmri_file_type) else fmri_file_type

            # check if route parameters are provided
            if route_parameters:
                # check if all route parameters are provided
                for param in route_parameters:
                    if (param not in request.form) and (param not in request.args):
                        # Handle missing required fields
                        data_error = DataRequestError(
                            message=f'{error_msg}.',
                            fmri_file_type=current_file_type,
                            route=route,
                            input_field=param
                        )
                        logger.error(data_error)
                        return make_response(data_error.message, 400)

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

            except Exception as e:
                # check if exception is in custom exceptions
                # log as error and return 400 to handle in frontend
                if custom_exceptions:
                    for custom_exception in custom_exceptions:
                        if isinstance(e, custom_exception):
                            logger.error(e)
                            return make_response(e.message, 400)
                        
                # log as critical and return 500 to handle in frontend
                logger.critical(
                    f"{error_msg}: {str(e)}", 
                    exc_info=True
                )
                return make_response(error_msg, 500)
            
        return wrapper

    return decorator

# check string is numeric
def is_numeric(value):
    try:
        float(value)  # Try to convert to a number
        return True
    except ValueError:
        return False


def sanitize_array_for_json(arr: np.ndarray) -> List[List[float]]:
    """Convert numpy array to JSON-serializable format, replacing NaN with None.
    
    Parameters
    ----------
    arr : np.ndarray
        Input array that may contain NaN values
        
    Returns
    -------
    List[List[float]]
        JSON-serializable 2D list with NaN values replaced by None
    """
    # Replace NaN with None and convert to list
    return np.where(np.isnan(arr), None, arr).tolist()


# Function to convert strings (passed via fetch) to list of floats
def str_to_float_list(string):
    return list(map(float, string.split(',')))
