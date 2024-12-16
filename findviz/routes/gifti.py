"""Routes for Gifti file handling and utilities"""
import json

import nibabel as nib
import numpy as np

from flask import Blueprint, request, jsonify
from nibabel.gifti import GiftiDataArray

from findviz import analysis
from findviz.routes import utils
from findviz.routes.common import cache
from findviz.routes.utils import package_gii_metadata

gifti_bp = Blueprint('gifti', __name__)  # Create a blueprint


# Route to handle file upload and return initial visualizations
@gifti_bp.route('/upload_gii', methods=['POST'])
def upload_files_gii():
    cache['file_type'] = 'gifti'
    # get form data
    left_file = request.files.get('left_hemisphere_file')
    right_file = request.files.get('right_hemisphere_file')
    left_mesh_file = request.files.get('left_hemisphere_mesh_file')
    right_mesh_file = request.files.get('right_hemisphere_mesh_file')

    left_key = None
    right_key = None
    vertices_left = None
    faces_left = None
    vertices_right = None
    faces_right = None
    timepoints = None

    if left_file:
        # load left hemisphere functional and store in cache
        left_bytes = left_file.read()
        try:
            left_img = nib.GiftiImage.from_bytes(left_bytes)
        except:
            error_msg = 'there was a problem loading the left hemisphere func.gii file. Check format.'
            return jsonify({'error': error_msg, 'file': 'left_mesh'}), 400
        # check format - each time point should be a 1-d array
        if len(np.squeeze(left_img.darrays[0].data).shape) > 1:
            error_msg = 'there was a problem loading the left hemisphere func.gii file. Expecting 1d-array per timepoint. Check format.'
            return jsonify({'error': error_msg, 'file': 'left'}), 400
        left_key = left_file.filename
        cache['left_key'] = left_key
        # store in cache
        cache[left_key] = left_img

        # load right hemisphere surface geometry
        left_mesh_bytes = left_mesh_file.read()
        try:
            fsmesh_left = nib.GiftiImage.from_bytes(left_mesh_bytes)
        except:
            error_msg = 'there was a problem loading the left hemisphere surf.gii file. Check format.'
            return jsonify({'error': error_msg, 'file': 'left_mesh'}), 400
        # check format - there should two arrays - coords and faces
        if len(fsmesh_left.darrays) != 2:
            error_msg = 'there was a problem loading the left hemisphere surf.gii file. Should only contain coordinates and faces arrays in geometry file. Check format.'
            return jsonify({'error': error_msg, 'file': 'left_mesh'}), 400
        # assumes first position is coordinates, and second is faces
        vertices_left = fsmesh_left.darrays[0].data
        faces_left = fsmesh_left.darrays[1].data
        cache['vertices_left'] = vertices_left
        cache['faces_left'] = faces_left

    else:
        left_img = None

    if right_file:
        # load right hemisphere functional and store in cache
        right_bytes = right_file.read()
        try:
            right_img = nib.GiftiImage.from_bytes(right_bytes)
        except:
            error_msg = 'there was a problem loading the right hemisphere func.gii file. Check format.'
            return jsonify({'error': error_msg, 'file': 'left_mesh'}), 400
        # check format - each time point should be a 1-d array
        if len(np.squeeze(right_img.darrays[0].data).shape) > 1:
            error_msg = 'there was a problem loading the right hemisphere func.gii file. Expecting 1d-array per timepoint. Check format.'
            return jsonify({'error': error_msg, 'file': 'right'}), 400
        right_key = right_file.filename
        cache['right_key'] = right_key
        # store in cache
        cache[right_key] = right_img

        # load right hemisphere surface geometry
        right_mesh_bytes = right_mesh_file.read()
        try:
            fsmesh_right = nib.GiftiImage.from_bytes(right_mesh_bytes)
        except:
            error_msg = 'there was a problem loading the right hemisphere surf.gii file. Check format.'
            return jsonify({'error': error_msg, 'file': 'left_mesh'}), 400
        # check format - there should two arrays - coords and faces
        if len(fsmesh_right.darrays) != 2:
            error_msg = 'there was a problem loading the right hemisphere surf.gii file. Check format.'
            return jsonify({'error': error_msg, 'file': 'right_mesh'}), 400
        # assumes first position is coordinates, and second is faces
        vertices_right = fsmesh_right.darrays[0].data
        faces_right = fsmesh_right.darrays[1].data
        cache['vertices_right'] = vertices_right
        cache['faces_right'] = faces_right
    else:
        right_img = None

    # check length of func.gii are the same for both hemispheres
    if (left_file is not None) & (right_file is not None):
        if len(right_img.darrays) != len(left_img.darrays):
            error_msg = 'the number of timepoints in the left and right func.gii are not the same'
            return jsonify({'error': error_msg, 'file': 'none'}), 400

    # get global min and max
    metadata = package_gii_metadata(left_img, right_img)
    # store global min and max in cache
    cache['global_min'] = metadata['global_min']
    cache['global_max'] = metadata['global_max']

    response_data = {
        'left_key': left_key,
        'right_key': right_key,
        'vertices_left': vertices_left.tolist() if vertices_left is not None else None,
        'faces_left': faces_left.tolist() if faces_left is not None else None,
        'vertices_right': vertices_right.tolist() if vertices_right is not None else None,
        'faces_right': faces_right.tolist() if faces_right is not None else None,
        'timepoints': metadata['timepoints'],
        'global_min': metadata['global_min'].item(),
        'global_max': metadata['global_max'].item()
    }
    return jsonify(response_data)


# Route to handle dynamic gifti brain plot generation based on time point
@gifti_bp.route('/get_brain_gii_plot', methods=['POST'])
def get_brain_gii_plot():
    left_key = request.form.get('left_key')
    right_key = request.form.get('right_key')
    time_point = int(request.form.get('time_point', 0))
    use_preprocess = utils.convert_value(
        request.form.get('use_preprocess')
    )

    func_data_left = None
    func_data_right = None

    # Handle left hemisphere GIFti file
    if left_key:
        # If preprocess state is true, return preprocessed data
        if use_preprocess:
            left_img = cache.get('preprocessed_left')
        else:
            left_img = cache.get(left_key)
        if not left_img:
            return jsonify({'error': 'File not found'}), 500
        else:
            func_data_left = left_img.darrays[time_point].data

    # Handle right hemisphere GIFti file
    if right_key:
        # If preprocess state is true, return preprocessed data
        if use_preprocess:
            right_img = cache.get('preprocessed_right')
        else:
            right_img = cache.get(right_key)
        if not right_img:
            return jsonify({'error': 'File not found'}), 500
        else:
            func_data_right = right_img.darrays[time_point].data

    # Return the appropriate data
    return jsonify({
        'intensity_left': func_data_left.tolist() if func_data_left is not None else None,
        'intensity_right': func_data_right.tolist() if func_data_right is not None else None
    })


# Route to fetch time course data for a selected vertex
@gifti_bp.route('/get_time_course_gii', methods=['GET'])
def get_time_course_gii():
    file_key = request.args.get('file_key')
    vertex_index = int(request.args.get('vertex_index'))
    hemi = request.args.get('hemisphere')
     # determine whether to use preprocessed data
    use_preprocess = utils.convert_value(
        request.args.get('use_preprocess')
    )
    # Get gifti img
    if use_preprocess:
        if hemi == 'left':
            gifti_img = cache.get('preprocessed_left')
        else:
            gifti_img = cache.get('preprocessed_right')
    else:
        gifti_img = cache.get(file_key)

    if not gifti_img:
        return jsonify({'error': 'File not found'}), 500

    # Extract the vertex's time course
    time_course = [d.data[vertex_index] for d in gifti_img.darrays]
    time_course = [t.item() for t in time_course]

    # create time course label
    time_course_label = f'Vertex: {vertex_index}'
    # store in cache
    if 'timeseries' in cache:
        cache['timeseries'][time_course_label] = time_course
    else:
        cache['timeseries'] = {
            time_course_label: time_course
        }

    return jsonify(
        {
            'time_course': time_course,
            'time_course_label': time_course_label
        }
    )


# route to normalize gifti time course
@gifti_bp.route('/preprocess_gii', methods=['GET'])
def preprocess_gii():
    # If reset, deleted preprocessed data and pass raw data
    reset = utils.convert_value(
        request.args.get('reset')
    )
    if reset:
        # ensure preprocessed file is in cache before deleting
        if 'preprocessed_left' in cache:
            del cache['preprocessed_left']
        if 'preprocessed_right' in cache:
            del cache['preprocessed_right']
        # Pass raw global min and max
        return jsonify({
            'global_min': cache['global_min'].item(),
            'global_max': cache['global_max'].item()
        })

    # get data passed from fetch
    left_key = utils.convert_value(
        request.args.get('left_key')
    )
    right_key = utils.convert_value(
        request.args.get('right_key')
    )
    norm_enabled = utils.convert_value(
        request.args.get('normalize_enabled')
    )
    filter_enabled = utils.convert_value(
        request.args.get('filter_enabled')
    )
    params = {
        'tr': request.args.get('TR'),
        'low_cut': request.args.get('lowCut'),
        'high_cut': request.args.get('highCut'),
        'mean_center': request.args.get('meanCenter'),
        'z_score': request.args.get('zScore'),
    }

    # convert params from response
    params = utils.convert_params(params)

    # get norm method
    if params['mean_center']:
        norm_method = 'mean_center'
    elif params['z_score']:
        norm_method = 'z_score'
    else:
        norm_method = None

    # preprocess left hemisphere gifti file
    if left_key:
        left_img = cache.get(left_key)
        if not left_img:
            return jsonify({'error': 'File not found'}), 500
        # convert to array
        left_img_array = gii_to_array(left_img)
        # If filtering specified
        if filter_enabled:
            left_img_array = utils.filter(
                left_img_array, params['low_cut'], params['high_cut'],
                params['tr']
            )
        # If normalization specified
        if norm_enabled:
            left_img_array = utils.normalize(
                left_img_array, norm_method, axis=0
            )
        # convert to gifti
        left_img = array_to_gii(left_img_array)
        # save to cache
        cache['preprocessed_left'] = left_img
    else:
        left_img = None


    # normalize right hemisphere Gifti file
    if right_key:
        right_img = cache.get(right_key)
        if not right_img:
            return jsonify({'error': 'File not found'}), 500
        # convert to array
        right_img_array = gii_to_array(right_img)
        # If filtering specified
        if filter_enabled:
            right_img_array = utils.filter(
                right_img_array, params['low_cut'], params['high_cut'],
                params['tr']
            )
        # If normalization specified
        if norm_enabled:
            right_img_array = utils.normalize(
                right_img_array, norm_method, axis=0
            )
        # convert to gifti
        right_img = array_to_gii(right_img_array)
        # save to cache
        cache['preprocessed_right'] = right_img

    else:
        right_img = None


    # get min and max for preprocessed data
    metadata = package_gii_metadata(left_img, right_img)

    # pass new global min and global max
    return jsonify({
        'global_min': metadata['global_min'].item(),
        'global_max': metadata['global_max'].item()
    })


# route to compute window average of nii data
@gifti_bp.route('/compute_distance_gii', methods=['POST'])
def compute_distance_gii():
    # load parameters
    time_point = utils.convert_value(request.form.get('time_point'))
    dist_metric = utils.convert_value(request.form.get('dist_metric'))
    left_key = utils.convert_value(
        request.form.get('left_key')
    )
    right_key = utils.convert_value(
        request.form.get('right_key')
    )
    use_preprocess = utils.convert_value(
        request.form.get('use_preprocess')
    )
    # left hemisphere
    if left_key:
        if use_preprocess:
            left_img = cache.get('preprocessed_left')
        else:
            left_img = cache.get(left_key)

        # convert to array
        left_img_array = gii_to_array(left_img)

    else:
        left_img_array = None

    # right hemisphere
    if right_key:
        if use_preprocess:
            right_img = cache.get('preprocessed_right')
        else:
            right_img = cache.get(right_key)

        # convert to array
        right_img_array = gii_to_array(right_img)

    else:
        right_img_array = None

    gifti_array, _ = concat_gii_hemi(
        left_img_array, right_img_array
    )

    # get time point distance
    dist_vec = analysis.distance(gifti_array, time_point, dist_metric)


    return jsonify({
        'time_point': time_point,
        'dist_vec': dist_vec.tolist()
    })


# route to compute window average of gii data
@gifti_bp.route('/compute_avg_gii', methods=['POST'])
def compute_avg_gii():
    # load markers
    markers = request.form.get('markers')
    markers = json.loads(markers)
    # load parameters
    left_key = utils.convert_value(
        request.form.get('left_key')
    )
    right_key = utils.convert_value(
        request.form.get('right_key')
    )
    l_edge = utils.convert_value(request.form.get('left_edge'))
    r_edge = utils.convert_value(request.form.get('right_edge'))
    use_preprocess = utils.convert_value(
        request.form.get('use_preprocess')
    )
    # Load mesh and face data
    faces_left = json.loads(request.form.get('faces_left'))
    faces_right = json.loads(request.form.get('faces_right'))
    vertices_left = json.loads(request.form.get('vertices_left'))
    vertices_right = json.loads(request.form.get('vertices_right'))

    # left hemisphere
    if left_key:
        if use_preprocess:
            left_img = cache.get('preprocessed_left')
        else:
            left_img = cache.get(left_key)

        # convert to array
        left_img_array = gii_to_array(left_img)

        # calculate window average
        left_w_avg = analysis.window_average(
            left_img_array, markers, l_edge, r_edge
        )

        # convert to gifti
        left_avg_img = array_to_gii(left_w_avg)

    else:
        left_avg_img = None

    # right hemisphere
    if right_key:
        if use_preprocess:
            right_img = cache.get('preprocessed_right')
        else:
            right_img = cache.get(right_key)

        # convert to array
        right_img_array = gii_to_array(right_img)

        # calculate window average
        right_w_avg = analysis.window_average(
            right_img_array, markers, l_edge, r_edge
        )

        # convert to gifti
        right_avg_img = array_to_gii(right_w_avg)

    else:
        right_avg_img = None

    # get min and max for avg data
    metadata = package_gii_metadata(left_avg_img, right_avg_img)

    # save average map data in cache
    cache['avg_l'] = left_avg_img if left_key else None
    cache['avg_r'] = right_avg_img if right_key else None
    cache['avg_map'] = {}
    cache['avg_map']['plot_type'] = 'gifti'
    # ensure front-end knows where average maps are stored
    cache['avg_map']['left_key'] = 'avg_l' if left_key else None
    cache['avg_map']['right_key'] = 'avg_r' if right_key else None
    cache['avg_map']['global_min'] = metadata['global_min']
    cache['avg_map']['global_max'] = metadata['global_max']
    cache['avg_map']['timepoints'] = np.arange(l_edge, r_edge+1).tolist()
    cache['avg_map']['vertices_left'] = cache['vertices_left'] if left_key else None
    cache['avg_map']['vertices_right'] = cache['vertices_right'] if right_key else None
    cache['avg_map']['faces_left'] = cache['faces_left'] if left_key else None
    cache['avg_map']['faces_right'] = cache['faces_right'] if right_key else None

    return jsonify(success=True)


# route to compute cross-correlation of time course with gii data
@gifti_bp.route('/compute_corr_gii', methods=['POST'])
def compute_corr_nii():
    # load time course array
    ts = request.form.get('ts')
    ts = json.loads(ts)
    # convert to array with one column
    ts = np.array(ts)[:,np.newaxis]
    # load parameters
    ts_label = request.form.get('label')
    left_key = utils.convert_value(
        request.form.get('left_key')
    )
    right_key = utils.convert_value(
        request.form.get('right_key')
    )
    nlag = utils.convert_value(request.form.get('negative_lag'))
    plag = utils.convert_value(request.form.get('positive_lag'))
    use_preprocess = utils.convert_value(
        request.form.get('use_preprocess')
    )
    # Load mesh and face data
    faces_left = json.loads(request.form.get('faces_left'))
    faces_right = json.loads(request.form.get('faces_right'))
    vertices_left = json.loads(request.form.get('vertices_left'))
    vertices_right = json.loads(request.form.get('vertices_right'))

    # get array of lags
    lags = np.arange(nlag, plag+1)

    # left hemisphere
    if left_key:
        if use_preprocess:
            left_img = cache.get('preprocessed_left')
        else:
            left_img = cache.get(left_key)

        # convert to array
        left_img_array = gii_to_array(left_img)

        # compute correlation
        correlation_map_l = analysis.correlation(left_img_array, ts, lags)

        # convert to gifti
        corr_left_img = array_to_gii(correlation_map_l)

    else:
        corr_left_img = None

    # right hemisphere
    if right_key:
        if use_preprocess:
            right_img = cache.get('preprocessed_right')
        else:
            right_img = cache.get(right_key)

        # convert to array
        right_img_array = gii_to_array(right_img)

        # compute correlation
        correlation_map_r = analysis.correlation(right_img_array, ts, lags)

        # convert to gifti
        corr_right_img = array_to_gii(correlation_map_r)

    else:
        corr_right_img = None

    # get min and max for correlation map
    metadata = package_gii_metadata(corr_left_img, corr_right_img)


    # save correlation map data in cache
    cache['corr_l'] = corr_left_img if left_key else None
    cache['corr_r']= corr_right_img if right_key else None
    cache['corr_map'] = {}
    cache['corr_map']['plot_type'] = 'gifti'
    # ensure front-end knows where correlation maps are stored
    cache['corr_map']['left_key'] = 'corr_l' if left_key else None
    cache['corr_map']['right_key'] = 'corr_r' if right_key else None
    cache['corr_map']['global_min'] = metadata['global_min']
    cache['corr_map']['global_max'] = metadata['global_max']
    cache['corr_map']['timepoints'] = lags.tolist()
    cache['corr_map']['vertices_left'] = cache['vertices_left'] if left_key else None
    cache['corr_map']['vertices_right'] = cache['vertices_right'] if right_key else None
    cache['corr_map']['faces_left'] = cache['faces_left'] if left_key else None
    cache['corr_map']['faces_right'] = cache['faces_right'] if right_key else None

    return jsonify(success=True)


# utility concatenate 2d arrays from both hemispheres
def concat_gii_hemi(gifti_array_l, gifti_array_r):
    split_index = None
    if gifti_array_l is None:
        return gifti_array_r, split_index

    if gifti_array_r is None:
        return gifti_array_l, split_index

    # left hemisphere is always in the first position
    split_index = gifti_array_l.shape[1]
    gifti_img = np.hstack([gifti_array_r, gifti_array_l])
    return gifti_img, split_index


# utility - convert gifti to 2d array
def gii_to_array(gifti_img):
    data_2d = []
    for d in gifti_img.darrays:
        # Access the data arrays in the GIFTI files
        data_t = d.data
        data_2d.append(data_t)

    return np.vstack(data_2d)


# utility - create gifti object from 2d array
def array_to_gii(data):
    gifti_img = nib.GiftiImage()
    for row_i in range(data.shape[0]):
        gii_data_array = GiftiDataArray(
            data=data[row_i,:], datatype=16
        )
        gifti_img.add_gifti_data_array(gii_data_array)

    return gifti_img
