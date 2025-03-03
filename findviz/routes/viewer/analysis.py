"""
Analysis routes for findviz viewer
"""
import json

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.viz import transforms
from findviz.routes.shared import data_manager
from findviz.routes.utils import convert_value, handle_route_errors, Routes
from findviz.viz.analysis.correlate import Correlate
from findviz.viz.analysis.distance import Distance
from findviz.viz.analysis.peak_finder import PeakFinder
from findviz.viz.analysis.average import WindowAverage
from findviz.viz.exception import (
    ParameterInputError, 
    PeakFinderNoPeaksFoundError,
    NiftiMaskError
)

analysis_bp = Blueprint('analysis', __name__)
logger = setup_logger(__name__)


@analysis_bp.route(Routes.CORRELATE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error correlating',
    log_msg='Correlation found successfully',
    route=Routes.CORRELATE,
    fmri_file_type=data_manager.fmri_file_type,
    route_parameters=['label', 'time_course_type', 'negative_lag', 'positive_lag'],
    custom_exceptions=[ParameterInputError]
)
def correlate():
    logger.info('Correlating time course with fMRI data')
    # get label from request
    label = request.json['label']
    # get time course type (timecourse or task) from request
    time_course_type = request.json['time_course_type']
    # get correlate parameters from request
    correlate_params = request.json
    # get time course, task and fmri data from data manager
    viewer_data = data_manager.get_viewer_data(
        fmri_data=True,
        time_course_data=True,
        task_data=True,
        label=label
    )
    if time_course_type == 'timecourse':
        time_course = viewer_data['ts'][label]
    elif time_course_type == 'task':
        time_course = viewer_data['task'][label]
    # get fmri file type
    fmri_file_type = data_manager.fmri_file_type
    # convert fmri data to array
    if fmri_file_type == 'nifti':
        # if mask is not provided, log error and return 400 error
        if viewer_data['mask_img'] is None:
            e = NiftiMaskError(
                message="A brain mask is required for nifti preprocessing",
            )
            logger.error(e)
            return make_response(e.message, 400)
        # convert fmri data to array
        fmri_data = transforms.nifti_to_array_masked(
            viewer_data['fmri'],
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        fmri_data, split_indx = transforms.gifti_to_array(viewer_data['fmri'])
    # initialize correlate class
    correlate = Correlate(
        negative_lag=correlate_params['negative_lag'],
        positive_lag=correlate_params['positive_lag'],
        time_length=fmri_data.shape[0]
    )
    # correlate time course with fmri data
    correlation_map = correlate.correlate(fmri_data, time_course)
    return {'status': 'success'}


@analysis_bp.route(Routes.DISTANCE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error calculating distance',
    log_msg='Distance calculated successfully',
    route=Routes.DISTANCE,
    fmri_file_type=data_manager.fmri_file_type,
    route_parameters=['distance_metric'],
    custom_exceptions=[ParameterInputError, NiftiMaskError]
)
def distance():
    logger.info('Calculating distance')
    # get distance metric from request
    distance_metric = request.form['distance_metric']
    # get fmri datafrom data manager
    viewer_data = data_manager.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
    )
    # get fmri file type
    fmri_file_type = data_manager.fmri_file_type
    # convert fmri data to array
    if fmri_file_type == 'nifti':
        # if mask is not provided, raise error
        if viewer_data['mask_img'] is None:
            raise NiftiMaskError(
                message="A brain mask is required for time point distance calculation",
            )        
        # convert fmri data to array
        fmri_data = transforms.nifti_to_array_masked(
            viewer_data['func_img'],
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        fmri_data, split_indx = transforms.gifti_to_array(
            viewer_data['left_func_img'],
            viewer_data['right_func_img']
        )
    # create distance class
    distance = Distance(
        distance_metric=distance_metric
    )
    # calculate distance from current time point and fmri data
    distance_map = distance.calculate_distance(data_manager.timepoint, fmri_data)
    # create distance plot state in data manager
    data_manager.create_distance_plot_state(distance_map)
    return {'status': 'success'}



@analysis_bp.route(Routes.FIND_PEAKS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error finding peaks',
    log_msg='Peaks found successfully',
    route=Routes.FIND_PEAKS,
    fmri_file_type=data_manager.fmri_file_type,
    route_parameters=[
        'label', 
        'time_course_type', 
        'peak_finder_params'
    ],
    custom_exceptions=[PeakFinderNoPeaksFoundError]
)
def find_peaks():
    logger.info('Finding peaks')
    # get label from request
    label = request.form['label']
    # get time course type (timecourse or task) from request
    time_course_type = request.form['time_course_type']
    # get peak finder parameters from request
    peak_finder_params = json.loads(request.form['peak_finder_params'])
    # convert peak finder parameters
    peak_finder_params = { 
        key: convert_value(value) for key, value in peak_finder_params.items()
    }
    # get time course and task data from data manager
    viewer_data = data_manager.get_viewer_data(
        fmri_data=False,
        time_course_data=True,
        task_data=True
    )
    if time_course_type == 'timecourse':
        data = viewer_data['ts'][label]
    elif time_course_type == 'task':
        data = viewer_data['task'][label]
    # create peak finder
    peak_finder = PeakFinder(
        zscore=peak_finder_params['zscore'],
        peak_distance=peak_finder_params['peak_distance'],
        peak_height=peak_finder_params['peak_height'],
        peak_prominence=peak_finder_params['peak_prominence'],
        peak_width=peak_finder_params['peak_width'],
        peak_threshold=peak_finder_params['peak_threshold']
    )
    # find peaks
    peaks = peak_finder.find_peaks(data)
    # convert peaks to list
    peaks = peaks.tolist()
    logger.info(f'Peaks found: {peaks}')
    # update annotation markers in data manager
    data_manager.add_annotation_markers(peaks)

    return {'status': 'success'}


@analysis_bp.route(Routes.WINDOWED_AVERAGE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error averaging',
    log_msg='Averaging found successfully',
    route=Routes.WINDOWED_AVERAGE,
    fmri_file_type=data_manager.fmri_file_type,
    route_parameters=['window_average_params'],
    custom_exceptions=[ParameterInputError, NiftiMaskError]
)
def windowed_average():
    logger.info('Window averaging')
    # get window average parameters from request
    window_average_params = json.loads(request.form['window_average_params'])
    window_average_params = {
        key: convert_value(value) for key, value in window_average_params.items()
    }
    # get fmri data from data manager
    viewer_data = data_manager.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False
    )
    # get fmri file type
    fmri_file_type = data_manager.fmri_file_type
    # convert fmri data to array
    if fmri_file_type == 'nifti':
        # if mask is not provided, log error and return 400 error
        if viewer_data['mask_img'] is None:
            raise NiftiMaskError(
                message="A brain mask is required for nifti preprocessing",
            )
        # convert fmri data to array
        fmri_data = transforms.nifti_to_array_masked(
            viewer_data['func_img'],
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        fmri_data, split_indx = transforms.gifti_to_array(
            viewer_data['left_func_img'],
            viewer_data['right_func_img']
        )
    # get annotation markers from data manager
    annotation_markers = data_manager.annotation_markers
    # create window average
    try:
        window_average = WindowAverage(
            left_edge=window_average_params['left_edge'],
            right_edge=window_average_params['right_edge'],
            n_timepoints=data_manager.n_timepoints
        )
    except ParameterInputError as e:
        raise e
    
    # create window average
    window_average_data = window_average.average(fmri_data, annotation_markers)

    # convert window average data to image
    if fmri_file_type == 'nifti':
        window_average_img = transforms.array_to_nifti_masked(
            window_average_data,
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        window_average_img = transforms.array_to_gifti(
            window_average_data,
            both_hemispheres=data_manager._state.both_hemispheres,
            split_index=split_indx
        )
    # create window average plot state in data manager
    data_manager.create_window_average_plot_state(window_average_img)
    
    return {'status': 'success'}


