"""
Plot routes
Routes:
    ADD_ANNOTATION_MARKER: Add annotation marker
    CHANGE_TASK_CONVOLUTION: Change task convolution
    CHANGE_TIMECOURSE_SCALE: Change timecourse scale
    CLEAR_ANNOTATION_MARKERS: Clear annotation markers
    GET_ANNOTATION_MARKERS: Get annotation markers
    GET_DISTANCE_PLOT_OPTIONS: Get distance plot options
    GET_FMRI_PLOT_OPTIONS: Get fMRI plot options
    GET_LOCATION: Get click coordinates
    GET_TASK_CONDITIONS: Get task conditions
    GET_TASK_DESIGN_PLOT_OPTIONS: Get task design plot options
    GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS: Get timecourse global plot options
    GET_TIMECOURSE_PLOT_OPTIONS: Get timecourse plot options
    GET_TIMEMARKER_PLOT_OPTIONS: Get timemarker plot options
    MOVE_ANNOTATION_SELECTION: Move annotation selection
    RESET_FMRI_COLOR_OPTIONS: Reset fMRI color options
    REMOVE_DISTANCE_PLOT: Remove distance plot
    UPDATE_DISTANCE_PLOT_OPTIONS: Update distance plot options
    UPDATE_FMRI_PLOT_OPTIONS: Update fMRI plot options
    UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS: Update timecourse global plot options
    UPDATE_TIMECOURSE_PLOT_OPTIONS: Update timecourse plot options
    UPDATE_TIMEMARKER_PLOT_OPTIONS: Update timemarker plot options
"""

from flask import Blueprint, request

from findviz.logger_config import setup_logger
from findviz.routes.utils import Routes, convert_value, handle_route_errors
from findviz.routes.shared import data_manager

logger = setup_logger(__name__)
plot_bp = Blueprint('plot', __name__)

@plot_bp.route(Routes.ADD_ANNOTATION_MARKER.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in add annotation marker request',
    log_msg='Added annotation marker successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.ADD_ANNOTATION_MARKER
)
def add_annotation_marker() -> int:
    """Add annotation marker"""
    marker = convert_value(request.form['marker'])
    data_manager.add_annotation_markers(marker)
    return 200


@plot_bp.route(Routes.CHANGE_TASK_CONVOLUTION.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in change task convolution request',
    log_msg='Changed task convolution successfully'
)
def change_task_convolution() -> int:
    """Change task convolution globally across all tasks"""
    convolution = convert_value(request.form['convolution'])
    data_manager.update_timecourse_global_plot_options(
        {'global_convolution': convolution}
    )
    # update all task design plot options
    for label in data_manager._state.task_plot_options:
        data_manager.update_task_design_plot_options(
            label, {'convolution': convolution}
        )
    return 200


@plot_bp.route(Routes.CHANGE_TIMECOURSE_SCALE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in change timecourse scale change request',
    log_msg='Timecourse scale change successful'
)
def change_timecourse_scale() -> int:
    """Change timecourse scale"""
    data_manager.change_timecourse_scale(
        request.form['label'], 
        request.form['ts_type'], 
        request.form['scale_change']
    )
    return 200


@plot_bp.route(Routes.CLEAR_ANNOTATION_MARKERS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in clear annotation markers request',
    log_msg='Cleared annotation markers successfully'
)
def clear_annotation_markers() -> int:
    """Clear annotation markers"""
    data_manager.clear_annotation_markers()
    return 200


@plot_bp.route(Routes.GET_ANNOTATION_MARKERS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in annotation markers request',
    log_msg='Retrieved annotation markers successfully'
)
def get_annotation_markers() -> dict:
    """Get current annotation markers and current annotation selection"""
    markers = data_manager.annotation_markers
    selection = data_manager.annotation_selection
    highlight = data_manager.annotation_highlight_on
    return {
        'markers': markers,
        'selection': selection,
        'highlight': highlight
    }


@plot_bp.route(Routes.GET_DISTANCE_PLOT_OPTIONS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in distance plot options request',
    log_msg='Retrieved distance plot options successfully'
)
def get_distance_plot_options() -> dict:
    """Get current distance plot options."""
    return data_manager.get_distance_plot_options()


@plot_bp.route(Routes.GET_LOCATION.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in get location request',
    log_msg='Retrieved location successfully'
)
def get_location() -> dict:
    """Get current click coordinates."""
    return data_manager.get_location_data()


@plot_bp.route(Routes.GET_FMRI_PLOT_OPTIONS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in get fMRI plot options request',
    log_msg='Retrieved fMRI plot options successfully'
)
def get_fmri_plot_options() -> dict:
    """Get current fMRI plot options."""
    return data_manager.get_fmri_plot_options()


@plot_bp.route(Routes.GET_TASK_DESIGN_PLOT_OPTIONS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in task design plot options request',
    log_msg='Retrieved task design plot options successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.GET_TASK_DESIGN_PLOT_OPTIONS
)
def get_task_design_plot_options() -> dict:
    """Get current task design plot options"""
    label = convert_value(request.args.get('label'))
    return data_manager.get_task_design_plot_options(label)


@plot_bp.route(Routes.GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in timecourse global plot options request',
    log_msg='Retrieved timecourse global plot options successfully'
)
def get_timecourse_global_plot_options() -> dict:
    """Get current timecourse global plot options"""
    return data_manager.get_timecourse_global_plot_options()


@plot_bp.route(Routes.GET_TIMECOURSE_PLOT_OPTIONS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in timecourse plot options request',
    log_msg='Retrieved timecourse plot options successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.GET_TIMECOURSE_PLOT_OPTIONS
)
def get_timecourse_plot_options() -> dict:
    """Get current timecourse plot options"""
    label = convert_value(request.args.get('label'))
    return data_manager.get_timecourse_plot_options(label)


@plot_bp.route(Routes.GET_TIMEMARKER_PLOT_OPTIONS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in timemarker plot options request',
    log_msg='Retrieved timemarker plot options successfully'
)
def get_timemarker_plot_options() -> dict:
    """Get current timemarker plot options"""
    return data_manager.get_time_marker_plot_options()


@plot_bp.route(Routes.MOVE_ANNOTATION_SELECTION.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in move annotation selection request',
    log_msg='Moved annotation selection successfully'
)
def move_annotation_selection() -> int:
    """Move annotation selection"""
    data_manager.move_annotation_selection(request.form['direction'])
    return 200


@plot_bp.route(Routes.REMOVE_DISTANCE_PLOT.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in remove distance plot request',
    log_msg='Removed distance plot successfully'
)
def remove_distance_plot() -> int:
    """Remove distance plot"""
    data_manager.clear_distance_plot_state()
    return 200


@plot_bp.route(Routes.RESET_COLOR_OPTIONS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in reset color options request',
    log_msg='Reset color options successfully'
)
def reset_fmri_color_options() -> int:
    """Reset fMRI color options to defaults."""
    data_manager.reset_fmri_color_options()
    return 200


@plot_bp.route(Routes.UNDO_ANNOTATION_MARKER.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in undo annotation marker request',
    log_msg='Undid annotation marker successfully'
)
def undo_annotation_marker() -> int:
    """Undo annotation marker"""
    data_manager.pop_annotation_marker()
    return 200


@plot_bp.route(Routes.UPDATE_DISTANCE_PLOT_OPTIONS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in distance plot options update request',
    log_msg='Updated distance plot options successfully'
)
def update_distance_plot_options() -> int:
    """Update distance plot options"""
    data_manager.update_distance_plot_options(request.form['distance_plot_options'])
    return 200


@plot_bp.route(Routes.UPDATE_FMRI_PLOT_OPTIONS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in fMRI plot options update request',
    log_msg='Updated fMRI plot options successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.UPDATE_FMRI_PLOT_OPTIONS
)
def update_fmri_plot_options() -> int:
    """Update plot options based on form data."""
    data_manager.update_fmri_plot_options(request.form['fmri_plot_options'])
    return 200


@plot_bp.route(Routes.UPDATE_TASK_DESIGN_PLOT_OPTIONS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in task design plot options update request',
    log_msg='Updated task design plot options successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.UPDATE_TASK_DESIGN_PLOT_OPTIONS
)
def update_task_design_plot_options() -> int:
    """Update task design plot options"""
    label = convert_value(request.form['label'])
    plot_options = request.form['task_design_plot_options']
    data_manager.update_task_design_plot_options(label, plot_options)
    return 200


@plot_bp.route(Routes.UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in timecourse global plot options update request',
    log_msg='Updated timecourse global plot options successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS
)
def update_timecourse_global_plot_options() -> int:
    """Update timecourse global plot options"""
    data_manager.update_timecourse_global_plot_options(
        request.form['timecourse_global_plot_options']
    )
    return 200


@plot_bp.route(Routes.UPDATE_TIMECOURSE_PLOT_OPTIONS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in timecourse plot options update request',
    log_msg='Updated timecourse plot options successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.UPDATE_TIMECOURSE_PLOT_OPTIONS
)
def update_timecourse_plot_options() -> int:
    """Update timecourse plot options"""
    data_manager.update_timecourse_plot_options(
        request.form['label'],
        request.form['timecourse_plot_options']
    )
    return 200


@plot_bp.route(Routes.UPDATE_TIMEMARKER_PLOT_OPTIONS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in timemarker plot options update request',
    log_msg='Updated timemarker plot options successfully',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.UPDATE_TIMEMARKER_PLOT_OPTIONS
)
def update_timemarker_plot_options() -> int:
    """Update timemarker plot options"""
    data_manager.update_time_marker_plot_options(
        request.form['timemarker_plot_options']
    )
    return 200
