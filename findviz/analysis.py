import numpy as np

from scipy.stats import zscore

# window averaging around time points (markers)
def window_average(data, markers, left_edge, right_edge):
    # index windows for each marker
    windows = []
    for center in markers:
        windows.append(
            extract_range(data, center, left_edge, right_edge)
        )
    # convert to 3d array
    windows = np.stack(windows, axis=0)

    # average all windows
    w_avg = np.nanmean(windows, axis=0)

    return w_avg

# correlation between fMRI and ts (and lags)
def correlation(data, ts, lags):
    # standardize nifti and time course data
    ts = zscore(ts)
    data = zscore(data, axis=0)

    # get lag matrix
    lagmat = lag_mat(ts, lags)
    # compute correlation map
    correlation_map = (
        np.dot(data.T, lagmat) / len(ts)
    )
    return correlation_map.T

# index array with range (w/ NaN padding for out-of-bound indices )
def extract_range(array, center, left_edge, right_edge):
    num_rows, num_cols = array.shape
    range_size = right_edge - left_edge + 1
    # Create a NaN-filled placeholder for the range
    padded_range = np.full((range_size, num_cols), np.nan)

    # Calculate valid row indices
    start = max(0, center + left_edge)  # Valid start index in the array
    end = min(num_rows, center + right_edge + 1)  # Valid end index in the array
    insert_start = max(0, -1 * (center + left_edge))  # Where to insert in padded_range
    insert_end = insert_start + (end - start)  # End position in padded_range

    # Insert valid rows into the padded range
    padded_range[insert_start:insert_end, :] = array[start:end, :]
    return padded_range


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
