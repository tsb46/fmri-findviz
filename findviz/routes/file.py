"""
Routes for file upload and validation
"""

from flask import Blueprint, request, make_response, jsonify

from findviz.routes.utils import convert_value
from findviz.viz import exception
from findviz.viz.io.cache import Cache
from findviz.viz.io.timecourse import get_ts_header
from findviz.viz.io.upload import FileUpload

# create blueprint
file_bp = Blueprint('file', __name__)


@file_bp.route('/check_cache', methods=['GET'])
def check_cache():
    """Check if cache exists and return cached data if it does"""
    cache = Cache()
    
    if cache.exists():
        try:
            cached_data = cache.load()
            # Determine plot type from cached data
            plot_type = 'nifti' if 'nii_func' in cached_data else 'gifti'
            
            return jsonify({
                'has_cache': True,
                'cache_data': cached_data,
                'plot_type': plot_type
            })
        except Exception as e:
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
    except (
        exception.FileInputError,
        exception.FileUploadError,
        exception.FileValidationError
    ) as e:
        return make_response({
            "error": e.message,
            "file_type": e.file_type,
            "fields": e.field,
            "index": e.index
        }, 400)

    return make_response({
            "header": header.item()
        }, 201)

# Upload nifti file
@file_bp.route('/upload', methods=['POST'])
def upload():
    # get form parameters
    fmri_file_type = request.form.get('fmri_file_type')
    timecourse_input = convert_value(request.form.get('ts_input'))
    task_input = convert_value(request.form.get('task_input'))
    # initialiize FileUpload class
    file_upload = FileUpload(
        fmri_file_type, 
        ts_status=timecourse_input, 
        task_status=task_input,
        method='browser'
    )
    # get file uploads
    try:
        uploads = file_upload.upload()
    except (
        exception.FileInputError,
        exception.FileUploadError,
        exception.FileValidationError
    ) as e:
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








