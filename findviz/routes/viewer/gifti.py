"""
GIFTI data handling
"""

from typing import Tuple, Optional, List, Literal

import nibabel as nib
import numpy as np


def get_gifti_timepoint_data(
    time_point: int,
    func_left_img: Optional[nib.GiftiImage],
    func_right_img: Optional[nib.GiftiImage],
) -> Tuple[Optional[List[float]], Optional[List[float]]]:
    """Get functional data for a specific timepoint from left and right hemisphere Gifti images.
    
    Args:
        time_point: The timepoint to extract data from
        func_left_img: Gifti image containing left hemisphere functional data
        func_right_img: Gifti image containing right hemisphere functional data
        
    Returns:
        Tuple containing:
            - Left hemisphere functional data array for the timepoint (None if no left data)
            - Right hemisphere functional data array for the timepoint (None if no right data)
    """
    func_data_left = None
    func_data_right = None

    # Handle left hemisphere Gifti file
    if func_left_img is not None:
        func_data_left = func_left_img.darrays[time_point].data.tolist()

    # Handle right hemisphere GIFti file
    if func_right_img is not None:
        func_data_right = func_right_img.darrays[time_point].data.tolist()

    return func_data_left, func_data_right


def get_timecourse_gifti(
    func_left_img: Optional[nib.GiftiImage],
    func_right_img: Optional[nib.GiftiImage],
    vertex_index: int,
    hemisphere: Literal['left', 'right'],
) -> Tuple[List[float], str]:
    """Get functional time course and label for a specific vertex 
    from left or right hemisphere Gifti images
    
    Arguments:
    ----------  
        func_left_img: Gifti image containing left hemisphere functional data
        func_right_img: Gifti image containing right hemisphere functional data
        vertex_index: The vertex index to extract data from
        hemisphere: The hemisphere to extract data from
    
    Returns:
    --------
        Tuple containing:
            - Functional time course for vertex
            - Label for functional time course
    """
    if hemisphere == 'left':
        gifti_img = func_left_img
    elif hemisphere == 'right':
        gifti_img = func_right_img

    # Extract the vertex's time course
    time_course = [d.data[vertex_index] for d in gifti_img.darrays]
    time_course = [t.item() for t in time_course]

    # create time course label
    time_course_label = f'Hemisphere: {hemisphere}, Vertex: {vertex_index}'

    return time_course, time_course_label

