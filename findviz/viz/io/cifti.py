"""
Utilities for handling cifti file uploads. The left and/or right hemisphere
time series from the dtseries.nii file is converted to gifti files 
for visualization.
"""

from enum import Enum
from pathlib import Path
from typing import Literal, Optional, Dict, Union

import nibabel as nib
import numpy as np

from flask import request
from nibabel.cifti2.cifti2_axes import BrainModelAxis
from werkzeug.datastructures import FileStorage

from findviz.viz import exception
from findviz.viz.io import utils
from findviz.viz.io import validate
from findviz.viz.io.gifti import read_gii, GiftiDict, GiftiFiles
from findviz.viz.transforms import array_to_gifti

# Type aliases
FilePath = Union[str, Path]
FileUploadDict = Dict[str, Optional[Union[FilePath, 'FileStorage']]]

# Expected file upload inputs
class CiftiFiles(Enum):
    DTSERIES = 'cifti_dtseries'
    LEFT_MESH = 'left_gii_mesh'
    RIGHT_MESH = 'right_gii_mesh'

# Browser fields type definition
browser_fields: Dict[str, str] = {
    CiftiFiles.DTSERIES.value: 'cifti-dtseries',
    CiftiFiles.LEFT_MESH.value: 'cifti-surf-left',
    CiftiFiles.RIGHT_MESH.value: 'cifti-surf-right'
}

# Cifti left/right hemisphere axis keys
CIFTI_LEFT_CORTEX = 'CIFTI_STRUCTURE_CORTEX_LEFT'
CIFTI_RIGHT_CORTEX = 'CIFTI_STRUCTURE_CORTEX_RIGHT'

class CiftiUpload:
    """
    Class for handling cifti file uploads.

    Attributes
    ----------
    method : Literal['cli', 'browser']
        The method used for file uploads
    """

    def __init__(
        self,
        method: Literal['cli', 'browser']
    ):
        if method not in ['cli', 'browser']:
            raise ValueError('unrecognized upload method')
        self.method = method

    def upload(
        self,
        fmri_files: Optional[FileUploadDict] = None
    ) -> GiftiDict:
        """
        Upload cifti files

        Parameters
        ----------
        fmri_files : Optional[Dict[str, FilePath]]
            Dictionary of Cifti file paths: 
            {'cifti_dtseries': path, 'left_gii_mesh': path, 'right_gii_mesh': path}
        """
        if self.method == 'cli':
            file_uploads = fmri_files
        elif self.method == 'browser':
            file_uploads = self._get_browser_input()
        
        # check file uploads
        self._check_file_inputs(file_uploads)

        # store whether left and/or right files were uploaded
        if file_uploads[CiftiFiles.LEFT_MESH.value] is None:
            self.left_input = False
        else:
            self.left_input = True

        if file_uploads[CiftiFiles.RIGHT_MESH.value] is None:
            self.right_input = False
        else:
            self.right_input = True
        
        # Initialize output dictionary
        gifti_out = {
            GiftiFiles.LEFT_FUNC.value: None,
            GiftiFiles.RIGHT_FUNC.value: None,
            GiftiFiles.LEFT_MESH.value: None,
            GiftiFiles.RIGHT_MESH.value: None
        }

        # Process dtseries file
        # check dtseries file extension
        if not validate.validate_cii_dtseries_ext(
            utils.get_filename(file_uploads[CiftiFiles.DTSERIES.value])
        ):
            raise exception.FileInputError(
                'File extension is not recognized. Please upload '
                'a cifti file with a .dtseries.nii extension',
                exception.ExceptionFileTypes.CIFTI.value, self.method,
                [browser_fields[CiftiFiles.DTSERIES.value]]
            )
        
        # load and validate dtseries file
        try:
            cifti_img = read_cifti(
                file_uploads[CiftiFiles.DTSERIES.value],
                self.method
            )
            # check if dtseries cifti file has a brainmodel axis
            if not validate.validate_cii_brainmodel_axis(cifti_img):
                raise exception.FileValidationError(
                    'Cifti file does not have a brainmodel axis',
                    validate.validate_cii_brainmodel_axis.__name__,
                    exception.ExceptionFileTypes.CIFTI,
                    [browser_fields[CiftiFiles.DTSERIES.value]]
                )
        except Exception as e:
            raise exception.FileUploadError(
                'Error in reading dtseries cifti file',
                exception.ExceptionFileTypes.CIFTI.value, self.method,
                [browser_fields[CiftiFiles.DTSERIES.value]]
            ) from e

        # Process left hemisphere mesh and extract time series from dtseries file
        if self.left_input:
            if not validate.validate_gii_mesh_ext(
                utils.get_filename(file_uploads[CiftiFiles.LEFT_MESH.value])
            ):
                raise exception.FileInputError(
                    'File extension is not recognized. Please upload '
                    'a gifti file with a .surf.gii extension for left '
                    'hemisphere mesh (geometry) file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[CiftiFiles.LEFT_MESH.value]]
                )
            try:
                gii_left_mesh = read_gii(
                    file_uploads[CiftiFiles.LEFT_MESH.value], 
                    self.method
                )
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading left hemisphere mesh (geometry) gifti file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[CiftiFiles.LEFT_MESH.value]]
                ) from e
                
            if not validate.validate_gii_mesh(gii_left_mesh):
                raise exception.FileValidationError(
                    "The left hemisphere mesh (geometry) file should only contain "
                    "two data arrays, corresponding to coordinate and face arrays."
                    " Check format.",
                    validate.validate_gii_mesh.__name__,
                    exception.ExceptionFileTypes.GIFTI,
                    [browser_fields[CiftiFiles.LEFT_MESH.value]]
                )
            
            gifti_out[GiftiFiles.LEFT_MESH.value] = gii_left_mesh

            # extract left hemisphere time series from dtseries file
            try:
                cifti_left = select_hemisphere_cifti(
                    cifti_img,
                    'left'
                )
                # convert to gifti
                gifti_out[GiftiFiles.LEFT_FUNC.value] = array_to_gifti(
                    cifti_left,
                    both_hemispheres=False
                )
            except exception.FileValidationError as e:
                raise e
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in extracting left hemisphere time series from dtseries file',
                    exception.ExceptionFileTypes.CIFTI.value, self.method,
                    [browser_fields[CiftiFiles.DTSERIES.value]]
                ) from e
            
            # check length of functional and mesh files
            if not validate.validate_gii_func_mesh_len(
                gifti_out[GiftiFiles.LEFT_FUNC.value],
                gifti_out[GiftiFiles.LEFT_MESH.value]
            ):
                raise exception.FileValidationError(
                    "The left hemisphere time course from the dtseries.nii file and mesh (geometry) file "
                    f"are not the same length - {len(gifti_out[GiftiFiles.LEFT_FUNC.value].darrays[0].data)} != "
                    f"{len(gifti_out[GiftiFiles.LEFT_MESH.value].darrays[0].data)}. Check files are consistent "
                    "in length.",
                    validate.validate_gii_func_mesh_len.__name__,
                    exception.ExceptionFileTypes.GIFTI.value,
                    [
                        browser_fields[CiftiFiles.DTSERIES.value], 
                        browser_fields[CiftiFiles.LEFT_MESH.value]
                    ]
                )
        
        # Process right hemisphere mesh file
        if self.right_input:
            if not validate.validate_gii_mesh_ext(
                utils.get_filename(file_uploads[CiftiFiles.RIGHT_MESH.value])
            ):
                raise exception.FileInputError(
                    'File extension is not recognized. Please upload '
                    'a gifti file with a .surf.gii extension for right '
                    'hemisphere mesh (geometry) file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[CiftiFiles.RIGHT_MESH.value]]
                )
                
            try:
                gii_right_mesh = read_gii(
                    file_uploads[CiftiFiles.RIGHT_MESH.value],
                    self.method
                )
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading right hemisphere mesh (geometry) gifti file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[CiftiFiles.RIGHT_MESH.value]]
                ) from e
                
            if not validate.validate_gii_mesh(gii_right_mesh):
                raise exception.FileValidationError(
                    "The right hemisphere mesh (geometry) file should only contain "
                    "two data arrays, corresponding to coordinate and face arrays."
                    " Check format.",   
                    validate.validate_gii_mesh.__name__,
                    exception.ExceptionFileTypes.GIFTI,
                    [browser_fields[CiftiFiles.RIGHT_MESH.value]]
                )
            
            gifti_out[GiftiFiles.RIGHT_MESH.value] = gii_right_mesh
            
            # extract right hemisphere time series from dtseries file
            try:
                cifti_right = select_hemisphere_cifti(
                    cifti_img,
                    'right'
                )
                # convert to gifti
                gifti_out[GiftiFiles.RIGHT_FUNC.value] = array_to_gifti(
                    cifti_right,
                    both_hemispheres=False
                )
            except exception.FileValidationError as e:
                raise e
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in extracting right hemisphere time series from dtseries file',
                    exception.ExceptionFileTypes.CIFTI.value, self.method,
                    [browser_fields[CiftiFiles.DTSERIES.value]]
                ) from e
            
            # check length of functional and mesh files
            if not validate.validate_gii_func_mesh_len(
                gifti_out[GiftiFiles.RIGHT_FUNC.value],
                gifti_out[GiftiFiles.RIGHT_MESH.value]
            ):
                raise exception.FileValidationError(
                    "The right hemisphere time course from the dtseries.nii file and mesh (geometry) file "
                    f"are not the same length - {len(gifti_out[GiftiFiles.RIGHT_FUNC.value].darrays[0].data)} != "
                    f"{len(gifti_out[GiftiFiles.RIGHT_MESH.value].darrays[0].data)}. Check files are consistent "
                    "in length.",
                    validate.validate_gii_func_mesh_len.__name__,
                    exception.ExceptionFileTypes.GIFTI.value,
                    [
                        browser_fields[CiftiFiles.DTSERIES.value], 
                        browser_fields[CiftiFiles.RIGHT_MESH.value]
                    ]
                )
        
        return gifti_out
    
    @staticmethod
    def _get_browser_input() -> FileUploadDict:
        """
        Get file uploads from browser request.

        Returns
        -------
        FileUploadDict
            Dictionary containing file upload objects
        """
        dtseries_file = request.files.get(CiftiFiles.DTSERIES.value)
        left_mesh_file = request.files.get(CiftiFiles.LEFT_MESH.value)
        right_mesh_file = request.files.get(CiftiFiles.RIGHT_MESH.value)

        file_upload = {
            CiftiFiles.DTSERIES.value: dtseries_file,
            CiftiFiles.LEFT_MESH.value: left_mesh_file,
            CiftiFiles.RIGHT_MESH.value: right_mesh_file
        }
        return file_upload
    
    def _check_file_inputs(self, file_inputs: FileUploadDict) -> None:
        """
        Check cifti file inputs.

        Parameters
        ----------
        file_inputs : FileUploadDict
            Dictionary containing file uploads

        Raises
        ------
        FileValidationError
            If file inputs are incorrect or inconsistent
        """
        # get files from dict
        dtseries = file_inputs[CiftiFiles.DTSERIES.value]
        left_mesh = file_inputs[CiftiFiles.LEFT_MESH.value]
        right_mesh = file_inputs[CiftiFiles.RIGHT_MESH.value]

        msg, passed = validate.validate_cii_file_inputs(
            dtseries, 
            left_mesh, 
            right_mesh
        )
        # raise file validation error if file inputs incorrect
        if not passed:
            raise exception.FileValidationError(
                msg, exception.ExceptionFileTypes.CIFTI.value, self.method,
                [
                    browser_fields[CiftiFiles.DTSERIES.value], 
                    browser_fields[CiftiFiles.LEFT_MESH.value],
                    browser_fields[CiftiFiles.RIGHT_MESH.value],
                ]
            )


def read_cifti(
    file: Union[FilePath, FileStorage],
    method: Literal['cli', 'browser']
) -> nib.Cifti2Image:
    """
    Read dense time series cifti (dtseries.nii) file

    Parameters
    ----------
    file : Union[FilePath, FileStorage]
        Path to cifti file
    method : Literal['cli', 'browser']
    """
    if method =='cli':
        try:
            cifti_img = nib.load(file)
        # raise generic exception to be handled higher in stack
        except Exception as e:
            raise e
    elif method == 'browser':
        try:
            file_bytes = file.read()
            cifti_img = nib.Cifti2Image.from_bytes(file_bytes)
        except Exception as e:
            raise e
    
    return cifti_img


def select_hemisphere_cifti(
    cifti_img: nib.Cifti2Image,
    hemisphere: Literal['left', 'right']
) -> np.ndarray:
    """
    Get hemisphere time series from cifti file

    Parameters
    ----------
    cifti_img : nib.Cifti2Image
        Cifti image
    hemisphere : Literal['left', 'right']
        Hemisphere to extract time series from

    Returns
    -------
    np.ndarray
        Time series data

    Raises
    ------
    ValueError
        If hemisphere is not left or right
    FileValidationError
        If cifti image has more than one brainmodel axis
    """
    # get index of brain model axis (previously validated)
    brain_model_idx = [
        i for i in range(cifti_img.ndim) 
        if isinstance(cifti_img.header.get_axis(i), BrainModelAxis)
    ]
    # check if cifti image has more than one brainmodel axis
    if len(brain_model_idx) > 1:
        raise exception.FileValidationError(
            'Cifti dtseries.nii file has more than one brainmodel axis',
            validate.validate_cii_brainmodel_axis.__name__,
            exception.ExceptionFileTypes.CIFTI,
            [browser_fields[CiftiFiles.DTSERIES.value]]
        )
    # get axis key for hemisphere
    if hemisphere == 'left':
        axis_key = CIFTI_LEFT_CORTEX
    elif hemisphere == 'right':
        axis_key = CIFTI_RIGHT_CORTEX
    else:
        raise ValueError('Hemisphere must be either left or right')
    
    # iterate through brain model axis and check if left or right hemisphere axis key matches
    brain_model_axis = cifti_img.header.get_axis(brain_model_idx[0])
    if not validate.validate_cii_hemisphere(
        brain_model_axis,
        hemisphere,
        axis_key
    ):
        raise exception.FileValidationError(
            f'Cifti dtseries.nii file does not have a brainmodel axis for the {hemisphere} '
            f'hemisphere - {axis_key}',
            validate.validate_cii_hemisphere.__name__,
            exception.ExceptionFileTypes.CIFTI,
            [browser_fields[CiftiFiles.DTSERIES.value]]
        )
    # get index of hemisphere time series
    hemisphere_model = [
        bm for bm in brain_model_axis.iter_structures()
        if bm[0] == axis_key
    ][0]
    # slice cifti image to get hemisphere time series
    cifti_data = cifti_img.get_fdata()[:, hemisphere_model[1]]
    # get vertex indices (excludes medial wall)
    vertex_indx = hemisphere_model[2].vertex
    # initialize time series array
    hemisphere_data = np.zeros(
        (vertex_indx.max() + 1, cifti_data.shape[0]),
        dtype=cifti_data.dtype
    ).T
    # iterate through time series and copy data to ts_data
    hemisphere_data[:, vertex_indx] = cifti_data
    # transpose to time points along rows
    return hemisphere_data