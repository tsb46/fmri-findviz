"""
File upload validation checks
"""
import os

from typing import List, Iterable, Tuple, Optional, Literal

import nibabel as nib
import numpy as np

from nibabel.cifti2.cifti2_axes import BrainModelAxis

from findviz.viz.io import utils


def validate_cii_brainmodel_axis(cifti_img: nib.Cifti2Image) -> bool:
    """
    Validate that the cifti image has a brainmodel axis
    """
    axes = [cifti_img.header.get_axis(i) for i in range(cifti_img.ndim)]
    return any(isinstance(axis, BrainModelAxis) for axis in axes)
    

def validate_cii_dtseries_ext(fp: str) -> bool:
    """
    validate uploaded cifti dtseries file extension (dtseries.nii)
    """
    base, ext = os.path.splitext(fp)
    if ext == '.nii':
        base, ext = os.path.splitext(base)
        if ext == '.dtseries':
            return True
        else:
            return False
    else:
        return False


def validate_cii_file_inputs(
    dtseries: Optional[str] = None,
    left_mesh: Optional[str] = None,
    right_mesh: Optional[str] = None
) -> Tuple[str, bool]:
    """
    validate uploaded cifti file inputs
    """
    msg = ''
    checks_pass = True
    
    # check if dtseries file is valid
    if dtseries is None:
        msg = 'A dtseries.nii file must be provided'
        checks_pass = False
    
    # check if left mesh file is valid
    if (left_mesh is None) and (right_mesh is None):
        msg = 'A left or right hemisphere mesh file must be provided'
        checks_pass = False
    
    return msg, checks_pass


def validate_cii_hemisphere(
    brain_model_axis: BrainModelAxis,
    hemisphere: Literal['left', 'right'],
    axis_key: str
) -> bool:
    """
    Validate that the cifti image has a brainmodel axis for the left or right hemisphere
    """
    for axis in brain_model_axis.iter_structures():
        if axis[0] == axis_key:
            return True
    return False


def validate_gii_func_ext(fp: str) -> bool:
    """
    validate uploaded gifti functional file extension (func.gii)
    """
    base, ext = os.path.splitext(fp)
    if ext == '.gii':
        base, ext = os.path.splitext(base)
        if ext == '.func':
            return True
        else:
            return False
    else:
        return False


def validate_gii_mesh_ext(fp: str) -> bool:
    """
    validate uploaded gifti mesh file extension (surf.gii)
    """
    base, ext = os.path.splitext(fp)
    if ext == '.gii':
        base, ext = os.path.splitext(base)
        if ext == '.surf':
            return True
        else:
            return False
    else:
        return False

def validate_gii_file_inputs(
    left_mesh, 
    right_mesh,
    left_func, 
    right_func
) -> Tuple[str, List[str], bool]:
    """
    Take left and right hemisphere mesh (surf.gii) and functional (func.gii)
    files and ensure the appropriate file inputs
    return a tuple of (error message, missing files, checks pass)

    """
    # initialize error message and pass state
    msg = ''
    missing = []
    checks_pass = True
    if (left_func is None) and (right_func is None):
        msg =  'A left or right hemisphere functional file must be provided'
        missing = ['left_func', 'right_func']
        checks_pass = False

    if (left_mesh is None) and (right_mesh is None):
        msg = 'A left or right hemisphere mesh file must be provided'
        missing = ['left_mesh', 'right_mesh']
        checks_pass = False

    if (right_func is None) and (right_mesh is not None):
        msg = 'A right hemisphere func file must be provided with mesh input'
        missing = ['right_func']
        checks_pass = False
        
    if (right_func is not None) and (right_mesh is None):
        msg = 'A right hemisphere mesh file must be provided with func input'
        missing = ['right_mesh']
        checks_pass = False

    if (left_func is None) and (left_mesh is not None):
        msg = 'A left hemisphere func file must be provided with mesh input'
        missing = ['left_func']
        checks_pass = False

    if (left_func is not None) and (left_mesh is None):
        msg = 'A left hemisphere mesh file must be provided with func input'
        missing = ['left_mesh']
        checks_pass = False
    
    return msg, missing, checks_pass


def validate_gii_func(gii: nib.GiftiImage) -> bool:
    """
    Validate that gifti functional file (func.gii) has a 1d-array per 
    timepoint (data array).
    """
    for darray in gii.darrays:
        if len(np.squeeze(darray.data).shape) > 1:
            return False
    return True

def validate_gii_func_mesh_len(
    gii_func: nib.GiftiImage, 
    gii_mesh: nib.GiftiImage
) -> bool:
    """
    Validate that gifti functional file (func.gii) has the same number of 
    time courses as the number of vertices in the mesh file (surf.gii).
    """
    return len(gii_func.darrays[0].data) == len(gii_mesh.darrays[0].data)

def validate_gii_mesh(gii: nib.GiftiImage) -> bool:
    """
    The gifti mesh (geometry) file should only contain two data arrays,
    coresponding to coordinates and faces arrays .
    """
    return len(gii.darrays) == 2


def validate_gii_func_len(
    gii_lh: nib.GiftiImage, 
    gii_rh: nib.GiftiImage
) -> bool:
    """
    validate that gifti functionals from left and right hemisphere
    are equal length
    """
    return len(gii_lh.darrays) == len(gii_rh.darrays)


def validate_nii_ext(fp: str) -> bool:
    """
    validate uploaded nifti file extension (either .nii or .nii.gz)
    """
    # get file extension
    ext = utils.parse_nifti_file_ext(fp)
    # if not nifti file, raise error
    if ext is None:
        return False
    return True


def validate_nii_4d(nii: nib.Nifti1Image) -> bool:
    """
    Validate that nii is 4-dimensional. This is required for functional files.
    """
    if len(nii.shape) != 4:
        return False
    else:
        return True


def validate_nii_3d(nii: nib.Nifti1Image) -> bool:
    """
    Validate nii file is 3-dimensional (not 4). This is required for anatomical
    and mask files.
    """
    if len(nii.shape) != 3:
        return False
    else:
        return True


def validate_nii_same_dim_len(nii: nib.Nifti1Image, nii_ref: nib.Nifti1Image) -> bool:
    """
    Ensure the first 3 voxel-dimensions of nifti file (nii) are the same 
    length as a reference nifti file (nii_ref)
    """
    return np.array_equal(nii.shape[:3], nii_ref.shape[:3])


def validate_nii_brain_mask(nii_mask: nib.Nifti1Image) -> bool:
    """
    Ensure that the nifti brain mask only contains 0 and 1s
    """
    # Get the data array
    data_mask = nii_mask.get_fdata()
    # Check unique values in the array only have 0s and 1s
    unique_values = np.unique(data_mask)
    return np.array_equal(unique_values, [0, 1])
    

def validate_task_ext(fp: str) -> bool:
    """
    validate task design file extension (.csv or .tsv)
    """
    base, ext = os.path.splitext(fp)
    if ext == '.csv':
        return True
    elif ext == '.tsv':
        return True
    else:
        return False


def validate_task_header_required_cols(
    header: List[str],
    required_cols: List[str]
) -> bool:
    """
    validate task design file header has necessary columns.
    It must have two columns: 'onset' or 'duration'.
    It could also have a 'task_trial' column. Case-insensitive.
    """
    # lower case all header columns
    header = [col.strip().lower() for col in header]
    missing_cols = [col for col in required_cols 
                    if col.strip().lower() not in header]
    if len(missing_cols) > 0:
        return False

    return True


def validate_task_header_duplicates(
    header: List[str],
    required_cols: List[str]
) -> bool:
    """
    Ensure there are not duplicates of required columns
    """
    # Check for duplicates only among required columns
    duplicate_cols = [
        col for col in required_cols if header.count(col) > 1
    ]
    if len(duplicate_cols) > 0:
        return False

    return True


def validate_task_tr(tr: float) -> bool:
    """
    validate TR (repetition time) is not negative or 0
    """
    if tr <= 0:
        return False
    return True


def validate_task_slicetime(slicetime: float) -> bool:
    """
    validate slicetime reference value is between 0 and 1
    """
    if slicetime > 1:
        return False
    elif slicetime < 0:
        return False
    return True


def validate_ts_task_length(ts_list: Iterable[List]) -> bool:
    """
    Take a time course list and validate there is at least one row in the
    ts or task design file.
    """
    row_count = len(ts_list)
    if row_count < 1:
        return False
    else:
        return True


def validate_ts_ext(fp: str) -> bool:
    """
    validate time course file extension (.csv or .txt)
    """
    base, ext = os.path.splitext(fp)
    if ext == '.csv':
        return True
    elif ext == '.txt':
        return True
    else:
        return False


def validate_ts_single_col(row: List) -> bool:
    """
    validate that time course has a single column
    """
    if len(row) > 1:
        return False
    return True


def validate_ts_numeric(element) -> bool:
    """
    validate that time course element is numeric
    """
    # try convert to number, if exception, return failed validation
    try:
        float(element)
    except ValueError:
        return False
    return True

def validate_ts_fmri_length(
        fmri_len: int,
        ts: np.ndarray
) -> bool:
    """
    Validate that the length of the fmri time course length matches 
    that the length of the time course. 
    """
    
    return len(ts) == fmri_len









