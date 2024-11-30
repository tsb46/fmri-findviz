"""Routes for Nifti file handling and utilities"""

import json
import gzip
import os
import tempfile

from io import BytesIO

import nibabel as nib
import numpy as np

from flask import Blueprint, request, jsonify, render_template
from nilearn.image import index_img, reorder_img, smooth_img
from nilearn import masking
from scipy.stats import zscore

from findviz import analysis
from findviz.routes import utils
from findviz.routes.common import cache
from findviz.routes.utils import package_nii_metadata


nifti_bp = Blueprint('nifti', __name__)  # Create a blueprint

# Save the NIfTI file in a temporary directory
nifti_dir = tempfile.mkdtemp()

# Upload nifti file
@nifti_bp.route('/upload_nii', methods=['POST'])
def upload_files_nii():
    cache['file_type'] = 'nifti'
    nifti_file = request.files.get('nifti_file')
    anatomical_file = request.files.get('anatomical_file')
    mask_file = request.files.get('mask_file')
    # Load NIfTI files
    file_key = nifti_file.filename
    cache['file_key'] = file_key
    try:
        nifti_img = load_nii_file(nifti_file)
    except nib.spatialimages.HeaderDataError:
        error_msg = 'There was a problem reading header of functional file'
        return jsonify({'error': error_msg, 'file': 'func'}), 400

    # If nifti is not 4D, return error
    if len(nifti_img.shape) < 4:
        error_msg = 'Only 4D NIfTI files are not supported for functional file'
        return jsonify({'error': error_msg, 'file': 'func'}), 400

    # reorient to RAS
    nifti_img = reorder_img(nifti_img)
    # store in cache
    cache[file_key] = nifti_img

    # handle anatomical file (optional)
    anatomical_img = None
    if anatomical_file:
        anatomical_key = anatomical_file.filename
        cache['anat_key'] = anatomical_key
        # load anatomical file
        try:
            anatomical_img = load_nii_file(anatomical_file)
        except nib.spatialimages.HeaderDataError:
            error_msg = 'There was a problem reading header of anatomical file'
            return jsonify({'error': error_msg, 'file': 'anat'}), 400

        # If anat nifti is not 3D, return error
        if len(anatomical_img.shape) > 3:
            error_msg = 'Anatomical file must be a 3D NIfTI file'
            return jsonify({'error': error_msg, 'file': 'anat'}), 400

        # Check anat nifti has the same field of view
        if not np.array_equal(anatomical_img.shape, nifti_img.shape[:3]):
            error_msg = 'Anatomical file must have same Field-of-View (FOV) as functional file'
            return jsonify({'error': error_msg, 'file': 'anat'}), 400
        # Reorient to RAS
        anatomical_img = reorder_img(anatomical_img)
        # store in cache
        cache[anatomical_key] = anatomical_img

    # handle mask file (optional)
    mask_img = None
    if mask_file:
        mask_key = mask_file.filename
        cache['mask_key'] = mask_key
        # load mask file
        try:
            mask_img = load_nii_file(mask_file)
        except nib.spatialimages.HeaderDataError:
            error_msg = 'There was a problem reading header of mask file'
            return jsonify({'error': error_msg, 'file': 'mask'}), 400

        # If nifti is not 3D, return error
        if len(mask_img.shape) > 3:
            error_msg = 'Brain mask file must be a 3D NIfTI file'
            return jsonify({'error': error_msg, 'file': 'mask'}), 400

        # check mask is same FOV
        if not np.array_equal(mask_img.shape, nifti_img.shape[:3]):
            error_msg = 'Mask file must have same Field-of-View (FOV) as functional file'
            return jsonify({'error': error_msg, 'file': 'mask'}), 400

        # Reorient to RAS
        mask_img = reorder_img(mask_img)
        # store mask img in cache
        cache[mask_key] = mask_img

    # get data for return to app
    metadata = package_nii_metadata(nifti_img)

    return jsonify({
        'file_key': file_key,
        'anat_key': anatomical_key if anatomical_img else None,
        'mask_key': mask_key if mask_img else None,
        'timepoints': metadata['timepoints'],
        'slice_len': metadata['slice_len'],
        'global_min': metadata['global_min'],
        'global_max': metadata['global_max']
    })


# Route to get all three slices (X, Y, Z) at a specific time point
@nifti_bp.route('/get_slices', methods=['POST'])
def get_slices():
    file_key = request.form.get('file_key')
    anat_key = request.form.get('anat_key')
    mask_key = request.form.get('mask_key')
    view_state = request.form.get('view_state')
    montage_slice_dir = request.form.get('montage_slice_dir')
    x_slice = request.form.get('x_slice')
    y_slice = request.form.get('y_slice')
    z_slice = request.form.get('z_slice')
    time_point = int(request.form.get('time_point', 0))
    use_preprocess = utils.convert_value(
        request.form.get('use_preprocess')
    )
    update_voxel_coord = utils.convert_value(
        request.form.get('update_voxel_coord')
    )

    # Get nifti img
    if use_preprocess:
        nifti_img = cache.get('preprocessed')
    else:
        nifti_img = cache.get(file_key)
    if not nifti_img:
        return jsonify({'error': 'File not found'}), 404

    # get anatomical file (optional), returns None if no image supplied
    anat_img = cache.get(anat_key)

    # get mask file (optional), returns None if no image supplied
    mask_img = cache.get(mask_key)

    # Select time point
    nifti_img_t = index_img(nifti_img, time_point)

    slice_out = {
        'func': {},
        'anat': {},
        'mask': {},
        'coords': {}
    }
    # Loop through axes and update
    for axis, slice_i in zip(['x', 'y', 'z'], [x_slice, y_slice, z_slice]):
        # set axis to all same direction, if montage
        if view_state == 'montage':
            nifti_axis = montage_slice_dir
        else:
            nifti_axis = axis
        slice_int = int(slice_i)
        slice_out['func'][axis] = get_plotly_slice_data(
            nifti_img_t, slice_int, axis=nifti_axis
        )
        if anat_img:
            slice_out['anat'][axis] = get_plotly_slice_data(
                anat_img, slice_int, axis=nifti_axis
            )
        if mask_img:
            slice_out['mask'][axis] = get_plotly_slice_data(
                mask_img, slice_int, axis=nifti_axis
            )
        if update_voxel_coord:
            slice_out['coords'][axis] = [
                [(slice_int, j, i)
                for j in range(slice_out['func'][axis].shape[1])]
                for i in range(slice_out['func'][axis].shape[0])
            ]

    return jsonify({
        'x_slice': sanitize_data(slice_out['func']['x']),
        'y_slice': sanitize_data(slice_out['func']['y']),
        'z_slice': sanitize_data(slice_out['func']['z']),
        'x_slice_anat': sanitize_data(slice_out['anat']['x']) if anat_img else None,
        'y_slice_anat': sanitize_data(slice_out['anat']['y']) if anat_img else None,
        'z_slice_anat': sanitize_data(slice_out['anat']['z']) if anat_img else None,
        'x_slice_mask': sanitize_data(slice_out['mask']['x']) if mask_img else None,
        'y_slice_mask': sanitize_data(slice_out['mask']['y']) if mask_img else None,
        'z_slice_mask': sanitize_data(slice_out['mask']['z']) if mask_img else None,
        'x_voxel_coords': slice_out['coords']['x'] if update_voxel_coord else None,
        'y_voxel_coords': slice_out['coords']['y'] if update_voxel_coord else None,
        'z_voxel_coords': slice_out['coords']['z'] if update_voxel_coord else None
    })


# Route to fetch time course data for a selected voxel
@nifti_bp.route('/get_time_course_nii', methods=['GET'])
def get_time_course_nii():
    file_key = request.args.get('file_key')
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    z = int(request.args.get('z'))
    # determine whether to use preprocessed data
    use_preprocess = utils.convert_value(
        request.args.get('use_preprocess')
    )

    # Get nifti img
    if use_preprocess:
        nifti_img = cache.get('preprocessed')
    else:
        nifti_img = cache.get(file_key)
    if not nifti_img:
        return jsonify({'error': 'File not found'}), 404

    # Extract the voxel's time course
    time_course = nifti_img.get_fdata()[x, y, z, :].tolist()

    # store in cache
    if 'timeseries' in cache:
        cache['timeseries']['fmri'] = time_course
    else:
        cache['timeseries'] = {
            'fmri': time_course
        }

    return jsonify({'time_course': time_course})


# route to normalize nifti time course
@nifti_bp.route('/preprocess_nii', methods=['GET'])
def preprocess_nii():
    # If reset, deleted preprocessed data and pass raw data
    reset = utils.convert_value(
        request.args.get('reset')
    )
    if reset:
        # ensure preprocessed file is in cache before deleting
        if 'preprocessed' in cache:
            del cache['preprocessed']
        # Pass raw global min and max
        return jsonify({
            'global_min': cache['global_min'],
            'global_max': cache['global_max']
        })

    # get data passed from fetch
    file_key = request.args.get('file_key')
    norm_enabled = utils.convert_value(
        request.args.get('normalize_enabled')
    )
    filter_enabled = utils.convert_value(
        request.args.get('filter_enabled')
    )
    smooth_enabled = utils.convert_value(
        request.args.get('smooth_enabled')
    )
    mask_key = request.args.get('mask_key')
    params = {
        'tr': request.args.get('TR'),
        'low_cut': request.args.get('lowCut'),
        'high_cut': request.args.get('highCut'),
        'mean_center': request.args.get('meanCenter'),
        'z_score': request.args.get('zScore'),
        'fwhm': request.args.get('smoothFWHM')
    }

    # convert params from response
    params = utils.convert_params(params)
    nifti_img = cache.get(file_key)
    if not nifti_img:
        return jsonify({'error': 'File not found'}), 404

    # perform filtering first, if specified
    if filter_enabled:
        # get mask file
        mask_img = cache.get(mask_key)
        # get 2d array within mask
        nifti_2d = masking.apply_mask(nifti_img, mask_img)
        # temporal filtering
        nifti_2d_filt = utils.filter(
            nifti_2d, params['low_cut'], params['high_cut'],
            params['tr']
        )
        # put back into 4d array
        nifti_img = masking.unmask(nifti_2d_filt, mask_img)
        # Free up memory
        del nifti_2d, nifti_2d_filt

    # perform spatial smoothing, if specified
    if smooth_enabled:
        nifti_img = smooth_img(nifti_img, params['fwhm'])


    # perform normalization, if specified
    if norm_enabled:
        # get norm method
        if params['mean_center']:
            norm_method = 'mean_center'
        elif params['z_score']:
            norm_method = 'z_score'
        else:
            return jsonify({'error': 'normalization option unrecognized'}), 404
        # Normalize data
        data_norm = utils.normalize(
            nifti_img.get_fdata(), norm_method, axis=3
        )
        # create new nifti object
        nifti_img = nib.Nifti1Image(
            data_norm, nifti_img.affine, nifti_img.header
        )
        # free up memory
        del data_norm


    # get preprocessed data for min and max
    nifti_data = nifti_img.get_fdata()
    global_min_norm, global_max_norm = utils.get_minmax(nifti_data, 'nifti')

    # save preprocessed data in cache
    cache['preprocessed'] = nifti_img

    # pass new global min and global max
    return jsonify({
        'global_min': global_min_norm,
        'global_max': global_max_norm
    })


# route to get world (scanner/atlas) coordinates
@nifti_bp.route('/get_world_coords', methods=['GET'])
def get_world_coords():
    # get nifti img affine
    file_key = request.args.get('file_key')
    affine = cache[file_key].affine
    # get current slice indices
    x = utils.convert_value(request.args.get('x'))
    y = utils.convert_value(request.args.get('y'))
    z = utils.convert_value(request.args.get('z'))
    coords = [x,y,z,1]
    # project voxel coordinates to world coords
    x_world, y_world, z_world, _ = np.dot(affine, coords)
    return jsonify(
        {'x': x_world, 'y': y_world, 'z': z_world}
    )


# route to compute window average of nii data
@nifti_bp.route('/compute_avg_nii', methods=['POST'])
def compute_avg_nii():
    # load markers
    markers = request.form.get('markers')
    markers = json.loads(markers)
    # load parameters
    file_key = request.form.get('file_key')
    mask_key = request.form.get('mask_key')
    anat_key = request.form.get('anat_key')
    slice_len = request.form.get('slice_len')
    l_edge = utils.convert_value(request.form.get('left_edge'))
    r_edge = utils.convert_value(request.form.get('right_edge'))
    use_preprocess = utils.convert_value(
        request.form.get('use_preprocess')
    )
    # Get nifti img
    if use_preprocess:
        nifti_img = cache.get('preprocessed')
    else:
        nifti_img = cache.get(file_key)
    if not nifti_img:
        return jsonify({'error': 'Nifti file not found'}), 404

    # get mask file
    mask_img = cache.get(mask_key)
    if not mask_img:
        return jsonify({'error': 'Mask file not found'}), 404

    # get 2d array within mask
    nifti_2d = masking.apply_mask(nifti_img, mask_img)

    # calculate window average
    w_avg = analysis.window_average(nifti_2d, markers, l_edge, r_edge)

    # convert 2d array back to nifti
    nifti_img_avg = masking.unmask(
        w_avg,
        mask_img
    )
    # get min and max of new nifti
    metadata = package_nii_metadata(nifti_img_avg)
    # save correlation map data in cache
    cache['avg'] = nifti_img_avg
    cache['avg_map'] = {}
    cache['avg_map']['plot_type'] = 'nifti'
    # ensure front-end knows where average maps are stored
    cache['avg_map']['file_key'] = 'avg'
    cache['avg_map']['mask_key'] = mask_key
    cache['avg_map']['anat_key'] = anat_key
    cache['avg_map']['slice_len'] = metadata['slice_len']
    cache['avg_map']['global_min'] = metadata['global_min']
    cache['avg_map']['global_max'] = metadata['global_max']
    cache['avg_map']['timepoints'] = np.arange(l_edge, r_edge+1).tolist()

    return jsonify(success=True)

# route to compute cross-correlation of time course with nii data
@nifti_bp.route('/compute_corr_nii', methods=['POST'])
def compute_corr_nii():
    # load time course array
    ts = request.form.get('ts')
    ts = json.loads(ts)
    # convert to array with one column
    ts = np.array(ts)[:,np.newaxis]
    # load parameters
    ts_label = request.form.get('label')
    file_key = request.form.get('file_key')
    mask_key = request.form.get('mask_key')
    anat_key = request.form.get('anat_key')
    slice_len = request.form.get('slice_len')
    nlag = utils.convert_value(request.form.get('negative_lag'))
    plag = utils.convert_value(request.form.get('positive_lag'))
    use_preprocess = utils.convert_value(
        request.form.get('use_preprocess')
    )
    # Get nifti img
    if use_preprocess:
        nifti_img = cache.get('preprocessed')
    else:
        nifti_img = cache.get(file_key)
    if not nifti_img:
        return jsonify({'error': 'Nifti file not found'}), 404

    # get mask file
    mask_img = cache.get(mask_key)
    if not mask_img:
        return jsonify({'error': 'Mask file not found'}), 404

    # get 2d array within mask
    nifti_2d = masking.apply_mask(nifti_img, mask_img)

    # get array of lags
    lags = np.arange(nlag, plag+1)

    # compute correlation
    correlation_map = analysis.correlation(nifti_2d, ts, lags)

    # convert 2d array back to nifti
    nifti_img_corr = masking.unmask(
        correlation_map,
        mask_img
    )

    # get min and max of new nifti
    metadata = package_nii_metadata(nifti_img_avg)

    # save correlation map data in cache
    cache['corr'] = nifti_img_corr
    cache['corr_map'] = {}
    cache['corr_map']['plot_type'] = 'nifti'
    # ensure front-end knows where correlation maps are stored
    cache['corr_map']['file_key'] = 'corr'
    cache['corr_map']['mask_key'] = mask_key
    cache['corr_map']['anat_key'] = anat_key
    cache['corr_map']['slice_len'] = metadata['slice_len']
    cache['corr_map']['global_min'] = metadata['global_min']
    cache['corr_map']['global_max'] = metadata['global_max']
    cache['corr_map']['timepoints'] = lags.tolist()

    return jsonify(success=True)


# Helper function to load nifti data
def load_nii_file(nifti_file):
    try:
        file_stream = BytesIO(nifti_file.read())
        # load compressed gzip file
        if nifti_file.filename.endswith('.nii.gz'):
            with gzip.GzipFile(fileobj=file_stream, mode="rb") as d_stream:
                nifti_data = BytesIO(d_stream.read())
            file_stream.close()
            nifti_img = nib.Nifti1Image.from_bytes(nifti_data.read())
        elif nifti_file.filename.endswith('.nii'):
            nifti_img = nib.Nifti1Image.from_bytes(file_stream.read())

        return nifti_img
    # If header throws error, raise error
    except nib.spatialimages.HeaderDataError as e:
        raise


# Helper function to generate Plotly slice data
def get_plotly_slice_data(nifti_img, slice_index, axis='x'):
    # Extract the slice data
    if axis == 'x':
        slice_data = np.squeeze(
            nifti_img.get_fdata()[slice_index, :, :]
        ).transpose()
    elif axis == 'y':
        slice_data = np.squeeze(
            nifti_img.get_fdata()[:, slice_index, :]
        ).transpose()
        # flip for radiological
        # slice_data = np.flip(slice_data, axis=1)
    elif axis == 'z':
        slice_data = np.squeeze(
            nifti_img.get_fdata()[:, :, slice_index]
        ).transpose()
        # flip for radiological
        # slice_data = np.flip(slice_data, axis=1)

    return slice_data


# Helper function to sanitize data by replacing NaN/Inf with zero
def sanitize_data(slice_data):
    if isinstance(slice_data, np.ndarray):
        slice_data = np.nan_to_num(slice_data, nan=0.0, posinf=0.0, neginf=0.0)
        return slice_data.tolist()
    return slice_data

