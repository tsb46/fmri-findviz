"""
Analysis routes for findviz viewer
"""

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.viz import transforms
from findviz.routes.shared import data_manager
from findviz.routes.utils import handle_route_errors, Routes
from findviz.viz.analysis.correlate import Correlate
from findviz.viz.analysis.distance import Distance
from findviz.viz.analysis.peak_finder import PeakFinder
from findviz.viz.analysis.average import WindowAverage
from findviz.viz.exception import ParameterInputError, PeakFinderNoPeaksFoundError

analysis_bp = Blueprint('analysis', __name__)
logger = setup_logger(__name__)


@analysis_bp.route(Routes.CORRELATE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error correlating',
    log_msg='Correlation found successfully',
    route=Routes.CORRELATE
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
        fmri_data = transforms.nifti_to_array(viewer_data['fmri'])
    elif fmri_file_type == 'gifti':
        fmri_data, split_indx = transforms.gifti_to_array(viewer_data['fmri'])
    # create correlate
    try:
        correlate = Correlate(
            negative_lag=correlate_params['negative_lag'],
            positive_lag=correlate_params['positive_lag'],
            time_length=fmri_data.shape[0]
        )
    except ParameterInputError as e:
        logger.error(e)
        return make_response(e.message, 400)
    
    correlation_map = correlate.correlate(fmri_data, time_course)
    return {'status': 'success'}


@analysis_bp.route(Routes.DISTANCE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error calculating distance',
    log_msg='Distance calculated successfully',
    route=Routes.DISTANCE
)
def distance():
    logger.info('Calculating distance')
    # get distance parameters from request
    distance_params = request.json
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
        fmri_data = transforms.nifti_to_array(viewer_data['fmri'])
    elif fmri_file_type == 'gifti':
        fmri_data, split_indx = transforms.gifti_to_array(viewer_data['fmri'])
    # create distance class
    distance = Distance(
        distance_metric=distance_params['distance_metric']
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
    route=Routes.FIND_PEAKS
)
def find_peaks():
    logger.info('Finding peaks')
    # get label from request
    label = request.json['label']
    # get time course type (timecourse or task) from request
    time_course_type = request.json['time_course_type']
    # get peak finder parameters from request
    peak_finder_params = request.json
    # get time course and taskdata from data manager
    viewer_data = data_manager.get_viewer_data(
        fmri_data=False,
        time_course_data=True,
        task_data=True,
        label=label
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
    try:
        peaks = peak_finder.find_peaks(data)
    except PeakFinderNoPeaksFoundError as e:
        logger.error(e)
        return make_response(e.message, 400)
    # convert peaks to list
    peaks = peaks.tolist()
    logger.info(f'Peaks found: {peaks}')
    # update annotation markers in data manager
    data_manager.add_annotation_markers(peaks)

    return {'status': 'success'}


@analysis_bp.route(Routes.AVERAGE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error averaging',
    log_msg='Averaging found successfully',
    route=Routes.AVERAGE
)
def average():
    logger.info('Window averaging')
    # get label from request
    label = request.json['label']
    # get window average parameters from request
    window_average_params = request.json
    # get fmri data from data manager
    viewer_data = data_manager.get_viewer_data(
        fmri_data=True,
        time_course_data=True,
        task_data=True,
        label=label
    )
    # get fmri file type
    fmri_file_type = data_manager.fmri_file_type
    # convert fmri data to array
    if fmri_file_type == 'nifti':
        fmri_data = transforms.nifti_to_array(viewer_data['fmri'])
    elif fmri_file_type == 'gifti':
        fmri_data, split_indx = transforms.gifti_to_array(viewer_data['fmri'])
    # get annotation markers from data manager
    annotation_markers = data_manager.annotation_markers
    # create window average
    try:
        window_average = WindowAverage(
            left_edge=window_average_params['left_edge'],
            right_edge=window_average_params['right_edge'],
        )
    except ParameterInputError as e:
        logger.error(e)
        return make_response(e.message, 400)
    # create window average
    window_average_map = window_average.average(fmri_data, annotation_markers)
    
    return {'status': 'success'}


