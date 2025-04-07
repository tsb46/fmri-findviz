"""
Analysis routes for findviz viewer
"""
import json

from flask import Blueprint, request, make_response

from findviz.logger_config import setup_logger
from findviz.viz import transforms
from findviz.routes.shared import data_manager
from findviz.routes.utils import (
    convert_value, 
    handle_route_errors, 
    Routes
)
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
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route_parameters=['label', 'time_course_type', 'negative_lag', 'positive_lag'],
    custom_exceptions=[ParameterInputError, NiftiMaskError]
)
def correlate():
    logger.info('Correlating time course with fMRI data')
    # get label from request
    label = request.form['label']
    # get time course type (timecourse or task) from request
    time_course_type = request.form['time_course_type']
    # get correlate parameters from request
    correlate_params = {
        'negative_lag': convert_value(request.form['negative_lag']),
        'positive_lag': convert_value(request.form['positive_lag'])
    }
    # get time course, task and fmri data from data manager
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=True,
        time_course_data=True,
        task_data=True
    )
    if time_course_type == 'timecourse':
        time_course = viewer_data['ts'][label]
    elif time_course_type == 'task':
        time_course = viewer_data['task'][label]
    # get fmri file type
    fmri_file_type = data_manager.ctx.fmri_file_type
    # convert fmri data to array
    if fmri_file_type == 'nifti':
        # if mask is not provided, log error and return 400 error
        if viewer_data['mask_img'] is None:
            raise NiftiMaskError(
                message="A brain mask is required for nifti preprocessing",
            )
        # convert nifti data to array
        fmri_data = transforms.nifti_to_array_masked(
            viewer_data['func_img'],
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        # get surface meshes (for analysis viewer)
        viewer_metadata = data_manager.ctx.get_viewer_metadata()
        # convert gifti data to array
        fmri_data, split_indx = transforms.gifti_to_array(
            viewer_data['left_func_img'],
            viewer_data['right_func_img']
        )
    # initialize correlate class
    correlate = Correlate(
        negative_lag=correlate_params['negative_lag'],
        positive_lag=correlate_params['positive_lag'],
        time_length=fmri_data.shape[0]
    )
    # correlate time course with fmri data
    correlation_data = correlate.correlate(fmri_data, time_course)

     # convert window average data to image
    if fmri_file_type == 'nifti':
        correlation_img = transforms.array_to_nifti_masked(
            correlation_data,
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        correlation_img = transforms.array_to_gifti(
            correlation_data,
            both_hemispheres=data_manager.ctx.both_hemispheres,
            split_index=split_indx
        )
        if data_manager.ctx.both_hemispheres:
            left_gifti = correlation_img[0]
            right_gifti = correlation_img[1]
        else:
            if data_manager.ctx.left_surface_input:
                left_gifti = correlation_img
                right_gifti = None
            elif data_manager.ctx.right_surface_input:
                left_gifti = None
                right_gifti = correlation_img
        
    # create new context for correlation
    data_manager.create_analysis_context('correlate')
    # switch to new context
    data_manager.switch_context('correlate')
    # create state for correlation
    if fmri_file_type == 'nifti':
        data_manager.ctx.create_nifti_state(
            func_img=correlation_img,
            anat_img=viewer_data['anat_img'],
            mask_img=viewer_data['mask_img']
        )
    else:
        data_manager.ctx.create_gifti_state(
            left_func_img=left_gifti,
            right_func_img=right_gifti,
            faces_left=viewer_metadata['faces_left'],
            faces_right=viewer_metadata['faces_right'],
            vertices_left=viewer_metadata['vertices_left'],
            vertices_right=viewer_metadata['vertices_right']
        )
    # set timepoints for correlation
    data_manager.ctx.set_timepoints(correlate.lags.tolist())
    
    return {'status': 'success'}


@analysis_bp.route(Routes.DISTANCE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error calculating distance',
    log_msg='Distance calculated successfully',
    route=Routes.DISTANCE,
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route_parameters=['distance_metric'],
    custom_exceptions=[ParameterInputError, NiftiMaskError]
)
def distance():
    logger.info('Calculating distance')
    # get distance metric from request
    distance_metric = request.form['distance_metric']
    # get fmri datafrom data manager
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
    )
    # get fmri file type
    fmri_file_type = data_manager.ctx.fmri_file_type
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
    distance_map = distance.calculate_distance(
        data_manager.ctx.timepoint, fmri_data
    )
    # create distance plot state in data manager
    data_manager.ctx.create_distance_plot_state(distance_map)
    return {'status': 'success'}



@analysis_bp.route(Routes.FIND_PEAKS.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error finding peaks',
    log_msg='Peaks found successfully',
    route=Routes.FIND_PEAKS,
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
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
    viewer_data = data_manager.ctx.get_viewer_data(
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
    data_manager.ctx.add_annotation_markers(peaks)

    return {'status': 'success'}


@analysis_bp.route(Routes.WINDOWED_AVERAGE.value, methods=['POST'])
@handle_route_errors(
    error_msg='Error performing windowed average',
    log_msg='Windowed average performed successfully',
    route=Routes.WINDOWED_AVERAGE,
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
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
    viewer_data = data_manager.ctx.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False
    )
    # get fmri file type
    fmri_file_type = data_manager.ctx.fmri_file_type
    # convert fmri data to array
    if fmri_file_type == 'nifti':
        # if mask is not provided, log error and return 400 error
        if viewer_data['mask_img'] is None:
            raise NiftiMaskError(
                message="A brain mask is required for nifti preprocessing",
            )
        # convert nifti data to array
        fmri_data = transforms.nifti_to_array_masked(
            viewer_data['func_img'],
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        # get surface meshes (for analysis viewer)
        viewer_metadata = data_manager.ctx.get_viewer_metadata()
        # convert gifti data to array
        fmri_data, split_indx = transforms.gifti_to_array(
            viewer_data['left_func_img'],
            viewer_data['right_func_img']
        )
    # get annotation markers from data manager
    annotation_markers = data_manager.ctx.annotation_markers
    # create window average
    try:
        window_average = WindowAverage(
            left_edge=window_average_params['left_edge'],
            right_edge=window_average_params['right_edge'],
            n_timepoints=data_manager.ctx.n_timepoints
        )
    except ParameterInputError as e:
        raise e
    
    # create window average
    window_average_data = window_average.average(fmri_data, annotation_markers)

    # convert window average data to image
    if fmri_file_type == 'nifti':
        # convert window average data to nifti
        window_average_img = transforms.array_to_nifti_masked(
            window_average_data,
            viewer_data['mask_img']
        )
    elif fmri_file_type == 'gifti':
        # convert window average data to gifti
        window_average_img = transforms.array_to_gifti(
            window_average_data,
            both_hemispheres=data_manager.ctx.both_hemispheres,
            split_index=split_indx
        )
        if data_manager.ctx.both_hemispheres:
            left_gifti = window_average_img[0]
            right_gifti = window_average_img[1]
        else:
            if data_manager.ctx.left_surface_input:
                left_gifti = window_average_img
                right_gifti = None
            elif data_manager.ctx.right_surface_input:
                left_gifti = None
                right_gifti = window_average_img
        
    # create new context for window average
    data_manager.create_analysis_context('average')
    # switch to new context
    data_manager.switch_context('average')
    # create state for window average
    if fmri_file_type == 'nifti':
        data_manager.ctx.create_nifti_state(
            func_img=window_average_img,
            anat_img=viewer_data['anat_img'],
            mask_img=viewer_data['mask_img']
        )
    else:
        data_manager.ctx.create_gifti_state(
            left_func_img=left_gifti,
            right_func_img=right_gifti,
            faces_left=viewer_metadata['faces_left'],
            faces_right=viewer_metadata['faces_right'],
            vertices_left=viewer_metadata['vertices_left'],
            vertices_right=viewer_metadata['vertices_right']
        )
    # set timepoints for window average
    data_manager.ctx.set_timepoints(window_average.get_timepoints())

    return {'status': 'success'}


