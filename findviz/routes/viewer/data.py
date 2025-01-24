"""
Viewer routes

Routes:
    GET_FMRI_DATA: Get FMRI data
    GET_FUNCTIONAL_TIMECOURSE: Get functional timecourse
    UPDATE_LOCATION: Update location
    UPDATE_TIMEPOINT: Update timepoint
"""

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.routes.utils import Routes
from findviz.routes.shared import data_manager
from findviz.routes.viewer.nifti import (
    get_nifti_timepoint_data, get_timecourse_nifti
)
from findviz.routes.viewer.gifti import (
    get_gifti_timepoint_data, get_timecourse_gifti
)
from findviz.viz.exception import DataRequestError

# Set up a logger for the app
logger = setup_logger(__name__)

data_bp = Blueprint('data', __name__)

@data_bp.route(Routes.GET_FMRI_DATA.value, methods=['GET'])
def get_fmri_data() -> tuple[dict, int]:
    """Get FMRI data for the current timepoint and location.
    
    Returns:
        tuple[dict, int]: A tuple containing:
            - dict: Response data with keys:
                - timepoint_data: Current timepoint data
                - plot_options: Current plot options
            - int: HTTP status code (200 for success, 400/500 for errors)
    
    Raises:
        DataRequestError: If required data fields are missing
        Exception: For unexpected errors
    """
    logger.info("Handling data update request")
    fmri_file_type = data_manager.get_file_type()
    # get location and plot options data from data manager
    loc_data = data_manager.get_location_data()
    plot_options = data_manager.get_plot_options()
    try:
        # get viewer data from data manager
        viewer_data = data_manager.get_viewer_data(
            fmri_data=True,
            time_course_data=False,
            task_data=False,
        )
        # pass viewer data to get_timepoint_data
        if fmri_file_type == 'nifti':
            timepoint_data = get_nifti_timepoint_data(
                time_point=data_manager.timepoint,
                func_img=viewer_data['func_img'],
                x_slice=loc_data['x'],
                y_slice=loc_data['y'],
                z_slice=loc_data['z'],
                view_state=data_manager.view_state,
                montage_slice_dir=data_manager.montage_slice_dir,
                threshold_min=plot_options['threshold_min'],
                threshold_max=plot_options['threshold_max'],
                anat_img=viewer_data['anat_img']
            )
        else:
            timepoint_data = get_gifti_timepoint_data(
                time_point=data_manager.timepoint,
                func_left_img=viewer_data['func_left_img'],
                func_right_img=viewer_data['func_right_img'],
                threshold_min=plot_options['threshold_min'],
                threshold_max=plot_options['threshold_max']
            )

    except KeyError as e:
        data_error = DataRequestError(
            message='Error in data update request.',
            fmri_file_type=fmri_file_type,
            route=Routes.GET_DATA_UPDATE,
            input_field=e.args[0]
        )
        logger.error(data_error)
        return make_response(
            data_error.message, 400
        )

    except Exception as e:
        logger.critical("Unknown error in data update request: %s", str(e), exc_info=True)
        msg = f"Unknown error in data update request"
        return make_response(msg, 500)
    
    
    logger.info("Data update request successful")
    return make_response(
        {
            'timepoint_data': timepoint_data,
            'plot_options': plot_options
        }, 200
    )

@data_bp.route(Routes.GET_FUNCTIONAL_TIMECOURSE.value, methods=['GET'])
def get_functional_timecourse() -> tuple[dict, int]:
    """Get functional timecourse data for the current location.
    
    Returns:
        tuple[dict, int]: A tuple containing:
            - dict: Timecourse data for the current location
            - int: HTTP status code (200 for success, 400/500 for errors)
    
    Raises:
        DataRequestError: If required data fields are missing
        Exception: For unexpected errors
    """
    fmri_file_type = data_manager.get_file_type()
    try:
        viewer_data = data_manager.get_viewer_data(
            fmri_data=True,
            time_course_data=False,
            task_data=False,
        )
        # get location data from data manager
        loc_data = data_manager.get_location_data()

        if fmri_file_type == 'nifti':
            timecourse_data, voxel_label = get_timecourse_nifti(
                func_img=viewer_data['func_img'],
                x=loc_data['x'],
                y=loc_data['y'],
                z=loc_data['z']
            )
        else:
            timecourse_data, voxel_label = get_timecourse_gifti(
                func_left_img=viewer_data['func_left_img'],
                func_right_img=viewer_data['func_right_img'],
                vertex_index=loc_data['selected_vertex'],
                hemisphere=loc_data['selected_hemi']
            )

    except KeyError as e:
        data_error = DataRequestError(
            message='Error in functional timecourse request.',
            fmri_file_type=fmri_file_type,
            route=Routes.GET_FUNCTIONAL_TIMECOURSE,
            input_field=e.args[0]   
        )
        logger.error(data_error)
        return make_response(data_error.message, 400)
    except Exception as e:
        logger.critical("Unknown error in functional timecourse request: %s", str(e), exc_info=True)
        msg = f"Unknown error in functional timecourse request"
        return make_response(msg, 500)

    # add time course data to data manager
    data_manager.update_timecourse(timecourse_data, voxel_label)

    return make_response(timecourse_data, 200)



@data_bp.route(Routes.UPDATE_LOCATION.value, methods=['POST'])
def update_location() -> tuple[int, int]:
    """Update current location based on form data.
    
    For NIFTI files, expects form data with:
        - x_slice: X coordinate
        - y_slice: Y coordinate 
        - z_slice: Z coordinate
    
    For GIFTI files, expects form data with:
        - vertex_index: Selected vertex index
        - hemisphere: Selected hemisphere
    
    Returns:
        tuple[int, int]: A tuple containing:
            - int: HTTP status code (200 for success)
            - int: HTTP status code (400/500 for errors)
    
    Raises:
        DataRequestError: If required form fields are missing
        Exception: For unexpected errors
    """
    try:
        fmri_file_type = data_manager.get_file_type()
        if fmri_file_type == 'nifti':
            x_slice = request.form['x_slice']
            y_slice = request.form['y_slice']
            z_slice = request.form['z_slice']
            loc_data = {
                'x': int(x_slice),
                'y': int(y_slice),
                'z': int(z_slice)
            }
        else:
            vertex_index = request.form['vertex_index']
            hemisphere = request.form['hemisphere']
            loc_data = {
                'selected_vertex': int(vertex_index),
                'selected_hemi': hemisphere
            }
        data_manager.update_location(loc_data)
        return make_response(200)
    except KeyError as e:
        data_error = DataRequestError(
            message='Error in location update request.',
            fmri_file_type=fmri_file_type,
            route=Routes.UPDATE_LOCATION,
            input_field=e.args[0]
        )
        logger.error(data_error)
        return make_response(
            data_error.message, 400
        )
    
    except Exception as e:
        logger.critical("Unknown error in location update request: %s", str(e), exc_info=True)
        msg = f"Unknown error in location update request"
        return make_response(msg, 500)


@data_bp.route(Routes.UPDATE_TIMEPOINT.value, methods=['POST'])
def update_timepoint() -> tuple[int, int]:
    """Update current timepoint based on form data.
    
    Expects form data with:
        - time_point: New timepoint value (integer)
    
    Returns:
        tuple[int, int]: A tuple containing:
            - int: HTTP status code (200 for success)
            - int: HTTP status code (400/500 for errors)
    
    Raises:
        DataRequestError: If time_point field is missing or invalid
        Exception: For unexpected errors
    """
    try:
        # convert timepoint to int
        timepoint = int(request.form['time_point'])
        data_manager.update_timepoint(timepoint)
        return make_response(200)
    except KeyError as e:
        fmri_file_type = data_manager.get_file_type()
        data_error = DataRequestError(
            message='Error in timepoint update request.',
            fmri_file_type=fmri_file_type,
            route=Routes.UPDATE_TIMEPOINT,
            input_field=e.args[0]
        )
        logger.error(data_error)
        return make_response(
            data_error.message, 400
        )
    except Exception as e:
        logger.critical("Unknown error in timepoint update request: %s", str(e), exc_info=True)
        msg = f"Unknown error in timepoint update request"
        return make_response(msg, 500)


