"""
Plot options routes
Routes:
    GET_PLOT_OPTIONS: Get plot options
    RESET_COLOR_OPTIONS: Reset color options
    UPDATE_PLOT_OPTIONS: Update plot options
"""

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.routes.utils import Routes, convert_value
from findviz.routes.shared import data_manager
from findviz.viz.exception import DataRequestError

# Set up a logger for the app
logger = setup_logger(__name__)

plot_options_bp = Blueprint('plot_options', __name__)


@plot_options_bp.route(Routes.ADD_ANNOTATION_MARKER.value, methods=['POST'])
def add_annotation_marker() -> tuple[int, int]:
    """Add annotation marker"""
    try:
        marker = convert_value(request.form['marker'])
        data_manager.add_annotation_marker(marker)
        return make_response(200)
    except KeyError as e:
        data_error = DataRequestError(
            message='Error in add annotation marker request.',
            fmri_file_type=data_manager.file_type,
            route=Routes.ADD_ANNOTATION_MARKER,
            input_field=e.args[0]
        )
        logger.error(data_error)
        return make_response(data_error.message, 400)
    except Exception as e:
        logger.critical(
            "Error in add annotation marker request: %s", 
            str(e), exc_info=True
        )
        error_message = f"Unknown error in add annotation marker request"
        return make_response(error_message, 500)


@plot_options_bp.route(Routes.CLEAR_ANNOTATION_MARKERS.value, methods=['POST'])
def clear_annotation_markers() -> tuple[int, int]:
    """Clear annotation markers"""
    try:
        data_manager.clear_annotation_markers()
        return make_response(200)
    except Exception as e:
        logger.critical(
            "Error in clear annotation markers request: %s",
            str(e), exc_info=True
        )
        error_message = f"Unknown error in clear annotation markers request"
        return make_response(error_message, 500)

@plot_options_bp.route(Routes.GET_ANNOTATION_MARKERS.value, methods=['GET'])
def get_annotation_markers() -> tuple[list, int]:
    """Get current annotation markers.
    
    Returns:
        tuple[list, int]: A tuple containing:
            - list: Current annotation markers
            - int: HTTP status code (200 for success, 500 for errors)
    """
    try:
        annotation_markers = data_manager.annotation_markers
        return make_response(annotation_markers, 200)
    except Exception as e:
        logger.critical(
            "Error in annotation markers request: %s", 
            str(e), exc_info=True
        )
        error_message = f"Unknown error in annotation markers request"
        return make_response(error_message, 500)


@plot_options_bp.route(Routes.GET_PLOT_OPTIONS.value, methods=['GET'])
def get_plot_options() -> tuple[dict, int]:
    """Get current plot options.
    
    Returns:
        tuple[dict, int]: A tuple containing:
            - dict: Current plot options
            - int: HTTP status code (200 for success, 500 for errors)
    
    Raises:
        Exception: For unexpected errors
    """
    try:
        plot_options = data_manager.get_plot_options()
        return make_response(plot_options, 200)
    except Exception as e:
        logger.critical(
            "Error in plot options request: %s", str(e), exc_info=True
        )
        error_message = f"Unknown error in plot options request"
        return make_response(error_message, 500)


@plot_options_bp.route(Routes.GET_TIMECOURSE_PLOT_OPTIONS.value, methods=['GET'])
def get_timecourse_plot_options() -> tuple[dict, int]:
    """Get current timecourse plot options.
    
    Returns:
        tuple[dict, int]: A tuple containing:
            - dict: Current timecourse plot options
            - int: HTTP status code (200 for success, 500 for errors)
    """
    try:
        label = convert_value(request.args.get('label'))
        plot_options = data_manager.get_timecourse_plot_options(
            label=label
        )
        return make_response(plot_options, 200)
    except KeyError as e:
        data_error = DataRequestError(
            message='Error in timecourse plot options request.',
            fmri_file_type=data_manager.file_type,
            route=Routes.GET_TIMECOURSE_PLOT_OPTIONS,
            input_field=e.args[0]
        )
        logger.error(data_error)
        return make_response(data_error.message, 400)
    except Exception as e:
        logger.critical(
            "Error in timecourse plot options request: %s", 
            str(e), exc_info=True
        )
        error_message = f"Unknown error in timecourse plot options request"
        return make_response(error_message, 500)


@plot_options_bp.route(Routes.RESET_COLOR_OPTIONS.value, methods=['POST'])
def reset_color_options() -> tuple[int, int]:
    """Reset color options to defaults.
    
    Returns:
        tuple[int, int]: A tuple containing:
            - int: HTTP status code (200 for success)
            - int: HTTP status code (500 for errors)
    
    Raises:
        Exception: For unexpected errors
    """
    try:
        data_manager.reset_color_options()
        return make_response(200)
    except Exception as e:
        logger.critical(
            "Error in reset color options request: %s", 
            str(e), exc_info=True
        )
        error_message = f"Unknown error in reset color options request"
        return make_response(error_message, 500)


@plot_options_bp.route(Routes.UNDO_ANNOTATION_MARKER.value, methods=['POST'])
def undo_annotation_marker() -> tuple[int, int]:
    """Undo annotation marker"""
    try:
        data_manager.pop_annotation_marker()
        return make_response(200)
    except Exception as e:
        logger.critical(
            "Error in undo annotation marker request: %s", 
            str(e), exc_info=True
        )
        error_message = f"Unknown error in undo annotation marker request"
        return make_response(error_message, 500)


@plot_options_bp.route(Routes.UPDATE_PLOT_OPTIONS.value, methods=['POST'])
def update_plot_options() -> tuple[int, int]:
    """Update plot options based on form data.
    
    Expects form data with:
        - plot_options: Updated plot options
    
    Returns:
        tuple[int, int]: A tuple containing:
            - int: HTTP status code (200 for success)
            - int: HTTP status code (400/500 for errors)
    
    Raises:
        DataRequestError: If plot_options field is missing
        Exception: For unexpected errors
    """
    try:
        fmri_file_type = data_manager.get_file_type()
        data_manager.update_plot_options(request.form['plot_options'])
        return make_response(200)
    except KeyError as e:
        data_error = DataRequestError(
            message='Error in plot options update request.',
            fmri_file_type=fmri_file_type,
            route=Routes.UPDATE_PLOT_OPTIONS,
            input_field=e.args[0]
        )
        logger.error(data_error)
        return make_response(
            data_error.message, 400
        )
    except Exception as e:
        logger.critical(
            "Unknown error in plot options update request: %s", 
            str(e), exc_info=True
        )
        error_message = f"Unknown error in plot options update request"
        return make_response(error_message, 500)
