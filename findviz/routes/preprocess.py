"""
Routes for preprocessing of FMRI and timecourse data
"""

from typing import Literal, TypedDict

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.routes.shared import data_manager
from findviz.routes.utils import Routes
from findviz.viz.preprocess.fmri import preprocess_fmri
from findviz.viz.preprocess.timecourse import preprocess_timecourse
from findviz.viz.exception import DataRequestError

# Set up a logger for the app
logger = setup_logger(__name__)

preprocess_bp = Blueprint('preprocess', __name__)


# Input types for preprocess_fmri route
class PreprocessFMRIInputs(TypedDict):
    mean_center: bool
    z_score: bool
    filter: bool
    smooth: bool
    tr: float
    low_cut: float
    high_cut: float
    fwhm: float


# Input types for preprocess_timecourse route
class PreprocessTimecourseInputs(TypedDict):
    ts_label: str
    mean_center: bool
    z_score: bool
    filter: bool
    smooth: bool
    tr: float
    low_cut: float
    high_cut: float


@preprocess_bp.route(Routes.GET_PREPROCESSED_FMRI.value, methods=['POST'])
def get_preprocessed_fmri():
    """
    Get preprocessed FMRI data
    """
    # Get file type
    fmri_file_type = data_manager.get_file_type()

    # If fmri data is already preprocessed, clear it
    if data_manager.fmri_preprocessed:
        logger.info("FMRI data already preprocessed, clearing it")
        data_manager.clear_fmri_preprocessed()

    # Get inputs
    inputs = PreprocessFMRIInputs(**request.form)
    logger.info(f"Preprocessing FMRI data with inputs: {inputs}")

    # Get viewer data
    viewer_data = data_manager.get_viewer_data(
            fmri_data=True,
            use_preprocess=False,
            time_course_data=False,
            task_data=False,
        )
    
    try:
        # Preprocess fmri data
        func_proc = preprocess_fmri(
            file_type=fmri_file_type,
            inputs=inputs,
            func_img=viewer_data['func_img'],
            mask_img=viewer_data['mask_img'],
            left_img=viewer_data['left_img'],
            right_img=viewer_data['right_img']
        )
        logger.info(f"Preprocessing of fmri data successful")

        # store preprocessed data
        if fmri_file_type == 'nifti':
            data_manager.store_fmri_preprocessed({'func_img': func_proc})
        else:
            data_manager.store_fmri_preprocessed(
                {'left_func_img': func_proc[0], 'right_func_img': func_proc[1]}
            )
            
    except KeyError as e:
        data_error = DataRequestError(
            message='Error in preprocess fmri request',
            fmri_file_type=fmri_file_type,
            route=Routes.GET_PREPROCESSED_FMRI,
            input_field=e.args[0]   
        )
        logger.error(data_error)
        return make_response(data_error.message, 400)
    except Exception as e:
        logger.critical(f"Error in preprocess_fmri route: {e}")
        return make_response(
            "Unknown error in preprocess fmri request", 500
        )


@preprocess_bp.route(Routes.GET_PREPROCESSED_TIMECOURSE.value, methods=['POST'])
def get_preprocessed_timecourse():
    """
    Get preprocessed timecourse data
    """
    # If timecourse data is already preprocessed, clear it
    if data_manager.ts_preprocessed:
        logger.info("Timecourse data already preprocessed, clearing it")
        data_manager.clear_timecourse_preprocessed()

    # Get inputs
    inputs = PreprocessTimecourseInputs(**request.form)
    logger.info(f"Preprocessing timecourse data with inputs: {inputs}")
    # Get viewer data
    viewer_data = data_manager.get_viewer_data(
            fmri_data=False,
            use_preprocess=False,
            time_course_data=True,
            task_data=False,
        )
    
    try:
        ts_proc = preprocess_timecourse(
            inputs=inputs,
            viewer_data=viewer_data['ts_data'][inputs['ts_label']]
        )
        logger.info(f"Preprocessing of timecourse data successful")
        # store preprocessed data
        data_manager.store_timecourse_preprocessed(
            {inputs['ts_label']: ts_proc}
        )
    except KeyError as e:
        data_error = DataRequestError(
            message='Error in preprocess timecourse request',
            route=Routes.GET_PREPROCESSED_TIMECOURSE,
            input_field=e.args[0]   
        )
        logger.error(data_error)
        return make_response(data_error.message, 400)
    except Exception as e:
        logger.critical(f"Error in preprocess_timecourse route: {e}")
        return make_response("Unknown error in preprocess timecourse request", 500)
