"""
Utilities for handling gifti file uploads
"""
from enum import Enum
from pathlib import Path
from typing import Literal, Optional, Dict, Union

import nibabel as nib

from flask import request
from werkzeug.datastructures import FileStorage

from findviz.viz import exception
from findviz.viz.io import utils
from findviz.viz.io import validate

# Type aliases
FilePath = Union[str, Path]
FileUploadDict = Dict[str, Optional[Union[FilePath, 'FileStorage']]]
GiftiDict = Dict[str, Optional[nib.GiftiImage]]

# Expected file upload inputs
class GiftiFiles(Enum):
    LEFT_FUNC = 'left_gii_func'
    RIGHT_FUNC = 'right_gii_func'
    LEFT_MESH = 'left_gii_mesh'
    RIGHT_MESH = 'right_gii_mesh'

# gifti form fields in upload modal
browser_fields: Dict[str, str] = {
    GiftiFiles.LEFT_FUNC.value: 'left-hemisphere-gifti-func',
    GiftiFiles.RIGHT_FUNC.value: 'right-hemisphere-gifti-func',
    GiftiFiles.LEFT_MESH.value: 'left-hemisphere-gifti-mesh',
    GiftiFiles.RIGHT_MESH.value: 'right-hemisphere-gifti-mesh'
}


class GiftiUpload:
    """
    Class for handling gifti file uploads.

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
        fmri_files: Optional[Dict[str, Union[str, Path]]] = None,
    ) -> GiftiDict:
        """
        Get and validate gifti files uploaded from cli or browser.

        Parameters
        ----------
        fmri_files : Optional[Dict[str, FilePath]]
            Dictionary of Gifti file paths: 
            {'left_gii_func': path, 'right_gii_func': path, 'left_gii_mesh': path, 'right_gii_mesh': path}

        Returns
        -------
        GiftiDict
            Dictionary containing validated Nifti images

        Raises
        ------
        FileInputError
            If required files are missing or have invalid extensions
        FileUploadError
            If there are issues reading the files
        FileValidationError
            If files fail validation checks
        """
        if self.method == 'cli':
            file_uploads = fmri_files
        elif self.method == 'browser':
            file_uploads = self._get_browser_input()

        # check file uploads
        self._check_file_inputs(file_uploads)

        # store whether left and/or right files were uploaded
        if file_uploads[GiftiFiles.LEFT_FUNC.value] is None:
            self.left_input = False
        else:
            self.left_input = True

        if file_uploads[GiftiFiles.RIGHT_FUNC.value] is None:
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

        # Process left hemisphere inputs
        if self.left_input:
            # load and validate left functional file
            # check left functional file extension
            if not validate.validate_gii_func_ext(
                utils.get_filename(file_uploads[GiftiFiles.LEFT_FUNC.value])
            ):
                raise exception.FileInputError(
                    'File extension is not recognized. Please upload '
                    'a gifti file with a .func.gii extension for left '
                    'hemisphere functional file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[GiftiFiles.LEFT_FUNC.value]]
                )
            try:
                gii_left_func = read_gii(
                    file_uploads[GiftiFiles.LEFT_FUNC.value], 
                    self.method
                )
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading left functional gifti file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[GiftiFiles.LEFT_FUNC.value]]
                ) from e
            
            if not validate.validate_gii_func(gii_left_func):
                raise exception.FileValidationError(
                    "The left hemisphere func.gii file should have have 1d-array "
                    "per data array (timepoint). Check format.",
                    validate.validate_gii_func.__name__,
                    exception.ExceptionFileTypes.GIFTI.value,
                    [browser_fields[GiftiFiles.LEFT_FUNC.value]]
                )
            
            gifti_out[GiftiFiles.LEFT_FUNC.value] = gii_left_func

            # load and validate left mesh
            # check left mesh file extension
            if not validate.validate_gii_mesh_ext(
                utils.get_filename(file_uploads[GiftiFiles.LEFT_MESH.value])
            ):
                raise exception.FileInputError(
                    'File extension is not recognized. Please upload '
                    'a gifti file with a .surf.gii extension for left '
                    'hemisphere mesh (geometry) file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[GiftiFiles.LEFT_MESH.value]]
                )
            try:
                gii_left_mesh = read_gii(
                    file_uploads[GiftiFiles.LEFT_MESH.value], 
                    self.method
                )
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading left hemisphere mesh (geometry) gifti file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method,
                    [browser_fields[GiftiFiles.LEFT_MESH.value]]
                ) from e
            
            if not validate.validate_gii_mesh(gii_left_mesh):
                raise exception.FileValidationError(
                    "The left hemisphere mesh (geometry) file should only contain "
                    "two data arrays, corresponding to coordinate and face arrays."
                     " Check format.",
                    validate.validate_gii_mesh.__name__,
                    exception.ExceptionFileTypes.GIFTI.value,
                    [browser_fields[GiftiFiles.LEFT_MESH.value]]
                )
            
            gifti_out[GiftiFiles.LEFT_MESH.value] = gii_left_mesh

            # check length of functional and mesh files
            if not validate.validate_gii_func_mesh_len(gii_left_func, gii_left_mesh):
                raise exception.FileValidationError(
                    f"The left hemisphere func.gii file and mesh (geometry) file "
                    f"are not the same length - {len(gii_left_func.darrays[0].data)} != "
                    f"{len(gii_left_mesh.darrays[0].data)}. Check files are consistent "
                    "in length.",
                    validate.validate_gii_func_mesh_len.__name__,
                    exception.ExceptionFileTypes.GIFTI.value,
                    [
                        browser_fields[GiftiFiles.LEFT_FUNC.value], 
                        browser_fields[GiftiFiles.LEFT_MESH.value]
                    ]
                )

            # Process right hemisphere inputs
            if self.right_input:
                # check left functional file extension
                if not validate.validate_gii_func_ext(
                    utils.get_filename(file_uploads[GiftiFiles.RIGHT_FUNC.value])
                ):
                    raise exception.FileInputError(
                        'File extension is not recognized. Please upload '
                        'a gifti file with a .func.gii extension for right '
                        'hemisphere functional file',
                        exception.ExceptionFileTypes.GIFTI.value, self.method,
                        [browser_fields[GiftiFiles.RIGHT_FUNC.value]]
                    )
                # load and validate right functional file
                try:
                    gii_right_func = read_gii(
                        file_uploads[GiftiFiles.RIGHT_FUNC.value], 
                        self.method
                    )
                except Exception as e:
                    raise exception.FileUploadError(
                        'Error in reading right functional gifti file',
                        exception.ExceptionFileTypes.GIFTI.value, self.method,
                        [browser_fields[GiftiFiles.RIGHT_FUNC.value]]
                    ) from e
                
                if not validate.validate_gii_func(gii_right_func):
                    raise exception.FileValidationError(
                        "The right hemisphere func.gii file should have have 1d-array "
                        "per data array (timepoint). Check format.",
                        validate.validate_gii_func.__name__,
                        exception.ExceptionFileTypes.GIFTI.value,
                        [browser_fields[GiftiFiles.RIGHT_FUNC.value]]
                    )
                
                gifti_out[GiftiFiles.RIGHT_FUNC.value] = gii_right_func

                # load and validate right mesh
                # check right mesh file extension
                if not validate.validate_gii_mesh_ext(
                    utils.get_filename(file_uploads[GiftiFiles.RIGHT_MESH.value])
                ):
                    raise exception.FileInputError(
                        'File extension is not recognized. Please upload '
                        'a gifti file with a .surf.gii extension for right '
                        'hemisphere mesh (geometry) file',
                        exception.ExceptionFileTypes.GIFTI.value, self.method,
                        [browser_fields[GiftiFiles.RIGHT_MESH.value]]
                    )
                try:
                    gii_right_mesh = read_gii(
                        file_uploads[GiftiFiles.RIGHT_MESH.value], 
                        self.method
                    )
                except Exception as e:
                    raise exception.FileUploadError(
                        'Error in reading right hemisphere mesh (geometry) gifti file',
                        exception.ExceptionFileTypes.GIFTI.value, self.method,
                        [browser_fields[GiftiFiles.RIGHT_MESH.value]]
                    ) from e
                
                if not validate.validate_gii_mesh(gii_right_mesh):
                    raise exception.FileValidationError(
                        "The right hemisphere mesh (geometry) file should only contain "
                        "two data arrays, corresponding to coordinate and face arrays."
                        " Check format.",
                        validate.validate_gii_mesh.__name__,
                        exception.ExceptionFileTypes.GIFTI,
                        [browser_fields[GiftiFiles.RIGHT_MESH.value]]
                    )
            
                gifti_out[GiftiFiles.RIGHT_MESH.value] = gii_left_mesh

            # check length of functional and mesh files
            if not validate.validate_gii_func_mesh_len(gii_left_func, gii_left_mesh):
                raise exception.FileValidationError(
                    f"The right hemisphere func.gii file and mesh (geometry) file "
                    f"are not the same length - {len(gii_right_func.darrays[0].data)} != "
                    f"{len(gii_right_mesh.darrays[0].data)}. Check files are consistent "
                    "in length.",
                    validate.validate_gii_func_mesh_len.__name__,
                    exception.ExceptionFileTypes.GIFTI.value,
                    [
                        browser_fields[GiftiFiles.RIGHT_FUNC.value], 
                        browser_fields[GiftiFiles.RIGHT_MESH.value]
                    ]
                )
            
            # if left and right hemispheres passed, check length is consistent
            if self.left_input & self.right_input:
                if not validate.validate_gii_func_len(gii_left_func, gii_right_func):
                    raise exception.FileValidationError(
                        "The left and right hemisphere func.gii files are "
                        "not the same length. Check files are consistent in length.",
                        validate.validate_gii_func_len.__name__,
                        exception.ExceptionFileTypes.GIFTI.value,
                        [
                            browser_fields[GiftiFiles.LEFT_FUNC.value], 
                            browser_fields[GiftiFiles.RIGHT_FUNC.value]
                        ]
                    )
            return gifti_out

    def _check_file_inputs(self, file_inputs: FileUploadDict) -> None:
        """
        Check left and right hemisphere file uploads.

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
        left_func = file_inputs[GiftiFiles.LEFT_FUNC.value]
        right_func = file_inputs[GiftiFiles.RIGHT_FUNC.value]
        left_mesh = file_inputs[GiftiFiles.LEFT_MESH.value]
        right_mesh = file_inputs[GiftiFiles.RIGHT_MESH.value]

        msg, passed = validate.validate_gii_file_inputs(
            left_mesh, 
            right_mesh, 
            left_func, 
            right_func
        )
        # raise file validation error if file inputs incorrect
        if not passed:
            raise exception.FileValidationError(
                msg, exception.ExceptionFileTypes.GIFTI.value, self.method,
                [
                    browser_fields[GiftiFiles.LEFT_FUNC.value], 
                    browser_fields[GiftiFiles.RIGHT_FUNC.value],
                    browser_fields[GiftiFiles.LEFT_MESH.value],
                    browser_fields[GiftiFiles.RIGHT_MESH.value],
                ]
            )

    @staticmethod
    def _get_browser_input() -> FileUploadDict:
        """
        Get file uploads from browser request.

        Returns
        -------
        FileUploadDict
            Dictionary containing file upload objects
        """
        left_func_file = request.files.get(GiftiFiles.LEFT_FUNC.value)
        right_func_file = request.files.get(GiftiFiles.RIGHT_FUNC.value)
        left_mesh_file = request.files.get(GiftiFiles.LEFT_MESH.value)
        right_mesh_file = request.files.get(GiftiFiles.RIGHT_MESH.value)

        file_upload = {
            GiftiFiles.LEFT_FUNC.value: left_func_file,
            GiftiFiles.RIGHT_FUNC.value: right_func_file,
            GiftiFiles.LEFT_MESH.value: left_mesh_file,
            GiftiFiles.RIGHT_MESH.value: right_mesh_file
        }
        return file_upload


def read_gii(
    file: Union[FilePath, FileStorage],
    method: Literal['cli', 'browser']
) -> nib.GiftiImage:
    """
    Read gifti file based on method of upload.

    Parameters
    ----------
    file : Union[FilePath, FileStorage]
        Either a gifti file from the browser or full path to file from CLI
    method : Literal['cli', 'browser']
        Whether the file was uploaded through browser or CLI

    Returns
    -------
    nib.GiftiImage
        Loaded nibabel image

    Raises
    ------
    Exception
        If there are issues reading the file
    """
    if method =='cli':
        try:
            gifti_img = nib.load(file)
        # raise generic exception to be handled higher in stack
        except Exception as e:
            raise e
    elif method == 'browser':
        try:
            file_bytes = file.read()
            gifti_img = nib.GiftiImage.from_bytes(file_bytes)
        except Exception as e:
            raise e
        
    return gifti_img
