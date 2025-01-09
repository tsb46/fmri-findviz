"""
Viewer routes
"""
from findviz.logger_config import get_logger

from typing import TypedDict, Literal

import nibabel as nib

from flask import Blueprint, request, make_response

from findviz.routes.shared import data_manager
from findviz.routes.viewer.nifti import (
    get_nifti_timepoint_data, get_timecourse_nifti
)
from findviz.routes.viewer.gifti import (
    get_gifti_timepoint_data, get_timecourse_gifti
)
from findviz.viz.exception import DataRequestError, Routes

logger = get_logger(__name__)

viewer_bp = Blueprint('viewer', __name__)

# Input types for viewer routes
class NiftiDataInputs(TypedDict):
    view_state: Literal['axial', 'coronal', 'sagittal']
    montage_slice_dir: Literal['x', 'y', 'z']
    x_slice: int
    y_slice: int
    z_slice: int 
    time_point: int
    use_preprocess: bool
    update_voxel_coord: bool

class GiftiDataInputs(TypedDict):
    time_point: int
    use_preprocess: bool

class NiftiTimecourseInputs(TypedDict):
    x: int
    y: int
    z: int
    use_preprocess: bool

class GiftiTimecourseInputs(TypedDict):
    time_point: int
    vertex_index: int
    hemisphere: Literal['left', 'right']
    use_preprocess: bool


@viewer_bp.route('/get_data_update', methods=['POST'])
def get_data_update():
    logger.info("Handling data update request")
    fmri_file_type = data_manager.get_file_type()
    inputs = request.form
    if fmri_file_type == 'nifti':
        inputs = NiftiDataInputs(**request.form)
    else:
        inputs = GiftiDataInputs(**request.form)
    try:
        # get viewer data from data manager
        viewer_data = data_manager.get_viewer_data(
            fmri_data=True,
            use_preprocess=inputs['use_preprocess'],
            time_course_data=False,
            task_data=False,
        )
        # pass viewer data to get_timepoint_data
        if fmri_file_type == 'nifti':
            timepoint_data = get_nifti_timepoint_data(
                time_point=inputs['time_point'],
                func_img=viewer_data['func_img'],
                x_slice=inputs['x_slice'],
                y_slice=inputs['y_slice'],
                z_slice=inputs['z_slice'],
                view_state=inputs['view_state'],
                anat_img=viewer_data['anat_img'],
                mask_img=viewer_data['mask_img'],
                montage_slice_dir=inputs['montage_slice_dir'],
                update_voxel_coord=inputs['update_voxel_coord']
            )
        else:
            timepoint_data = get_gifti_timepoint_data(
                time_point=inputs['time_point'],
                func_left_img=viewer_data['func_left_img'],
                func_right_img=viewer_data['func_right_img']
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
    
    # update brain location data
    if fmri_file_type == 'nifti':
        loc_data = {
            'x': inputs['x_slice'],
            'y': inputs['y_slice'],
            'z': inputs['z_slice']
        }
    else:
        loc_data = {
            'selected_vertex': inputs['vertex_index'],
            'selected_hemi': inputs['hemisphere']
        }
    
    data_manager.update_location(loc_data)

    logger.info("Data update request successful")
    return make_response(
        timepoint_data, 200
    )

        
@viewer_bp.route('/get_functional_timecourse', methods=['POST'])
def get_functional_timecourse():
    fmri_file_type = data_manager.get_file_type()
    inputs = request.form
    if fmri_file_type == 'nifti':
        inputs = NiftiTimecourseInputs(**request.form)
    else:
        inputs = GiftiTimecourseInputs(**request.form)
    try:
        viewer_data = data_manager.get_viewer_data(
            fmri_data=True,
            use_preprocess=inputs['use_preprocess'],
            time_course_data=False,
            task_data=False,
        )
        if fmri_file_type == 'nifti':
            timecourse_data, voxel_label = get_timecourse_nifti(
                func_img=viewer_data['func_img'],
                x=inputs['x'],
                y=inputs['y'],
                z=inputs['z']
            )
        else:
            timecourse_data, voxel_label = get_timecourse_gifti(
                func_left_img=viewer_data['func_left_img'],
                func_right_img=viewer_data['func_right_img'],
                vertex_index=inputs['vertex_index'],
                hemisphere=inputs['hemisphere']
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
