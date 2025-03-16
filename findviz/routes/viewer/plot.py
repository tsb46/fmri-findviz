"""
Plot routes
Routes:
    ADD_ANNOTATION_MARKER: Add annotation marker
    CHANGE_TASK_CONVOLUTION: Change task convolution
    CHECK_FMRI_PREPROCESSED: Check if fmri data is preprocessed
    CHECK_TS_PREPROCESSED: Check if timecourse is preprocessed
    CLEAR_ANNOTATION_MARKERS: Clear annotation markers
    GET_ANNOTATION_MARKERS: Get annotation markers
    GET_ANNOTATION_MARKER_PLOT_OPTIONS: Get annotation marker plot options
    GET_DISTANCE_PLOT_OPTIONS: Get distance plot options
    GET_FMRI_PLOT_OPTIONS: Get fMRI plot options
    GET_NIFTI_VIEW_STATE: Get nifti view state (ortho or montage)
    GET_TASK_DESIGN_PLOT_OPTIONS: Get task design plot options
    GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS: Get timecourse global plot options
    GET_TIMECOURSE_PLOT_OPTIONS: Get timecourse plot options
    GET_TIMEMARKER_PLOT_OPTIONS: Get timemarker plot options
    GET_TS_FMRI_PLOTTED: Get whether an fmri timecourse is plotted
    MOVE_ANNOTATION_SELECTION: Move annotation selection
    RESET_FMRI_COLOR_OPTIONS: Reset fMRI color options
    REMOVE_DISTANCE_PLOT: Remove distance plot
    UPDATE_ANNOTATION_MARKER_PLOT_OPTIONS: Update annotation marker plot options
    UPDATE_DISTANCE_PLOT_OPTIONS: Update distance plot options
    UPDATE_FMRI_PLOT_OPTIONS: Update fMRI plot options
    UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS: Update timecourse global plot options
    UPDATE_TIMECOURSE_PLOT_OPTIONS: Update timecourse plot options
    UPDATE_TIMECOURSE_SHIFT: Update timecourse shift (scale or constant)
    UPDATE_TIMEMARKER_PLOT_OPTIONS: Update timemarker plot options
    UPDATE_NIFTI_VIEW_STATE: Update nifti view state (ortho or montage)
"""

import json

from flask import Blueprint, request

from findviz.logger_config import setup_logger
from findviz.routes.utils import (
    convert_value,
    handle_context,
    handle_route_errors,
    Routes
)
from findviz.routes.shared import data_manager

logger = setup_logger(__name__)
plot_bp = Blueprint('plot', __name__)

@plot_bp.route(Routes.ADD_ANNOTATION_MARKER.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in add annotation marker request',
    log_msg='Added annotation marker successfully',
    route_parameters=['marker'],
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.ADD_ANNOTATION_MARKER
)
def add_annotation_marker() -> dict:
    """Add annotation marker"""
    marker = convert_value(request.form['marker'])
    data_manager.ctx.add_annotation_markers(marker)
    return {'marker': marker}


@plot_bp.route(Routes.CHANGE_TASK_CONVOLUTION.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in change task convolution request',
    log_msg='Changed task convolution successfully',
    route_parameters=['convolution'],
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.CHANGE_TASK_CONVOLUTION
)
def change_task_convolution() -> int:
    """Change task convolution globally across all tasks"""
    convolution = convert_value(request.form['convolution'])
    data_manager.ctx.update_timecourse_global_plot_options(
        {'global_convolution': convolution}
    )
    if convolution:
        conv_type = 'hrf'
    else:
        conv_type = 'block'
    # update all task design plot options
    for label in data_manager.ctx.task_plot_options:
        data_manager.ctx.update_task_design_plot_options(
            label, {'convolution': conv_type}
        )
    return {'status': 'success'}


@plot_bp.route(Routes.CHECK_FMRI_PREPROCESSED.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in check fmri preprocessed request',
    log_msg='Checked fmri preprocessed successfully',
    route=Routes.CHECK_FMRI_PREPROCESSED
)
def check_fmri_preprocessed() -> dict:
    """Check if fmri data is preprocessed"""
    return {'is_preprocessed': data_manager.ctx.fmri_preprocessed}


@plot_bp.route(Routes.CHECK_TS_PREPROCESSED.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in check timecourse preprocessed request',
    log_msg='Checked timecourse preprocessed successfully',
    route_parameters=['label', 'ts_type'],
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.CHECK_TS_PREPROCESSED
)
def check_ts_preprocessed() -> dict:
    """Check if timecourse is preprocessed"""
    label = convert_value(request.form['label'])
    ts_type = convert_value(request.form['ts_type'])
    if ts_type == 'timecourse':
        is_preprocessed = data_manager.ctx.check_ts_preprocessed(label)
    else:
        # task design is not preprocessed
        is_preprocessed = False

    return {'is_preprocessed': is_preprocessed}


@plot_bp.route(Routes.CLEAR_ANNOTATION_MARKERS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in clear annotation markers request',
    log_msg='Cleared annotation markers successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.CLEAR_ANNOTATION_MARKERS
)
def clear_annotation_markers() -> dict:
    """Clear annotation markers"""
    data_manager.ctx.clear_annotation_markers()
    return {'status': 'success'}


@plot_bp.route(Routes.GET_ANNOTATION_MARKERS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in annotation markers request',
    log_msg='Retrieved annotation markers successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_ANNOTATION_MARKERS
)
def get_annotation_markers() -> dict:
    """Get annotation markers, annotation selection, and annotation plot options"""
    markers = data_manager.ctx.annotation_markers
    selection = data_manager.ctx.annotation_selection
    plot_options = data_manager.ctx.annotation_marker_plot_options.to_dict()
    return {
        'markers': markers,
        'selection': selection,
        'plot_options': plot_options
    }


@plot_bp.route(Routes.GET_ANNOTATION_MARKER_PLOT_OPTIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in get annotation marker plot options request',
    log_msg='Retrieved annotation marker plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_ANNOTATION_MARKER_PLOT_OPTIONS
)
def get_annotation_marker_plot_options() -> dict:
    """Get annotation marker plot options"""
    return data_manager.ctx.get_annotation_marker_plot_options()


@plot_bp.route(Routes.GET_DISTANCE_PLOT_OPTIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in distance plot options request',
    log_msg='Retrieved distance plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_DISTANCE_PLOT_OPTIONS
)
def get_distance_plot_options() -> dict:
    """Get current distance plot options."""
    return data_manager.ctx.get_distance_plot_options()


@plot_bp.route(Routes.GET_FMRI_PLOT_OPTIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in get fMRI plot options request',
    log_msg='Retrieved fMRI plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_FMRI_PLOT_OPTIONS
)
def get_fmri_plot_options() -> dict:
    """Get current fMRI plot options."""
    return data_manager.ctx.get_fmri_plot_options()


@plot_bp.route(Routes.GET_NIFTI_VIEW_STATE.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in nifti view state request',
    log_msg='Retrieved nifti view state successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_NIFTI_VIEW_STATE
)
def get_nifti_view_state() -> dict:
    """Get current nifti view state"""
    return {'view_state': data_manager.ctx.view_state}


@plot_bp.route(Routes.GET_TASK_DESIGN_PLOT_OPTIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in task design plot options request',
    log_msg='Retrieved task design plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TASK_DESIGN_PLOT_OPTIONS,
    route_parameters=['label']
)
def get_task_design_plot_options() -> dict:
    """Get current task design plot options"""
    label = convert_value(request.args.get('label'))
    return data_manager.ctx.get_task_design_plot_options(label)


@plot_bp.route(Routes.GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse global plot options request',
    log_msg='Retrieved timecourse global plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS
)
def get_timecourse_global_plot_options() -> dict:
    """Get current timecourse global plot options"""
    return data_manager.ctx.get_timecourse_global_plot_options()


@plot_bp.route(Routes.GET_TIMECOURSE_PLOT_OPTIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse plot options request',
    log_msg='Retrieved timecourse plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMECOURSE_PLOT_OPTIONS,
    route_parameters=['label']
)
def get_timecourse_plot_options() -> dict:
    """Get current timecourse plot options"""
    label = convert_value(request.args.get('label'))
    return data_manager.ctx.get_timecourse_plot_options(label)


@plot_bp.route(Routes.GET_TIMECOURSE_SHIFT_HISTORY.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse shift history request',
    log_msg='Retrieved timecourse shift history successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMECOURSE_SHIFT_HISTORY,
    route_parameters=['label', 'source']
)
def get_timecourse_shift_history() -> dict:
    """Get current timecourse shift history"""
    label = convert_value(request.args.get('label'))
    source = convert_value(request.args.get('source'))
    return data_manager.ctx.get_timecourse_shift_history(label, source)


@plot_bp.route(Routes.GET_TIMEMARKER_PLOT_OPTIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timemarker plot options request',
    log_msg='Retrieved timemarker plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMEMARKER_PLOT_OPTIONS
)
def get_timemarker_plot_options() -> dict:
    """Get current timemarker plot options"""
    return data_manager.ctx.get_time_marker_plot_options()


@plot_bp.route(Routes.GET_TS_FMRI_PLOTTED.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in get ts fmri plotted request',
    log_msg='Retrieved ts fmri plotted successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TS_FMRI_PLOTTED
)
def get_ts_fmri_plotted() -> dict:
    """Get whether an fmri timecourse is plotted"""
    return {'ts_fmri_plotted': data_manager.ctx.ts_fmri_plotted}


@plot_bp.route(Routes.MOVE_ANNOTATION_SELECTION.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in move annotation selection request',
    log_msg='Moved annotation selection successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.MOVE_ANNOTATION_SELECTION
)
def move_annotation_selection() -> dict:
    """Move annotation selection"""
    direction = convert_value(request.form['direction'])
    selected_marker = data_manager.ctx.move_annotation_selection(direction)
    return {'selected_marker': selected_marker}


@plot_bp.route(Routes.REMOVE_DISTANCE_PLOT.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in remove distance plot request',
    log_msg='Removed distance plot successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.REMOVE_DISTANCE_PLOT
)
def remove_distance_plot() -> dict:
    """Remove distance plot"""
    data_manager.ctx.clear_distance_plot_state()
    return {'status': 'success'}


@plot_bp.route(Routes.RESET_FMRI_COLOR_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in reset fMRI color options request',
    log_msg='Reset fMRI color options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.RESET_FMRI_COLOR_OPTIONS
)
def reset_fmri_color_options() -> dict:
    """Reset fMRI color options to defaults."""
    data_manager.ctx.reset_fmri_color_options()
    return {'status': 'success'}


@plot_bp.route(Routes.RESET_TIMECOURSE_SHIFT.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in reset timecourse shift request',
    log_msg='Reset timecourse shift successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.RESET_TIMECOURSE_SHIFT,
    route_parameters=['label', 'source', 'change_type']
)
def reset_timecourse_shift() -> dict:
    """Reset timecourse shift"""
    label = convert_value(request.form['label'])
    change_type = convert_value(request.form['change_type'])
    source = convert_value(request.form['source'])
    data_manager.ctx.reset_timecourse_shift(label, change_type, source)
    return {'status': 'success'}


@plot_bp.route(Routes.UNDO_ANNOTATION_MARKER.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in undo annotation marker request',
    log_msg='Undid annotation marker successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UNDO_ANNOTATION_MARKER
)
def undo_annotation_marker() -> dict:
    """Undo annotation marker"""
    data_manager.ctx.pop_annotation_marker()
    # get current annotation markers
    markers = data_manager.ctx.annotation_markers
    # check if there are any markers
    if len(markers) > 0:
        # get most recent marker
        marker = markers[-1]
    else:
        marker = None
    return {'marker': marker}


@plot_bp.route(Routes.UPDATE_DISTANCE_PLOT_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in distance plot options update request',
    log_msg='Updated distance plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_DISTANCE_PLOT_OPTIONS,
    route_parameters=['distance_plot_options']
)
def update_distance_plot_options() -> dict:
    """Update distance plot options"""
    distance_plot_options = json.loads(request.form['distance_plot_options'])
    data_manager.ctx.update_distance_plot_options(distance_plot_options)
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_FMRI_PLOT_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in fMRI plot options update request',
    log_msg='Updated fMRI plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_FMRI_PLOT_OPTIONS,
    route_parameters=['fmri_plot_options']
)
def update_fmri_plot_options() -> dict:
    """Update plot options based on form data."""
    fmri_plot_options = json.loads(request.form['fmri_plot_options'])
    data_manager.ctx.update_fmri_plot_options(fmri_plot_options)
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_ANNOTATION_MARKER_PLOT_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in update annotation marker plot options request',
    log_msg='Updated annotation marker plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_ANNOTATION_MARKER_PLOT_OPTIONS,
    route_parameters=['annotation_marker_plot_options']
)
def update_annotation_marker_plot_options() -> dict:
    """Update annotation marker plot options"""
    annotation_marker_plot_options = json.loads(
        request.form['annotation_marker_plot_options']
    )
    data_manager.ctx.update_annotation_marker_plot_options(
        annotation_marker_plot_options
    )
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_NIFTI_VIEW_STATE.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in nifti view state update request',
    log_msg='Updated nifti view state successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_NIFTI_VIEW_STATE,
    route_parameters=['view_state']
)
def update_nifti_view_state() -> dict:
    """Update nifti view state"""
    view_state = convert_value(request.form['view_state'])
    data_manager.ctx.update_view_state(view_state)
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_TASK_DESIGN_PLOT_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in task design plot options update request',
    log_msg='Updated task design plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_TASK_DESIGN_PLOT_OPTIONS,
    route_parameters=['label']
)
def update_task_design_plot_options() -> dict:
    """Update task design plot options"""
    label = convert_value(request.form['label'])
    task_design_plot_options = json.loads(request.form['task_design_plot_options'])
    data_manager.ctx.update_task_design_plot_options(label, task_design_plot_options)
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse global plot options update request',
    log_msg='Updated timecourse global plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS,
    route_parameters=['timecourse_global_plot_options']
)
def update_timecourse_global_plot_options() -> dict:
    """Update timecourse global plot options"""
    timecourse_global_plot_options = json.loads(
        request.form['timecourse_global_plot_options']
    )
    data_manager.ctx.update_timecourse_global_plot_options(
        timecourse_global_plot_options
    )
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_TIMECOURSE_PLOT_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse plot options update request',
    log_msg='Updated timecourse plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_TIMECOURSE_PLOT_OPTIONS,
    route_parameters=['label', 'timecourse_plot_options']
)
def update_timecourse_plot_options() -> dict:
    """Update timecourse plot options"""
    label = convert_value(request.form['label'])
    timecourse_plot_options = json.loads(request.form['timecourse_plot_options'])
    # convert values
    timecourse_plot_options = {
        convert_value(key): convert_value(value)
        for key, value in timecourse_plot_options.items()
    }
    data_manager.ctx.update_timecourse_plot_options(label, timecourse_plot_options)
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_TIMECOURSE_SHIFT.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse shift update request',
    log_msg='Updated timecourse shift successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_TIMECOURSE_SHIFT,
    route_parameters=['label', 'source', 'change_type', 'change_direction']
)
def update_timecourse_shift() -> dict:
    """Update timecourse shift"""
    label = convert_value(request.form['label'])
    source = convert_value(request.form['source'])
    change_type = convert_value(request.form['change_type'])
    change_direction = convert_value(request.form['change_direction'])
    data_manager.ctx.update_timecourse_shift(label, source, change_type, change_direction)
    return {'status': 'success'}


@plot_bp.route(Routes.UPDATE_TIMEMARKER_PLOT_OPTIONS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timemarker plot options update request',
    log_msg='Updated timemarker plot options successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_TIMEMARKER_PLOT_OPTIONS,
    route_parameters=['timemarker_plot_options']
)
def update_timemarker_plot_options() -> dict:
    """Update timemarker plot options"""
    timemarker_plot_options = json.loads(request.form['timemarker_plot_options'])
    data_manager.ctx.update_time_marker_plot_options(timemarker_plot_options)
    return {'status': 'success'}

