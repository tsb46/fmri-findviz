"""
Viewer data routes

Routes:
    CONVERT_TIMEPOINTS: Convert timepoints to seconds
    GET_CLICK_COORDS: Get click coords
    GET_COORD_LABELS: Get coordinate labels
    GET_CROSSHAIR_COORDS: Get crosshair coords
    GET_DIRECTION_LABEL_COORDS: Get direction label coords
    GET_DISTANCE_DATA: Get distance data
    GET_FMRI_DATA: Get FMRI data
    GET_LAST_TIMECOURSE: Get last added fmri timecourse
    GET_MONTAGE_DATA: Get montage data
    GET_TASK_CONDITIONS: Get task conditions
    GET_TIMECOURSE_DATA: Get timecourse data
    GET_TIMECOURSE_LABELS: Get timecourse labels
    GET_TIMECOURSE_SOURCE: Get timecourse source
    GET_TIMEPOINT: Get timepoint
    GET_TIMEPOINTS: Get timepoints
    GET_VERTEX_COORDS: Get vertex coordinates
    GET_VIEWER_METADATA: Get viewer metadata
    GET_VOXEL_COORDS: Get voxel coordinates
    GET_WORLD_COORDS: Get world coordinates
    POP_FMRI_TIMECOURSE: Pop fmri timecourse
    REMOVE_FMRI_TIMECOURSES: Remove all fmri timecourses
    UPDATE_LOCATION: Update location
    UPDATE_FUNCTIONAL_TIMECOURSE: Update functional timecourse
    UPDATE_MONTAGE_SLICE_DIR: Update montage slice direction
    UPDATE_MONTAGE_SLICE_IDX: Update montage slice indices
    UPDATE_TIMEPOINT: Update timepoint
    UPDATE_TR: Update TR
"""
import json

from typing import List, Tuple
from flask import Blueprint, request

from findviz.logger_config import setup_logger
from findviz.routes.utils import (
    convert_value,
    handle_context, 
    handle_route_errors, 
    Routes
)
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


@data_bp.route(Routes.CONVERT_TIMEPOINTS.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timepoints conversion request',
    log_msg='Timepoints conversion request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.CONVERT_TIMEPOINTS
)
def convert_timepoints() -> dict:
    """Convert timepoints to seconds"""
    data_manager.ctx.convert_timepoints()
    return {'status': 'success'}


@data_bp.route(Routes.GET_CLICK_COORDS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in click coords request',
    log_msg='Click coords request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_CLICK_COORDS
)
def get_click_coords() -> dict:
    """Get click coords"""
    return data_manager.ctx.get_click_coords()


@data_bp.route(Routes.GET_COORD_LABELS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in coordinate labels request',
    log_msg='Coordinate labels request successful',
    route=Routes.GET_COORD_LABELS
)
def get_coord_labels() -> dict:
    """Get coordinate labels"""
    if data_manager.ctx.fmri_file_type == 'nifti':
        return data_manager.ctx.coord_labels
    else:
        coord_labels = data_manager.ctx.coord_labels
        return {
            'left_coord_labels': coord_labels[0],
            'right_coord_labels': coord_labels[1]
        }


@data_bp.route(Routes.GET_CROSSHAIR_COORDS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in crosshair data request',
    log_msg='Crosshair data request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_CROSSHAIR_COORDS
)
def get_crosshair_coords() -> dict:
    """Get crosshair coordinates"""
    return data_manager.ctx.get_crosshair_coords()


@data_bp.route(Routes.GET_DIRECTION_LABEL_COORDS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in direction label coords request',
    log_msg='Direction label coords request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_DIRECTION_LABEL_COORDS
)
def get_direction_label_coords() -> dict:
    """Get direction label coordinates"""
    return data_manager.ctx.get_direction_label_coords()


@data_bp.route(Routes.GET_DISTANCE_DATA.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in distance data request',
    log_msg='Distance data request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_DISTANCE_DATA
)
def get_distance_data() -> list[float]:
    """Get distance data"""
    return data_manager.ctx.distance_data.tolist()


@data_bp.route(Routes.GET_FMRI_DATA.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in data update request',
    log_msg='Data update request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_FMRI_DATA
)
def get_fmri_data() -> dict:
    """Get FMRI data for the current timepoint and location."""
    # get plot options data from data manager
    plot_options = data_manager.ctx.get_fmri_plot_options()

    # get viewer data from data manager
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
    )

    # pass viewer data to get_timepoint_data
    if data_manager.ctx.fmri_file_type == 'nifti':
        slice_idx = data_manager.ctx.get_slice_idx()
        timepoint_data = get_nifti_data(
            time_point=data_manager.ctx.timepoint,
            func_img=viewer_data['func_img'],
            coord_labels=data_manager.ctx.coord_labels,
            slice_idx=slice_idx,
            view_state=data_manager.ctx.view_state,
            montage_slice_dir=data_manager.ctx.montage_slice_dir,
            threshold_min=plot_options['threshold_min'],
            threshold_max=plot_options['threshold_max'],
            threshold_min_orig = data_manager.ctx.color_options_original['threshold_min'],
            threshold_max_orig = data_manager.ctx.color_options_original['threshold_max'],
            anat_img=viewer_data['anat_img']
        )
    else:
        timepoint_data = get_gifti_data(
            time_point=data_manager.ctx.timepoint,
            left_func_img=viewer_data['left_func_img'],
            right_func_img=viewer_data['right_func_img'],
            threshold_min=plot_options['threshold_min'],
            threshold_max=plot_options['threshold_max'],
            threshold_min_orig = data_manager.ctx.color_options_original['threshold_min'],
            threshold_max_orig = data_manager.ctx.color_options_original['threshold_max'],
        )

    return {
        'data': timepoint_data,
        'plot_options': plot_options
    }


@data_bp.route(Routes.GET_LAST_TIMECOURSE.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in last fmri timecourse request',
    log_msg='Last fmri timecourse request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_LAST_TIMECOURSE
)
def get_last_timecourse() -> dict:
    """Get last added fmri timecourse"""
    return data_manager.ctx.get_last_timecourse()


@data_bp.route(Routes.GET_MONTAGE_DATA.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in montage data request',
    log_msg='Montage data request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_MONTAGE_DATA
)
def get_montage_data() -> dict:
    """Get montage data for the current location."""
    montage_data = {
        'montage_slice_dir': data_manager.ctx.montage_slice_dir,
        'montage_slice_idx': data_manager.ctx.montage_slice_idx,
        'montage_slice_len': data_manager.ctx.slice_len
    }
    return montage_data


@data_bp.route(Routes.GET_TASK_CONDITIONS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in task conditions request',
    log_msg='Task conditions request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TASK_CONDITIONS
)
def get_task_conditions() -> list[str]:
    """Get task conditions"""
    return data_manager.ctx.task_conditions


@data_bp.route(Routes.GET_TIMECOURSE_LABELS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse labels request',
    log_msg='Timecourse labels request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMECOURSE_LABELS
)
def get_timecourse_labels() -> list[str]:
    """Get timecourse labels"""
    return data_manager.ctx.ts_labels


@data_bp.route(Routes.GET_TIMECOURSE_LABELS_PREPROCESSED.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in preprocessed timecourse labels request',
    log_msg='Preprocessed timecourse labels request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMECOURSE_LABELS_PREPROCESSED
)
def get_timecourse_labels_preprocessed() -> list[str]:
    """Get preprocessed timecourse labels"""
    return data_manager.ctx.ts_labels_preprocessed


@data_bp.route(Routes.GET_TIMECOURSE_DATA.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse data request',
    log_msg='Timecourse data request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMECOURSE_DATA,
    route_parameters=['ts_labels']
)
def get_timecourse_data() -> dict:
    """Get timecourse data for the current location."""
    ts_labels = json.loads(request.args['ts_labels'])
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=False,
        time_course_data=True,
        task_data=True,
    )
    timecourse_data = {}
    # add timecourse data if it exists
    if 'ts' in viewer_data:
        timecourse_data.update(viewer_data['ts'])
    # add task data if it exists
    if 'task' in viewer_data:
        timecourse_data.update(viewer_data['task'])
        
    # filter timecourse data to only include the requested ts_labels (if passed)
    if ts_labels is not None:
        timecourse_data = {
            ts_label: timecourse_data[ts_label]
            for ts_label in ts_labels
            if ts_label in timecourse_data
        }
    return timecourse_data


@data_bp.route(Routes.GET_TIMECOURSE_SOURCE.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timecourse source request',
    log_msg='Timecourse source request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMECOURSE_SOURCE
)
def get_timecourse_source() -> dict:
    """Get timecourse source"""
    return {'timecourse_source': data_manager.ctx.timecourse_source}


@data_bp.route(Routes.GET_TIMEPOINT.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timepoint request',
    log_msg='Timepoint request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_TIMEPOINT
)
def get_timepoint() -> dict:
    """Get currently selected timepoint"""
    return {'timepoint': data_manager.ctx.timepoint}


@data_bp.route(Routes.GET_TIMEPOINTS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timepoints request',
    log_msg='Timepoints request successful',
    route=Routes.GET_TIMEPOINTS
)
def get_timepoints() -> dict:
    """Get all timepoints"""
    return {'timepoints': data_manager.ctx.get_timepoints()}


@data_bp.route(Routes.GET_VERTEX_COORDS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in vertex coordinates request',
    log_msg='Vertex coordinates request successful',
    route=Routes.GET_VERTEX_COORDS
)
def get_vertex_coords() -> dict:
    """Get vertex coordinates"""
    return {
        'vertex_number': data_manager.ctx.selected_vertex,
        'selected_hemisphere': data_manager.ctx.selected_hemi
    }

@data_bp.route(Routes.GET_VIEWER_METADATA.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in viewer metadata request',
    log_msg='Viewer metadata request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_VIEWER_METADATA
)
def get_viewer_metadata() -> dict:
    """Get viewer metadata"""
    return data_manager.ctx.get_viewer_metadata()


@data_bp.route(Routes.GET_VOXEL_COORDS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in voxel coordinates request',
    log_msg='Voxel coordinates request successful',
    route=Routes.GET_VOXEL_COORDS
)
def get_voxel_coords() -> dict:
    """Get voxel coordinates"""
    voxel_coords = data_manager.ctx.get_slice_idx()
    if data_manager.ctx.view_state == 'montage':
        voxel_coords = voxel_coords[data_manager.ctx.selected_slice]

    return voxel_coords


@data_bp.route(Routes.GET_WORLD_COORDS.value, methods=['GET'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in world coordinates request',
    log_msg='World coordinates request successful',
    route=Routes.GET_WORLD_COORDS
)
def get_world_coords() -> dict:
    world_coords = data_manager.ctx.get_world_coords()
    # package world coords into a dictionary
    world_coords_dict = {
        'x': world_coords[0],
        'y': world_coords[1],
        'z': world_coords[2]
    }
    return world_coords_dict


@data_bp.route(Routes.POP_FMRI_TIMECOURSE.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in fmri timecourse pop request',
    log_msg='Fmri timecourse pop request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.POP_FMRI_TIMECOURSE
)
def pop_fmri_timecourse() -> dict:
    """Pop fmri timecourse"""
    label = data_manager.ctx.pop_fmri_timecourse()
    return {'label': label}


@data_bp.route(Routes.REMOVE_FMRI_TIMECOURSES.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in fmri timecourse remove request',
    log_msg='Fmri timecourse remove request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.REMOVE_FMRI_TIMECOURSES
)
def remove_fmri_timecourses() -> dict:
    """Remove all fmri timecourses"""
    labels = data_manager.ctx.remove_fmri_timecourses()
    return {'labels': labels}


@data_bp.route(Routes.UPDATE_LOCATION.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in location update request',
    log_msg='Location update successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_LOCATION,
    route_parameters=['click_coords', 'slice_name']
)
def update_location() -> dict:
    """Update current location based on form data."""
    click_coords = json.loads(request.form['click_coords'])
    slice_name = request.form['slice_name']
    data_manager.ctx.update_location(click_coords, slice_name)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_FMRI_TIMECOURSE.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in fmri timecourse update request',
    log_msg='Fmri timecourse update request successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_FMRI_TIMECOURSE
)
def update_fmri_timecourse() -> dict:
    """Update fmri timecourse data for the current location."""
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
    )

    if data_manager.ctx.fmri_file_type == 'nifti':
        slice_idx = data_manager.ctx.get_slice_idx()
        # if montage view, get slice idx of currently selected slice
        if data_manager.ctx.view_state == 'montage':
            slice_idx = slice_idx[data_manager.ctx.selected_slice]
        timecourse_data, voxel_label = get_timecourse_nifti(
            func_img=viewer_data['func_img'],
            x=slice_idx['x'],
            y=slice_idx['y'],
            z=slice_idx['z']
        )
    else:
        click_coords = data_manager.ctx.get_click_coords()
        timecourse_data, voxel_label = get_timecourse_gifti(
            left_func_img=viewer_data['left_func_img'],
            right_func_img=viewer_data['right_func_img'],
            vertex_index=click_coords['selected_vertex'],
            hemisphere=click_coords['selected_hemi']
        )

    data_manager.ctx.update_timecourse(timecourse_data, voxel_label)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_MONTAGE_SLICE_DIR.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in montage slice direction update request',
    log_msg='Montage slice direction update successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_MONTAGE_SLICE_DIR,
    route_parameters=['montage_slice_dir']
)
def update_montage_slice_dir() -> dict:
    """Update montage slice direction"""
    montage_slice_dir = request.form['montage_slice_dir']
    data_manager.ctx.update_montage_slice_dir(montage_slice_dir)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_MONTAGE_SLICE_IDX.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in montage slice indices update request',
    log_msg='Montage slice indices update successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_MONTAGE_SLICE_IDX,
    route_parameters=['slice_name', 'slice_idx']
)
def update_montage_slice_idx() -> dict:
    """Update montage slice indices from slider changes"""
    slice_name = convert_value(request.form['slice_name'])
    slice_idx = convert_value(request.form['slice_idx'])
    data_manager.ctx.update_montage_slice_idx(slice_name, slice_idx)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_TIMEPOINT.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in timepoint update request',
    log_msg='Timepoint update successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.UPDATE_TIMEPOINT,
    route_parameters=['time_point']
)
def update_timepoint() -> dict:
    """Update current timepoint based on form data."""
    timepoint = convert_value(request.form['time_point'])
    data_manager.ctx.update_timepoint(timepoint)
    return {'status': 'success'}


@data_bp.route(Routes.UPDATE_TR.value, methods=['POST'])
@handle_context()
@handle_route_errors(
    error_msg='Unknown error in TR update request',
    log_msg='TR update successful',
    route=Routes.UPDATE_TR
)
def update_tr() -> dict:
    """Update TR"""
    tr = convert_value(request.form['tr'])
    data_manager.ctx.set_tr(tr)
    return {'status': 'success'}
