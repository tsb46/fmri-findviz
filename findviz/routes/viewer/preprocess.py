"""
Routes for preprocessing of FMRI and timecourse data

Routes:
    GET_PREPROCESSED_FMRI: Get preprocessed FMRI data
    GET_PREPROCESSED_TIMECOURSE: Get preprocessed timecourse data
    RESET_FMRI_PREPROCESS: Reset fmri preprocessing
    RESET_TIMECOURSE_PREPROCESS: Reset timecourse preprocessing
"""
import json

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.routes.shared import data_manager
from findviz.routes.utils import convert_value, Routes, handle_route_errors
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
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_PREPROCESSED_FMRI,
    route_parameters=list(PreprocessFMRIInputs.__annotations__.keys()),
    custom_exceptions=[NiftiMaskError, PreprocessInputError]
)
def get_preprocessed_fmri() -> dict:
    """Get preprocessed FMRI data"""
    if data_manager.ctx.fmri_preprocessed:
        logger.info("FMRI data already preprocessed, clearing it")
        data_manager.ctx.clear_fmri_preprocessed()

    params = {key: convert_value(value) for key, value in request.form.items()}
    inputs = PreprocessFMRIInputs(**params)
    logger.info(f"Preprocessing FMRI data with inputs: {inputs}")

    # Validate inputs
    fmri_input_validator = FMRIPreprocessInputValidator(data_manager.ctx.fmri_file_type)
    fmri_input_validator.validate_preprocess_input(inputs)

    # get fmri data
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
    )

    # preprocess fmri data
    if data_manager.ctx.fmri_file_type == 'nifti':
        func_proc = preprocess_fmri(
            file_type=data_manager.ctx.fmri_file_type,
            inputs=inputs,
            func_img=viewer_data['func_img'],
            mask_img=viewer_data['mask_img'],
        )
        data_manager.ctx.store_fmri_preprocessed({'func_img': func_proc})
    else:
        func_proc = preprocess_fmri(
            file_type=data_manager.ctx.fmri_file_type,
            inputs=inputs,
            left_func_img=viewer_data['left_func_img'],
            right_func_img=viewer_data['right_func_img'],
        )
        data_manager.ctx.store_fmri_preprocessed({
            'left_func_img': func_proc[0], 
            'right_func_img': func_proc[1]
        })
    
    logger.info(f"Preprocessed FMRI data successfully")
    
    return {'status': 'success'}


@preprocess_bp.route(Routes.GET_PREPROCESSED_TIMECOURSE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in preprocess timecourse request',
    log_msg='Timecourse preprocessing successful',
    route=Routes.GET_PREPROCESSED_TIMECOURSE,
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route_parameters=list(PreprocessTimecourseInputs.__annotations__.keys()),
    custom_exceptions=[PreprocessInputError]
)
def get_preprocessed_timecourse() -> dict:
    """Get preprocessed timecourse data"""
    ts_labels = json.loads(request.form['ts_labels'])
    params = {
        key: convert_value(value) for key, value in request.form.items()
        if key != 'ts_labels'
    }
    inputs = PreprocessTimecourseInputs(**params)
    logger.info(f"Preprocessing timecourse data with inputs: {inputs}")

    # Validate inputs
    timecourse_input_validator = TimecoursePreprocessInputValidator()
    timecourse_input_validator.validate_preprocess_input(
        inputs, ts_labels
    )

    # get timecourse data
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=False,
        time_course_data=True,
        task_data=False,
    )

    # preprocess timecourse data
    ts_data = {}
    for ts_label in ts_labels:
        ts_proc = preprocess_timecourse(
            timecourse_data=viewer_data['ts'][ts_label],
            inputs=inputs
        )
        ts_data[ts_label] = ts_proc

    # store preprocessed timecourse data
    data_manager.ctx.store_timecourse_preprocessed(ts_data)
    return {'status': 'success'}


@preprocess_bp.route(Routes.RESET_FMRI_PREPROCESS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in reset FMRI preprocessing request',
    log_msg='FMRI preprocessing reset successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.RESET_FMRI_PREPROCESS
)
def reset_fmri_preprocess() -> dict:
    """Reset FMRI preprocessing"""
    data_manager.ctx.clear_fmri_preprocessed()
    return {'status': 'success'}


@preprocess_bp.route(Routes.RESET_TIMECOURSE_PREPROCESS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Unknown error in reset timecourse preprocessing request',
    log_msg='Timecourse preprocessing reset successful',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.RESET_TIMECOURSE_PREPROCESS,
    route_parameters=['ts_labels'],
    custom_exceptions=[PreprocessInputError]
)
def reset_timecourse_preprocess() -> dict:
    """Reset timecourse preprocessing"""
    ts_labels = json.loads(request.form['ts_labels'])
    # check if no timecourse labels provided
    if len(ts_labels) == 0:
        raise PreprocessInputError(
            'No timecourses selected', 
            preprocess_method='reset'
        )
    # check if time course label is in preprocessed data
    for ts_label in ts_labels:
        if ts_label not in data_manager.ctx.ts_labels_preprocessed:
            raise PreprocessInputError(
                f'Timecourse {ts_label} is not preprocessed',
                preprocess_method='reset'
            )
    # clear timecourse preprocessed data
    data_manager.ctx.clear_timecourse_preprocessed(ts_labels)
    return {'status': 'success'}
