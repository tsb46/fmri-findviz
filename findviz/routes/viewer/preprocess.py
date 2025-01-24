"""
Routes for preprocessing of FMRI and timecourse data

Routes:
    GET_PREPROCESSED_FMRI: Get preprocessed FMRI data
    GET_PREPROCESSED_TIMECOURSE: Get preprocessed timecourse data
    POST_RESET_FMRI_PREPROCESS: Reset fmri preprocessing
    POST_RESET_TIMECOURSE_PREPROCESS: Reset timecourse preprocessing
"""

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.routes.shared import data_manager
from findviz.routes.utils import Routes
from findviz.viz.preprocess.fmri import preprocess_fmri, PreprocessFMRIInputs
from findviz.viz.preprocess.timecourse import preprocess_timecourse, PreprocessTimecourseInputs
from findviz.viz.preprocess.input import (
    FMRIPreprocessInputValidator, 
    TimecoursePreprocessInputValidator
)
from findviz.viz.exception import DataRequestError, PreprocessInputError

# Set up a logger for the app
logger = setup_logger(__name__)

preprocess_bp = Blueprint('preprocess', __name__)


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

    # validate inputs
    fmri_input_validator = FMRIPreprocessInputValidator(fmri_file_type)
    try:
        fmri_input_validator.validate_preprocess_input(inputs)
    except PreprocessInputError as e:
        logger.error(e)
        return make_response(e.message, 400)
    except Exception as e:
        logger.critical(f"Error in input validation for preprocess fmri route: {e}")
        return make_response(
            "Unknown error in input validation for preprocess fmri request", 
            500
        )
    logger.info('Validation of fmri preprocessing parameters successful')

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
            func_data=viewer_data['func_data'],
            mask_data=viewer_data['mask_data'],
        )
        logger.info(f"Preprocessing of fmri data successful")

        # store preprocessed data
        if fmri_file_type == 'nifti':
            data_manager.store_fmri_preprocessed({'func_img': func_proc})
        else:
            data_manager.store_fmri_preprocessed(
                {'left_func_img': func_proc[0], 'right_func_img': func_proc[1]}
            )
        return make_response("FMRI preprocessing successful", 200)
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
    # validate inputs
    timecourse_input_validator = TimecoursePreprocessInputValidator()
    try:
        timecourse_input_validator.validate_preprocess_input(inputs)
    except PreprocessInputError as e:
        logger.error(e)
        return make_response(e.message, 400)
    except Exception as e:
        logger.critical(f"Error in input validation for preprocess timecourse route: {e}")
        return make_response(
            "Unknown error in input validation for preprocess timecourse request", 
            500
        )
    logger.info('Validation of timecourse preprocessing parameters successful')
    # Get viewer data
    viewer_data = data_manager.get_viewer_data(
            fmri_data=False,
            use_preprocess=False,
            time_course_data=True,
            task_data=False,
        )
    # Preprocess timecourse data    
    try:
        ts_data = {}
        for ts_label in inputs['ts_labels']:
            ts_proc = preprocess_timecourse(
                inputs=inputs,
                viewer_data=viewer_data['ts_data'][ts_label]
            )
            ts_data[ts_label] = ts_proc
        logger.info(f"Preprocessing of timecourse data successful")
        # store preprocessed data
        data_manager.store_timecourse_preprocessed(ts_data)
        return make_response("Timecourse preprocessing successful", 200)
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


@preprocess_bp.route(Routes.RESET_FMRI_PREPROCESS.value, methods=['POST'])
def reset_fmri_preprocess():
    """
    Reset fmri preprocessing
    """
    data_manager.clear_fmri_preprocessed()
    logger.info("FMRI preprocessing reset")
    return make_response("FMRI preprocessing reset", 200)


@preprocess_bp.route(Routes.RESET_TIMECOURSE_PREPROCESS.value, methods=['POST'])
def reset_timecourse_preprocess():
    """
    Reset timecourse preprocessing
    """
    data_manager.clear_timecourse_preprocessed()
    logger.info("Timecourse preprocessing reset")
    return make_response("Timecourse preprocessing reset", 200)
