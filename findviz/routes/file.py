"""
Routes for file upload and validation
"""
from findviz.logger_config import setup_logger
from flask import Blueprint, request, make_response, jsonify
from findviz.routes.shared import data_manager
from findviz.routes.utils import convert_value, Routes
from findviz.viz import exception
from findviz.viz.io.cache import Cache
from findviz.viz.io.nifti import NiftiFiles
from findviz.viz.io.gifti import GiftiFiles
from findviz.viz.io.timecourse import get_ts_header
from findviz.viz.io.upload import FileUpload

# Get logger instance for this module
logger = setup_logger(__name__)

# create blueprint
file_bp = Blueprint('file', __name__)


@file_bp.route(Routes.CHECK_CACHE.value, methods=['GET'])
def check_cache():
    """Check if cache exists and return cached data if it does"""
    logger.info("Checking cache status")
    cache = Cache()
    has_cache = cache.exists()
    logger.info(f"Cache check: exists={has_cache}, path={cache.get_cache_path()}")
    if has_cache:
        try:
            cached_data = cache.load()
            # Determine plot type from cached data
            logger.info("Cache found and loaded successfully")
            return jsonify({
                'has_cache': True,
                'cache_data': cached_data,
                'plot_type': cached_data['file_type']
            })
        except Exception as e:
            logger.error("Error loading cached data: %s", str(e), exc_info=True)
            return jsonify({
                'has_cache': False,
                'error': str(e)
            })
    
    return jsonify({'has_cache': False})


@file_bp.route(Routes.CLEAR_CACHE.value, methods=['POST'])
def clear_cache():
    """Clear the cache"""
    logger.info("Clearing cache")
    try:
        cache = Cache()
        cache.clear()
        return jsonify({'success': True})
    except Exception as e:
        logger.error("Error clearing cache: %s", str(e), exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

# Get header of time course file
@file_bp.route(Routes.GET_HEADER.value, methods=['POST'])
def get_header():
    # get time course file and its index
    ts_file = request.files.get('ts_file')
    ts_index = convert_value(request.form.get('file_index'))
    try:
        header = get_ts_header(ts_file, ts_index)
        logger.info("Successfully extracted header from file: %s", ts_file.filename)
    except (
        exception.FileInputError,
        exception.FileUploadError
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
            "header": header
        }, 201)

# Upload file input
@file_bp.route(Routes.UPLOAD_FILES.value, methods=['POST'])
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
    # Initialize state in the active context
    if fmri_file_type == 'nifti':
        data_manager.ctx.create_nifti_state(
            func_img = uploads['nifti'][NiftiFiles.FUNC.value],
            anat_img = uploads['nifti'][NiftiFiles.ANAT.value],
            mask_img = uploads['nifti'][NiftiFiles.MASK.value]
        )
        logger.info("Nifti data manager state created successfully")
    else:
        data_manager.ctx.create_gifti_state(
            left_func_img=uploads['gifti'][GiftiFiles.LEFT_FUNC.value],
            right_func_img=uploads['gifti'][GiftiFiles.RIGHT_FUNC.value],
            left_mesh=uploads['gifti'][GiftiFiles.LEFT_MESH.value],
            right_mesh=uploads['gifti'][GiftiFiles.RIGHT_MESH.value]
        )
        logger.info("Gifti data manager state created successfully")
    # initialize data manager with or without time series data
    data_manager.ctx.add_timeseries(uploads['ts'])
    if file_upload.ts_status:
        logger.info("Time series data added to viewer data")
    else:
        logger.info("No time series data added to viewer data")

    # if task data, add to viewer data
    if file_upload.task_status:
        data_manager.ctx.add_task_design(
            task_data=uploads['task']['task_regressors'], 
            tr=uploads['task']['tr'], 
            slicetime_ref=uploads['task']['slicetime_ref']
        )
        logger.info("Task design data added to viewer data")
    else:
        logger.info("No task design data added to viewer data")

    # get viewer metadata
    viewer_metadata = data_manager.ctx.get_viewer_metadata()
    logger.info("Viewer metadata retrieved successfully")
    
    return make_response(
        viewer_metadata,
        201
    )


@file_bp.route(Routes.UPLOAD_SCENE.value, methods=['POST'])
def upload_scene() -> dict:
    """Upload a scene file"""
    logger.info("Uploading scene file")
    # Check if a file was uploaded
    if 'scene_file' not in request.files:
        logger.error("No scene file provided")
        return make_response({"error": "No scene file provided"}, 400)
    
    scene_file = request.files['scene_file']
    
    # Check if file is empty
    if scene_file.filename == '':
        logger.error("Empty file provided")
        return make_response({"error": "Empty file provided"}, 400)
    
    # Validate file extension
    if not scene_file.filename.endswith('.fvstate'):
        logger.error("Invalid file format. Expected .fvstate file")
        return make_response({"error": "Invalid file format. Expected .fvstate file"}, 400)
    
    try:
        # Read the file data
        scene_file_data = scene_file.read()
        
        # Load the state
        data_manager.load(scene_file_data)
        
        # Get viewer metadata for the restored state
        viewer_metadata = data_manager.ctx.get_viewer_metadata()
        
        return make_response(viewer_metadata, 200)
    except exception.FVStateVersionIncompatibleError as e:
        logger.error(f"Error loading scene file: {str(e)}")
        return make_response(
            {"error": f"Failed to load scene: {str(e)}"}, 400)
    except Exception as e:
        logger.error(f"Error loading scene file: {str(e)}")
        return make_response({"error": f"Failed to load scene: {str(e)}"}, 500)
    

