"""
GIFTI data handling
"""

from typing import Tuple, Optional, List, Literal, TypedDict

import nibabel as nib
import numpy as np

from findviz.routes.utils import sanitize_array_for_json


class GiftiTimePointData(TypedDict):
    left_hemisphere: List[float]
    right_hemisphere: List[float]

def get_gifti_data(
    time_point: int,
    left_func_img: Optional[nib.GiftiImage],
    right_func_img: Optional[nib.GiftiImage],
    threshold_min: float = 0,
    threshold_max: float = 0,
    threshold_min_orig: float = 0,
    threshold_max_orig: float = 0
) -> GiftiTimePointData:
    """Get functional data for a specific timepoint from left and right hemisphere Gifti images.
    
    Parameters:
    -----------
        time_point : int
            The timepoint to extract data from
        left_func_img : nib.GiftiImage
            Gifti image containing left hemisphere functional data
        right_func_img : nib.GiftiImage
            Gifti image containing right hemisphere functional data
        threshold_min : float
            Minimum threshold value
        threshold_max : float
            Maximum threshold value
        threshold_min_orig : float
            Original minimum threshold value
        threshold_max_orig : float
            Original maximum threshold value
    Returns:
    --------
        Dictionary containing:
            - Left hemisphere functional data array for the timepoint (None if no left data)
            - Right hemisphere functional data array for the timepoint (None if no right data)
    """
    func_data_left = None
    func_data_right = None

    # Handle left hemisphere Gifti file
    if left_func_img is not None:
        func_data_left = left_func_img.darrays[time_point].data.copy()
        # threshold data if threshold_min or threshold_max have been changed
        if (threshold_min != threshold_min_orig) or (threshold_max != threshold_max_orig):
            func_data_left = threshold_gifti_data(
                func_data_left, threshold_min, threshold_max
            )
        # sanitize data
        func_data_left = sanitize_array_for_json(func_data_left)

    # Handle right hemisphere Gifti file
    if right_func_img is not None:
        func_data_right = right_func_img.darrays[time_point].data.copy()
        # threshold data if threshold_min or threshold_max have been changed
        if (threshold_min != threshold_min_orig) or (threshold_max != threshold_max_orig):
            func_data_right = threshold_gifti_data(
                func_data_right, threshold_min, threshold_max
            )
        # sanitize data
        func_data_right = sanitize_array_for_json(func_data_right)

    gifti_data = {
        'left_hemisphere': func_data_left,
        'right_hemisphere': func_data_right
    }

    return gifti_data


def get_timecourse_gifti(
    left_func_img: Optional[nib.GiftiImage],
    right_func_img: Optional[nib.GiftiImage],
    vertex_index: int,
    hemisphere: Literal['left', 'right'],
) -> Tuple[List[float], str]:
    """Get functional time course and label for a specific vertex 
    from left or right hemisphere Gifti images
    
    Parameters:
    ------------  
        left_func_img : nib.GiftiImage
            Gifti image containing left hemisphere functional data
        right_func_img : nib.GiftiImage
            Gifti image containing right hemisphere functional data
        vertex_index : int
            The vertex index to extract data from
        hemisphere : Literal['left', 'right']
            The hemisphere to extract data from
    
    Returns:
    --------
        Tuple containing:
            - Functional time course for vertex
            - Label for functional time course
    """
    if hemisphere == 'left':
        gifti_img = left_func_img
    elif hemisphere == 'right':
        gifti_img = right_func_img

    # Extract the vertex's time course
    time_course = [d.data[vertex_index] for d in gifti_img.darrays]
    time_course = [t.item() for t in time_course]

    # create time course label
    time_course_label = f'Vertex: {vertex_index} ({hemisphere})'

    return time_course, time_course_label


def threshold_gifti_data(
    gifti_data: np.ndarray,
    threshold_min: float,
    threshold_max: float,
) -> np.ndarray:
    """Threshold a list of functional data
    
    Parameters:
    -----------
        gifti_data: np.ndarray
            List of functional data
        threshold_min: float
            Minimum threshold value
        threshold_max: float
            Maximum threshold value
    
    Returns:
    --------
        np.ndarray of thresholded functional data
    """
    # create mask
    mask = (gifti_data >= threshold_min) & (gifti_data <= threshold_max)
    # apply mask
    gifti_data[mask] = np.nan
    return gifti_data
