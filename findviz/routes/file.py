"""
Routes for file upload and validation
"""
from findviz.logger_config import setup_logger
from flask import Blueprint, request, make_response, jsonify
from findviz.routes.shared import data_manager
from findviz.routes.utils import convert_value
from findviz.viz import exception
from findviz.viz.io.cache import Cache
from findviz.viz.io.timecourse import get_ts_header
from findviz.viz.io.upload import FileUpload

# Get logger instance for this module
logger = setup_logger(__name__)

# create blueprint
file_bp = Blueprint('file', __name__)


@file_bp.route('/check_cache', methods=['GET'])
def check_cache():
    """Check if cache exists and return cached data if it does"""
    logger.info("Checking cache status")
    cache = Cache()
    
    if cache.exists():
        try:
            cached_data = cache.load()
            # Determine plot type from cached data
            plot_type = 'nifti' if 'nii_func' in cached_data else 'gifti'
            logger.info("Cache found and loaded successfully")
            return jsonify({
                'has_cache': True,
                'cache_data': cached_data,
                'plot_type': plot_type
            })
        except Exception as e:
            logger.error("Error loading cached data: %s", str(e), exc_info=True)
            return jsonify({
                'has_cache': False,
                'error': str(e)
            })
    
    return jsonify({'has_cache': False})


# Get header of time course file
@file_bp.route('/get_header', methods=['POST'])
def get_header():
    # get time course file and its index
    ts_file = request.files.get('ts_file')
    ts_index = convert_value(request.form.get('file_index'))
    try:
        header = get_ts_header(ts_file, ts_index)
        logger.info("Successfully extracted header from file: %s", ts_file.filename)
    except (
        exception.FileInputError,
        exception.FileUploadError,
        exception.FileValidationError
    ) as e:
        logger.error("Error reading time series file header: %s", 
                        str(e), exc_info=True)
        return make_response({
            "error": e.message,
            "file_type": e.file_type,
            "fields": e.field,
            "index": e.index
        }, 400)
    except Exception as e:
        logger.critical("Unexpected error reading time series file header: %s", 
                        str(e), exc_info=True)
        return make_response({
            "error": "An unexpected error occurred while reading the time series file header",
            "file_type": None,
            "fields": None,
            "index": None
        }, 500)

    return make_response({
            "header": header.item()
        }, 201)

# Upload file input
@file_bp.route('/upload', methods=['POST'])
def upload():
    logger.info("Starting file upload process")
    # get form parameters
    fmri_file_type = request.form.get('fmri_file_type')
    timecourse_input = convert_value(request.form.get('ts_input'))
    task_input = convert_value(request.form.get('task_input'))

    logger.debug("Upload parameters - fMRI type: %s, Timecourse: %s, Task: %s", 
                    fmri_file_type, timecourse_input, task_input)
    
    # initialiize FileUpload class
    file_upload = FileUpload(
        fmri_file_type, 
        ts_status=timecourse_input, 
        task_status=task_input,
        method='browser'
    )
    logger.info("FileUpload instance initialized")

    # get file uploads
    try:
        uploads = file_upload.upload()
        logger.info("Files successfully uploaded and validated")
    except (
        exception.FileInputError,
        exception.FileUploadError,
        exception.FileValidationError
    ) as e:
        logger.error("File upload error: %s", str(e), exc_info=True)
        # if error in time course upload, pass index of failed time course file
        if e.file_type == exception.ExceptionFileTypes.TIMECOURSE.value:
            index = e.index
        else:
            index = None

        return make_response({
            "error": e.message,
            "file_type": e.file_type,
            "fields": e.field,
            "index": index
        }, 400)
    except Exception as e:
        logger.critical("Unexpected error during file upload: %s", str(e), exc_info=True)
        return make_response({
            "error": "An unexpected error occurred during file upload",
            "file_type": None,
            "fields": None,
            "index": None
        }, 500)

    # pass fmri data to data manager and get viewer data
    if fmri_file_type == 'nifti':
        data_manager.create_nifti_state(
            func_img = uploads['nifti'][file_upload.Nifti.FUNC.value],
            anat_img = uploads['nifti'][file_upload.Nifti.ANAT.value],
            mask_img = uploads['nifti'][file_upload.Nifti.MASK.value]
        )
        logger.info("Nifti data manager state created successfully")
    else:
        data_manager.create_gifti_state(
            left_func=uploads['gifti'][file_upload.Gifti.LEFT_FUNC.value],
            right_func=uploads['gifti'][file_upload.Gifti.RIGHT_FUNC.value],
            left_mesh=uploads['gifti'][file_upload.Gifti.LEFT_MESH.value],
            right_mesh=uploads['gifti'][file_upload.Gifti.RIGHT_MESH.value]
        )
        logger.info("Gifti data manager state created successfully")
    # initialize data manager with or without time series data
    data_manager.add_timeseries(uploads['ts'])
    if file_upload['ts'] is not None:
        logger.info("Time series data added to viewer data")
    else:
        logger.info("No time series data added to viewer data")

    # if task data, add to viewer data
    if file_upload.task_status:
        data_manager.add_task_design(
            task_data=uploads['task']['task_regressor'], 
            tr=uploads['task']['tr'], 
            slicetime_ref=uploads['task']['slicetime_ref']
        )
        logger.info("Task design data added to viewer data")
    else:
        logger.info("No task design data added to viewer data")

    # get viewer metadata
    viewer_metadata = data_manager.get_viewer_metadata()
    logger.info("Viewer metadata retrieved successfully")

    return make_response(
        viewer_metadata,
        201
    )

