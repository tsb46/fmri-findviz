"""Handling main app screen, timecourse and visualization utilities"""

import csv
import decimal
import json
import os
import pickle
import tempfile

from io import TextIOWrapper

import numpy as np
import plotly.colors as pc

from flask import Blueprint, render_template, request, jsonify, send_file
from nilearn.glm.first_level import compute_regressor
from scipy.signal import find_peaks

from findviz.routes import utils
# from findviz.routes.utils import package_gii_metadata, package_nii_metadata


common_bp = Blueprint('common', __name__)  # Create a blueprint

# In-memory cache
cache = {}

# Route for the homepage
@common_bp.route('/')
def index():
    return render_template('index.html')

# display results view for a specific analysis route
@common_bp.route('/results_view/<analysis>')
def results_view(analysis):
    if analysis == 'average':
        data = cache['avg_map']
    elif analysis == 'correlate':
        data = cache['corr_map']
    return render_template('results.html', data=data, analysis=analysis)


# allow user to download cache for future uploads
@common_bp.route('/download_cache')
def download_cache():
    # Create a temporary file to save the cache
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'FIND_SCENE.pkl')

    # Save the data to a temporary file
    with open(file_path, 'wb') as f:
        pickle.dump(cache, f)
    # send cache to client
    return send_file(file_path, as_attachment=True)


# clear cache on file reupload
@common_bp.route('/clear_cache')
def clear_cache():
    # clear cache
    cache.clear()
    return "", 200


# allow user to upload cache ('scene') and start app
@common_bp.route('/upload_cache', methods=['POST'])
def upload_cache():
    # get cache file
    cache_file = request.files.get('scene_file')
    # try to load scene file
    try:
        upload_cache = pickle.load(cache_file.stream)
    except Exception as e:
        # return 500 error if problem
        return {'Error': str(e)}, 500
    # overwrite the existing cache
    global cache
    cache.clear()
    cache.update(upload_cache)

    # load cache data to 'simulate' file upload
    try:
        data_out = {}
        file_type = cache['file_type']
        data_out['file_type'] = file_type
        # handle nifti file uploads
        if file_type == 'nifti':
            data_out['file_key'] = cache['file_key']
            data_out['anat_key'] = cache.get('anat_key')
            data_out['mask_key'] = cache.get('mask_key')
            # get nifti img and calculate metadata
            nifti_img = cache[cache['file_key']]
            # get nifti metadata for viewer
            metadata = package_nii_metadata(nifti_img)
            data_out['timepoints'] = metadata['timepoints']
            data_out['global_min'] = metadata['global_min']
            data_out['global_max'] = metadata['global_max']
            data_out['slice_len'] = metadata['slice_len']

        elif file_type == 'gifti':
            data_out['left_key'] = cache.get('left_key')
            data_out['right_key'] = cache.get('right_key')
            # mesh data are numpy arrays, convert to json compatible
            mesh_fields = [
                'vertices_right',
                'vertices_left',
                'faces_left',
                'faces_right'
            ]
            for f in mesh_fields:
                f_data = cache.get(f)
                data_out[f] = f_data.tolist() if f_data is not None else None

            # get gifti metadata for viewer
            left_img = cache.get(data_out['left_key'])
            right_img = cache.get(data_out['right_key'])
            metadata = package_gii_metadata(left_img, right_img)
            data_out['timepoints'] = metadata['timepoints']
            data_out['global_min'] = metadata['global_min'].item()
            data_out['global_max'] = metadata['global_max'].item()

        # check whether timeseries were passed in input (don't count 'fmri')
        data_out['ts_enabled'] = False
        if 'timeseries' in cache:
            cache['timeseries'].pop('fmri', None)
            if len(cache['timeseries']) > 0:
                data_out['timeseries'] = {
                    'ts': list(cache['timeseries'].values()),
                    'tsLabels': list(cache['timeseries'].keys())
                }
                data_out['ts_enabled'] = True

        # check whether task design was passed in input
        if 'task' in cache:
            data_out['task'] = {
                "conditions_block": [
                    cache['task']['task_reg'][c]['block']
                    for c in cache['task']['conditions']
                ],
                "conditions_hrf": [
                    cache['task']['task_reg'][c]['hrf']
                    for c in cache['task']['conditions']
                ],
                "labels": cache['task']['conditions']
            }
            data_out['task_enabled'] = True
        else:
            data_out['task_enabled'] = False

    except KeyError as e:
        # cache is missing essential file input
        return {"Error": str(e)}, 500

    return jsonify(data_out)


# Route to load time series
@common_bp.route('/upload_ts', methods=['POST'])
def upload_ts():
    # initialize time course cache
    cache['timeseries'] = {}
    # Get the list of time series files
    ts_files = request.files.getlist('ts_files')
    ts_labels = request.form.getlist('ts_labels')
    ts_headers = request.form.getlist('ts_headers')
    fmri_file_type = request.form.get('fmri_file_type')
    file_key = request.form.get('file_key')
    # convert header flag to boolean
    ts_headers = [utils.convert_value(h) for h in ts_headers]
    # load fmri file to get number of time points
    fmri_img = cache.get(file_key)
    if fmri_file_type == 'nifti':
        fmri_len = fmri_img.shape[-1]
    elif fmri_file_type == 'gifti':
        fmri_len = len(fmri_img.darrays)

    # Load txt files and save in cache
    for ts_fp, ts_label, ts_header in zip(ts_files, ts_labels, ts_headers):
        # handle csv file inputs
        if ts_fp.filename.endswith('csv'):
            try:
                ts = read_csv(ts_fp, ',', ts_header)
                # grab the first column, rows with more than one column should
                # have been caught in javascript
                ts = [row[0] for row in ts]
            except:
                return jsonify(
                    {"error": f"unable to load file - {ts_fp.filename}. Check format."}
                ), 400  # Return 400 Bad Request
        # handle txt file inputs
        elif ts_fp.filename.endswith('txt'):
            try:
                # push up row if header present
                if ts_header:
                    row = 1
                else:
                    row = 0
                ts = np.loadtxt(ts_fp.stream, skiprows=row)
                # convert to list
                ts = ts.tolist()
            except:
                return jsonify(
                    {"error": f"unable to load file - {ts_fp.filename}. Check format."}
                ), 400  # Return 400 Bad Request

        # check length of time series match length of fMRI scan
        if len(ts) != fmri_len:
            return jsonify(
                {"error": f"length of {ts_fp.filename} ({len(ts)}) is not the same length as fmri volumes ({fmri_len})"}
            ), 400  # Return 400 Bad Request
        cache['timeseries'][ts_label] = ts
    return jsonify(
        {
            "ts": [cache['timeseries'][l] for l in ts_labels],
            'tsLabels': ts_labels
        }
    )


# Route to load task design file
@common_bp.route('/upload_task', methods=['POST'])
def upload_task():
    # Get and load task design files
    task_file = request.files.get('task_file')
    tr = utils.convert_value(request.form.get('task_tr'))
    slicetime_ref = utils.convert_value(
        request.form.get('task_slicetime_ref')
    )
    fmri_file_type = request.form.get('fmri_file_type')
    file_key = request.form.get('file_key')
    # determine whether tsv or csv (validated in javascript)
    if task_file.filename.endswith('csv'):
        delimiter = ','
    elif task_file.filename.endswith('tsv'):
        delimiter = '\t'
    try:
        task_events = read_csv(task_file, delimiter, skip_header=False)
    except:
        return jsonify(
            {"error": f"unable to load file - {task_file.filename}. Check format."}
        ), 400  # Return 400 Bad Request

    # load fmri file to get number of time points
    fmri_img = cache.get(file_key)
    if fmri_file_type == 'nifti':
        fmri_len = fmri_img.shape[-1]
    elif fmri_file_type == 'gifti':
        fmri_len = len(fmri_img.darrays)
    # calculate frame times based on lenght of fmri, slicetime ref and tr
    frame_times =  tr * (np.arange(fmri_len) + slicetime_ref)
    task_reg, conditions = get_task_regressors(task_events, frame_times)
    # assign task regressors and conditions to cache
    cache['task'] = {}
    cache['task']['task_reg'] = task_reg
    cache['task']['conditions'] = conditions
    return jsonify(
        {
            "conditions_block": [task_reg[c]['block'] for c in conditions],
            "conditions_hrf": [task_reg[c]['hrf'] for c in conditions],
            "labels": conditions,
        }
    )





# Route to calculate precision of floating point number for UserViz sliders
@common_bp.route('/get_precision', methods=['GET'])
def get_precision():
    data_range = request.args.get('data_range')
    data_range_dec = decimal.Decimal(data_range)
    return jsonify(abs(data_range_dec.as_tuple().exponent))


# Route to preprocess time courses
@common_bp.route('/preprocess_ts', methods=['POST'])
def preprocess_ts():
    # get passed json
    data = request.get_json()['data']
    # get parameters from response, convert numerics
    params = {
        'tr': utils.convert_value(data['TR']),
        'low_cut': utils.convert_value(data['lowCut']),
        'high_cut': utils.convert_value(data['highCut']),
        'mean_center': data['meanCenter'],
        'z_score': data['zScore'],
        'normalize': data['normalize'],
        'filter': data['filter']
    }
    # initialize ts output dict
    ts_out = {}
    # loop through ts selection
    for ts_label in data['tsLabels']:
        # get time course from cache and convert to 2d array w/ 1 column
        ts = np.array(cache['timeseries'][ts_label])[:,np.newaxis]
        # perform filtering, if specified
        if params['filter']:
            ts = utils.filter(
                ts, params['low_cut'], params['high_cut'],
                params['tr']
            )

        # perform normalization, if specified
        if params['normalize']:
            # get norm method
            if params['mean_center']:
                norm_method = 'mean_center'
            elif params['z_score']:
                norm_method = 'z_score'
            ts = utils.normalize(
                ts, norm_method, axis=0
            )
        # assign to output dictionary
        ts_out[ts_label] = np.squeeze(ts).tolist()

    return jsonify(ts_out)


# Route to preprocess time courses
@common_bp.route('/find_peaks_ts', methods=['POST'])
def find_peaks_ts():
    # load time course array
    ts = request.form.get('ts')
    ts = json.loads(ts)
    # get parameters from response, convert numerics
    peak_params = {
        'peak_height': request.form.get('peak_height'),
        'peak_threshold': request.form.get('peak_threshold'),
        'peak_distance': request.form.get('peak_distance'),
        'peak_prominence': request.form.get('peak_prominence'),
        'peak_width': request.form.get('peak_width')
    }
    peak_params = utils.convert_params(peak_params)

    # find peaks with scipy
    peaks, _ = find_peaks(
        ts,
        height = peak_params['peak_height'],
        threshold = peak_params['peak_threshold'],
        distance = peak_params['peak_distance'],
        prominence = peak_params['peak_prominence'],
        width = peak_params['peak_width']
    )
    return jsonify({
        'peaks': peaks.tolist()
    })



def get_task_regressors(task_events, frame_times):
    # get task regressors from task events
    # initialize task regressors dict
    task_reg = {}
    # pop header from task events
    header = task_events.pop(0)
    # get column index of onset and duration trial
    onset_idx = header.index('onset')
    duration_idx = header.index('duration')
    # first, check whether 'trial_types' is in header
    if 'trial_type' in header:
        trial_type_flag = True
        trial_type_idx = header.index('trial_type')
        conditions = list(set([r[trial_type_idx] for r in task_events]))
    else:
        trial_type_flag = False
        conditions = ['task']

    # Loop through each condition and create regressors
    for c in conditions:
        task_reg[c] = {}
        # get row indices of condition events
        if trial_type_flag:
            condition_idx = [
                i for i, r in enumerate(task_events)
                if r[trial_type_idx] == c
            ]
        else:
            condition_idx = list(range(len(task_events)))
        # Get onset of events in condition
        c_onsets = [
            float(task_events[i][onset_idx]) for i in condition_idx
        ]
        # Get duration of events in condition
        c_duration = [
            float(task_events[i][duration_idx]) for i in condition_idx
        ]
        # generate dummy amplitude values of 1s
        c_amp = [1 for i in condition_idx]
        # package condition data into nested list
        conditions_desc = [c_onsets, c_duration, c_amp]
        # use nilearn to compute task regression w/o convolution
        cond_reg, _ = compute_regressor(
            conditions_desc, hrf_model=None, frame_times=frame_times
        )
        task_reg[c]['block'] = cond_reg[:,0].tolist()
        # use nilearn to compute task regression w hrf convolution
        cond_reg, _ = compute_regressor(
            conditions_desc, hrf_model='glover', frame_times=frame_times
        )
        task_reg[c]['hrf'] = cond_reg[:,0].tolist()

    return task_reg, conditions


def read_csv(fp, delimiter, skip_header=True):
    # start reading after first line, if header
    if skip_header:
        row = 1
    else:
        row = 0
    file_stream = TextIOWrapper(fp.stream, encoding='utf-8-sig')
    # Create a CSV reader from the file stream
    csvreader = csv.reader(file_stream, delimiter=delimiter)

    # Skip the first line (header), if needed
    if row == 1:
        next(csvreader)

    # Read the remaining rows
    out = [row for row in csvreader]
    return out


def generate_colormap_data(colormaps):
    colormap_data = {}
    for cmap in colormaps:
        # Get the colorscale for each colormap
        colormap_colors = pc.get_colorscale(cmap)
        # Convert Plotly color codes to rgb
        rgb_colors = [
            (pos, code_to_rgb(color_code))
            for pos, color_code in colormap_colors
        ]
        # Put into html
        gradient = "linear-gradient(to right, " + ", ".join(
            [f"rgb({r},{g},{b})" for pos, (r, g, b) in rgb_colors]
        ) + ")"
        # package output
        colormap_data[cmap] = {
            'label': cmap,
            'gradient': gradient
        }
    return colormap_data


def code_to_rgb(color_code):
    # Some colormaps are in hex format, others rgb
    # if hex format
    if color_code.startswith('#'):
        color_rgb = pc.hex_to_rgb(color_code)
    # otherwise, assume rgb
    else:
        # clean string
        color_clean = color_code.replace('rgb(','').replace(')','')
        color_rgb = [int(c) for c in color_clean.split(',')]
    return color_rgb
