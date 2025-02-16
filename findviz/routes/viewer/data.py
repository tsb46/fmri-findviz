"""
Viewer routes

Routes:
    GET_CLICK_COORDS: Get click coords
    GET_CROSSHAIR_COORDS: Get crosshair coords
    GET_DIRECTION_LABEL_COORDS: Get direction label coords
    GET_DISTANCE_DATA: Get distance data
    GET_FMRI_DATA: Get FMRI data
    GET_FUNCTIONAL_TIMECOURSE: Get functional timecourse
    GET_MONTAGE_DATA: Get montage data
    GET_SLICE_LENGTHS: Get slice lengths
    GET_TASK_CONDITIONS: Get task conditions
    GET_TIMECOURSE_DATA: Get timecourse data
    GET_TIMECOURSE_LABELS: Get timecourse labels
    GET_TIMECOURSE_SOURCE: Get timecourse source
    GET_TIMEPOINT: Get timepoint
    GET_VIEWER_METADATA: Get viewer metadata
    POP_FMRI_TIMECOURSE: Pop fmri timecourse
    REMOVE_FMRI_TIMECOURSES: Remove all fmri timecourses
    UPDATE_LOCATION: Update location
    UPDATE_FUNCTIONAL_TIMECOURSE: Update functional timecourse
    UPDATE_MONTAGE_SLICE_DIR: Update montage slice direction
    UPDATE_MONTAGE_SLICE_IDX: Update montage slice indices
    UPDATE_TIMEPOINT: Update timepoint
"""
import json

from typing import List, Tuple
from flask import Blueprint, request

from findviz.logger_config import setup_logger
from findviz.routes.utils import Routes, handle_route_errors, convert_value
from findviz.routes.shared import data_manager
from findviz.routes.viewer.nifti import (
    get_nifti_data, get_timecourse_nifti
)
from findviz.routes.viewer.gifti import (
    get_gifti_data, get_timecourse_gifti
)

# Set up a logger for the app
logger = setup_logger(__name__)

data_bp = Blueprint('data', __name__)

@data_bp.route(Routes.CHANGE_TIMECOURSE_SCALE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in timecourse scale change request',
    log_msg='Timecourse scale change request successful',
    route=Routes.CHANGE_TIMECOURSE_SCALE,
    route_parameters=['label', 'scale_change', 'scale_change_unit']
)
def change_timecourse_scale() -> dict:
    """Change timecourse scale"""
    label = request.form['label']
    scale_change = request.form['scale_change']
    scale_change_unit = request.form['scale_change_unit']
    data_manager.change_timecourse_scale(label, scale_change, scale_change_unit)
    return {'status': 'success'}


@data_bp.route(Routes.GET_CLICK_COORDS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in click coords request',
    log_msg='Click coords request successful',
    route=Routes.GET_CLICK_COORDS
)
def get_click_coords() -> dict:
    """Get click coords"""
    return data_manager.get_click_coords()


@data_bp.route(Routes.GET_CROSSHAIR_COORDS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in crosshair data request',
    log_msg='Crosshair data request successful',
    route=Routes.GET_CROSSHAIR_COORDS
)
def get_crosshair_coords() -> dict:
    """Get crosshair coordinates"""
    return data_manager.get_crosshair_coords()


@data_bp.route(Routes.GET_DIRECTION_LABEL_COORDS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in direction label coords request',
    log_msg='Direction label coords request successful',
    route=Routes.GET_DIRECTION_LABEL_COORDS
)
def get_direction_label_coords() -> dict:
    """Get direction label coordinates"""
    return data_manager.get_direction_label_coords()


@data_bp.route(Routes.GET_DISTANCE_DATA.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in distance data request',
    log_msg='Distance data request successful',
    route=Routes.GET_DISTANCE_DATA
)
def get_distance_data() -> list[float]:
    """Get distance data"""
    return data_manager.distance_data.tolist()


@data_bp.route(Routes.GET_FMRI_DATA.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in data update request',
    log_msg='Data update request successful',
    fmri_file_type=data_manager.fmri_file_type,
    route=Routes.GET_FMRI_DATA
)
def get_fmri_data() -> dict:
    """Get FMRI data for the current timepoint and location."""
    # get plot options data from data manager
    plot_options = data_manager.get_fmri_plot_options()

    # get viewer data from data manager
    viewer_data = data_manager.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
    )
    
    # pass viewer data to get_timepoint_data
    if data_manager.fmri_file_type == 'nifti':
        slice_idx = data_manager.get_slice_idx()
        timepoint_data = get_nifti_data(
            time_point=data_manager.timepoint,
            func_img=viewer_data['func_img'],
            coord_labels=data_manager.coord_labels,
            slice_idx=slice_idx,
            view_state=data_manager.view_state,
            montage_slice_dir=data_manager.montage_slice_dir,
            threshold_min=plot_options['threshold_min'],
            threshold_max=plot_options['threshold_max'],
            anat_img=viewer_data['anat_img']
        )
    else:
        timepoint_data = get_gifti_data(
            time_point=data_manager.timepoint,
            func_left_img=viewer_data['func_left_img'],
            func_right_img=viewer_data['func_right_img'],
            threshold_min=plot_options['threshold_min'],
            threshold_max=plot_options['threshold_max']
        )

    return {
        'data': timepoint_data,
        'plot_options': plot_options
    }


@data_bp.route(Routes.GET_MONTAGE_DATA.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in montage data request',
    log_msg='Montage data request successful',
    route=Routes.GET_MONTAGE_DATA
)
def get_montage_data() -> dict:
    """Get montage data for the current location."""
    montage_data = {
        'montage_slice_dir': data_manager.montage_slice_dir,
        'montage_slice_idx': data_manager._state.montage_slice_idx,
        'montage_slice_len': data_manager.slice_len
    }
    return montage_data


@data_bp.route(Routes.GET_SLICE_LENGTHS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in slice lengths request',
    log_msg='Slice lengths request successful',
    route=Routes.GET_SLICE_LENGTHS
)
def get_slice_lengths() -> list[float]:
    """Get slice lengths"""
    return data_manager.slice_len


@data_bp.route(Routes.GET_TASK_CONDITIONS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in task conditions request',
    log_msg='Task conditions request successful',
    route=Routes.GET_TASK_CONDITIONS
)
def get_task_conditions() -> list[str]:
    """Get task conditions"""
    return data_manager.task_conditions


@data_bp.route(Routes.GET_TIMECOURSE_LABELS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in timecourse labels request',
    log_msg='Timecourse labels request successful',
    route=Routes.GET_TIMECOURSE_LABELS
)
def get_timecourse_labels() -> list[str]:
    """Get timecourse labels"""
    return data_manager.ts_labels


@data_bp.route(Routes.GET_TIMECOURSE_DATA.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in timecourse data request',
    log_msg='Timecourse data request successful',
    fmri_file_type=data_manager.fmri_file_type,
    route=Routes.GET_TIMECOURSE_DATA
)
def get_timecourse_data() -> dict:
    """Get timecourse data for the current location."""
    viewer_data = data_manager.get_viewer_data(
        fmri_data=False,
        time_course_data=True,
        task_data=True,
    )
    timecourse_data = viewer_data['ts']
    timecourse_data.extend(viewer_data['task'])
    return timecourse_data


@data_bp.route(Routes.GET_TIMECOURSE_SOURCE.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in timecourse source request',
    log_msg='Timecourse source request successful',
    route=Routes.GET_TIMECOURSE_SOURCE
)
def get_timecourse_source() -> dict:
    """Get timecourse source"""
    return {'timecourse_source': data_manager.timecourse_source}


@data_bp.route(Routes.GET_TIMEPOINT.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in timepoint request',
    log_msg='Timepoint request successful',
    route=Routes.GET_TIMEPOINT
)
def get_timepoint() -> dict:
    """Get current timepoint"""
    return {'timepoint': data_manager.timepoint}


@data_bp.route(Routes.GET_VIEWER_METADATA.value, methods=['GET'])
@handle_route_errors(
    error_msg='Unknown error in viewer metadata request',
    log_msg='Viewer metadata request successful',
    route=Routes.GET_VIEWER_METADATA
)
def get_viewer_metadata() -> dict:
    """Get viewer metadata"""
    return data_manager.get_viewer_metadata()


@data_bp.route(Routes.POP_FMRI_TIMECOURSE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in fmri timecourse pop request',
    log_msg='Fmri timecourse pop request successful',
    route=Routes.POP_FMRI_TIMECOURSE
)
def pop_fmri_timecourse() -> dict:
    """Pop fmri timecourse"""
    data_manager.pop_fmri_timecourse()
    return {'status': 'success'}


@data_bp.route(Routes.REMOVE_FMRI_TIMECOURSES.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in fmri timecourse remove request',
    log_msg='Fmri timecourse remove request successful',
    route=Routes.REMOVE_FMRI_TIMECOURSES
)
def remove_fmri_timecourses() -> dict:
    """Remove all fmri timecourses"""
    data_manager.remove_fmri_timecourses()
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_LOCATION.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in location update request',
    log_msg='Location update successful',
    fmri_file_type=data_manager.fmri_file_type,
    route=Routes.UPDATE_LOCATION,
    route_parameters=['click_coords', 'slice_name']
)
def update_location() -> dict:
    """Update current location based on form data."""
    click_coords = json.loads(request.form['click_coords'])
    slice_name = request.form['slice_name']
    data_manager.update_location(click_coords, slice_name)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_FUNCTIONAL_TIMECOURSE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in functional timecourse update request',
    log_msg='Functional timecourse update request successful',
    fmri_file_type=data_manager.fmri_file_type,
    route=Routes.UPDATE_FUNCTIONAL_TIMECOURSE
)
def update_functional_timecourse() -> dict:
    """Update functional timecourse data for the current location."""
    viewer_data = data_manager.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
    )

    if data_manager.fmri_file_type == 'nifti':
        slice_idx = data_manager.get_slice_idx()
        timecourse_data, voxel_label = get_timecourse_nifti(
            func_img=viewer_data['func_img'],
            x=slice_idx['x'],
            y=slice_idx['y'],
            z=slice_idx['z']
        )
    else:
        click_coords = data_manager.get_click_coords()
        timecourse_data, voxel_label = get_timecourse_gifti(
            func_left_img=viewer_data['func_left_img'],
            func_right_img=viewer_data['func_right_img'],
            vertex_index=click_coords['selected_vertex'],
            hemisphere=click_coords['selected_hemi']
        )

    data_manager.update_timecourse(timecourse_data, voxel_label)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_MONTAGE_SLICE_DIR.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in montage slice direction update request',
    log_msg='Montage slice direction update successful',
    route=Routes.UPDATE_MONTAGE_SLICE_DIR,
    route_parameters=['montage_slice_dir']
)
def update_montage_slice_dir() -> dict:
    """Update montage slice direction"""
    montage_slice_dir = request.form['montage_slice_dir']
    data_manager.update_montage_slice_dir(montage_slice_dir)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_MONTAGE_SLICE_IDX.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in montage slice indices update request',
    log_msg='Montage slice indices update successful',
    route=Routes.UPDATE_MONTAGE_SLICE_IDX,
    route_parameters=['slice_name', 'slice_idx']
)
def update_montage_slice_idx() -> dict:
    """Update montage slice indices from slider changes"""
    slice_name = convert_value(request.form['slice_name'])
    slice_idx = convert_value(request.form['slice_idx'])
    data_manager.update_montage_slice_idx(slice_name, slice_idx)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_TIMEPOINT.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in timepoint update request',
    log_msg='Timepoint update successful',
    fmri_file_type=data_manager.fmri_file_type,
    route=Routes.UPDATE_TIMEPOINT,
    route_parameters=['time_point']
)
def update_timepoint() -> dict:
    """Update current timepoint based on form data."""
    timepoint = convert_value(request.form['time_point'])
    data_manager.update_timepoint(timepoint)
    return {'status': 'success'}


