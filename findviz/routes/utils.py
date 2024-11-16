"""Utility Modules"""

import numpy as np

from nilearn import signal
from scipy.stats import zscore


def lag_mat(x, lags):
    """
    Create array of time-lagged copies of the time course. Modified
    for negative lags from:
    https://github.com/ulf1/lagmat
    """
    n_rows, n_cols = x.shape
    n_lags = len(lags)
    # return if no lags
    if n_lags < 1:
        return x
    # allocate memory
    x_lag = np.zeros(
        shape=(n_rows, n_cols * n_lags),
        order='F', dtype=x.dtype
    )
    # Copy lagged columns of X into X_lag
    for i, l in enumerate(lags):
        # target columns of X_lag
        j = i * n_cols
        k = j + n_cols  # (i+1) * ncols
        # number rows of X
        nl = n_rows - abs(l)
        # Copy
        if l >= 0:
            x_lag[l:, j:k] = x[:nl, :]
        else:
            x_lag[:l, j:k] = x[-nl:, :]
    return x_lag


# Convert values from json
def convert_value(value):
    # Check for booleans
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
    # Check for None
    if value.lower() == 'null' or value.lower() == 'none' or value == '':
        return None
    # Try to convert to integer
    try:
        return int(value)
    except ValueError:
        pass
    # Try to convert to float
    try:
        return float(value)
    except ValueError:
        pass
    # Return the value as-is if no conversion happened
    return value


# Function to apply conversion to all values in a dictionary
def convert_params(params):
    return {key: convert_value(value) for key, value in params.items()}

# Function to convert strings (passed via fetch) to list of floats
def str_to_float_list(string):
    return list(map(float, string.split(',')))


# Function to detect header
def detect_header_csv(ts_file):
    # initialize state variables
    success = False
    header = False
    with open(ts_file, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)
        # Ensure the file only has one column
        for row in reader:
            if len(row) != 1:
                firstrow = None
                return header, firstrow, success

        # Move back to the start of the file after checking the column count
        file.seek(0)
        reader = csv.reader(file, delimiter=delimiter)

        # Read the first two rows
        first_row = next(reader, None)
        second_row = next(reader, None)

        # If only one row exists, assume no header (we need at least two rows to compare)
        if second_row is None:
            success = True
            header = False
            return header, firstrow, success

        success = True
        # Check if the first row is non-numeric and the second row is numeric
        if not is_numeric(first_row[0]) and is_numeric(second_row[0]):
            header = True
        else:
            header = False
        return header, firstrow, success


# Get minimum and maximum of data of nifti or gifti
def get_minmax(data, file_type):
    if file_type == 'nifti':
        data_min = np.nanmin(data)
        data_max = np.nanmax(data)
    elif file_type == 'gifti':
        data_min = np.min([np.min(d.data) for d in data.darrays])
        data_max = np.max([np.max(d.data) for d in data.darrays])

    return data_min, data_max


# check string is numeric
def is_numeric(value):
    try:
        float(value)  # Try to convert to a number
        return True
    except ValueError:
        return False


# temporal filtering with nilearn
def filter(data, lowCut, highCut, tr):
    # compute sampling frequency
    sf = 1/tr
    # perform filtering
    data_filtered = signal.butterworth(
        data, sampling_rate=sf, low_pass=highCut,
        high_pass=lowCut
    )
    return data_filtered

# Normalize time courses based on file type (gifti vs nifti)
def normalize(data, norm, axis):
    # z-score normalization
    if norm == 'z_score':
        data_norm = data - data.mean(axis=axis, keepdims=True)
        data_norm = data_norm / data_norm.std(axis=axis, keepdims=True)
        # handle constant values that return nan
        data_norm = np.nan_to_num(data_norm, copy=False, nan=0.0)
    elif norm == 'mean_center':
        data_norm = data - data.mean(axis=axis, keepdims=True)

    return data_norm


