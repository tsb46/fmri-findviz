"""
Routes for preprocessing of FMRI and timecourse data

Routes:
    GET_PREPROCESSED_FMRI: Get preprocessed FMRI data
    GET_PREPROCESSED_TIMECOURSE: Get preprocessed timecourse data
    RESET_FMRI_PREPROCESS: Reset fmri preprocessing
    RESET_TIMECOURSE_PREPROCESS: Reset timecourse preprocessing
"""

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.routes.shared import data_manager
from findviz.routes.utils import Routes, handle_route_errors
from findviz.viz.preprocess.fmri import preprocess_fmri, PreprocessFMRIInputs
from findviz.viz.preprocess.timecourse import preprocess_timecourse, PreprocessTimecourseInputs
from findviz.viz.preprocess.input import (
    FMRIPreprocessInputValidator, 
    TimecoursePreprocessInputValidator
)
from findviz.viz.exception import PreprocessInputError, NiftiMaskError

logger = setup_logger(__name__)
preprocess_bp = Blueprint('preprocess', __name__)

@preprocess_bp.route(Routes.GET_PREPROCESSED_FMRI.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in preprocess FMRI request',
    log_msg='FMRI preprocessing successful',
    fmri_file_type=data_manager.get_file_type(),
    route=Routes.GET_PREPROCESSED_FMRI
)
def get_preprocessed_fmri() -> str:
    """Get preprocessed FMRI data"""
    if data_manager.fmri_preprocessed:
        logger.info("FMRI data already preprocessed, clearing it")
        data_manager.clear_fmri_preprocessed()

    inputs = PreprocessFMRIInputs(**request.form)
    logger.info(f"Preprocessing FMRI data with inputs: {inputs}")

    # Validate inputs
    try:
        fmri_input_validator = FMRIPreprocessInputValidator(data_manager.get_file_type())
        fmri_input_validator.validate_preprocess_input(inputs)
    except PreprocessInputError as e:
        logger.error(e)
        return make_response(e.message, 400)

    viewer_data = data_manager.get_viewer_data(
        fmri_data=True,
        use_preprocess=False,
        time_course_data=False,
        task_data=False,
    )
    try:
        func_proc = preprocess_fmri(
            file_type=data_manager.get_file_type(),
            inputs=inputs,
            func_data=viewer_data['func_data'],
            mask_data=viewer_data['mask_data'],
        )
    except NiftiMaskError as e:
        logger.error(e)
        return make_response(e.message, 400)

    if data_manager.get_file_type() == 'nifti':
        data_manager.store_fmri_preprocessed({'func_img': func_proc})
    else:
        data_manager.store_fmri_preprocessed({
            'left_func_img': func_proc[0], 
            'right_func_img': func_proc[1]
        })
    
    return "FMRI preprocessing successful"

@preprocess_bp.route(Routes.GET_PREPROCESSED_TIMECOURSE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in preprocess timecourse request',
    log_msg='Timecourse preprocessing successful',
    route=Routes.GET_PREPROCESSED_TIMECOURSE
)
def get_preprocessed_timecourse() -> str:
    """Get preprocessed timecourse data"""
    if data_manager.ts_preprocessed:
        logger.info("Timecourse data already preprocessed, clearing it")
        data_manager.clear_timecourse_preprocessed()

    inputs = PreprocessTimecourseInputs(**request.form)
    logger.info(f"Preprocessing timecourse data with inputs: {inputs}")

    # Validate inputs
    try:
        timecourse_input_validator = TimecoursePreprocessInputValidator()
        timecourse_input_validator.validate_preprocess_input(inputs)
    except PreprocessInputError as e:
        logger.error(e)
        return make_response(e.message, 400)

    viewer_data = data_manager.get_viewer_data(
        fmri_data=False,
        use_preprocess=False,
        time_course_data=True,
        task_data=False,
    )

    ts_data = {}
    for ts_label in inputs['ts_labels']:
        ts_proc = preprocess_timecourse(
            inputs=inputs,
            viewer_data=viewer_data['ts_data'][ts_label]
        )
        ts_data[ts_label] = ts_proc

    data_manager.store_timecourse_preprocessed(ts_data)
    return "Timecourse preprocessing successful"

@preprocess_bp.route(Routes.RESET_FMRI_PREPROCESS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in reset FMRI preprocessing request',
    log_msg='FMRI preprocessing reset successful'
)
def reset_fmri_preprocess() -> str:
    """Reset FMRI preprocessing"""
    data_manager.clear_fmri_preprocessed()
    return "FMRI preprocessing reset"

@preprocess_bp.route(Routes.RESET_TIMECOURSE_PREPROCESS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in reset timecourse preprocessing request',
    log_msg='Timecourse preprocessing reset successful'
)
def reset_timecourse_preprocess() -> str:
    """Reset timecourse preprocessing"""
    data_manager.clear_timecourse_preprocessed()
    return "Timecourse preprocessing reset"
