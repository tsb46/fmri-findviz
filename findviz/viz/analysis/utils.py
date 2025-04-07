import numpy as np


# index array with range (w/ NaN padding for out-of-bound indices )
def extract_range(array, center, left_edge, right_edge):
    """
    Extract a range of rows from an array with NaN padding for out-of-bound indices

    Parameters
    ----------
    array : np.ndarray
        array to extract range from
    center : int
        center of the range
    left_edge : int
        left edge of the range
    right_edge : int
        right edge of the range

    Returns
    -------
    padded_range : np.ndarray
        array with NaN padding for out-of-bound indices
    """
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


def get_lag_mat(x: np.ndarray, lags: list) -> np.ndarray:
    """
    Create array of time-lagged copies of the time course. Modified
    for negative lags from:
    https://github.com/ulf1/lagmat

    Parameters
    ----------
    x : np.ndarray
        time course (n_timepoints)
    lags : list
        lags (n_lags)

    Returns
    -------
    x_lag : np.ndarray
        time-lagged copies of the time course (n_timepoints, n_lags * n_timepoints)
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
        
        # Skip if lag is out of bounds (lag >= array length)
        if abs(l) >= n_rows:
            continue
            
        # number rows of X
        nl = n_rows - abs(l)
        
        # Copy
        if l >= 0:
            x_lag[l:, j:k] = x[:nl, :]
        else:
            x_lag[:l, j:k] = x[-nl:, :]
    return x_lag

