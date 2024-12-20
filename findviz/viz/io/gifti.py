"""
Utilities for handling gifti file uploads
"""
from enum import Enum
from typing import Literal

import nibabel as nib

from flask import request

from findviz.viz import exception
from findviz.viz.io import validate

# Expected file upload inputs
class GiftiFiles(Enum):
    LEFT_FUNC = 'left_gii_func'
    RIGHT_FUNC = 'right_gii_func'
    LEFT_MESH = 'left_gii_mesh'
    RIGHT_MESH = 'right_gii_mesh'


class GiftiUpload:
    """
    Class for handling gifti file uploads.

    Attributes:
        method (str): The method used for file uploads (cli , browser)
    """

    def __init__(
        self,
        method: Literal['cli', 'browser']
    ):
        if method not in ['cli', 'browser']:
            raise ValueError('unrecognized upload method')
        self.method = method

    def upload(self) -> dict:
        """
        Get gifti file inputs from cli or browser

        Returns:
        dict: uploaded files
        """
        if self.method == 'cli':
            file_uploads = self._get_cli_input()
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
            try:
                gii_left_func = read_gii(
                    file_uploads[GiftiFiles.LEFT_FUNC.value], 
                    self.method
                )
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading left functional gifti file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method
                ) from e
            
            if not validate.validate_gii_func(gii_left_func):
                raise exception.FileValidationError(
                    "The left hemisphere func.gii file should have have 1d-array "
                    "per data array (timepoint). Check format.",
                    validate.validate_gii_func.__name__,
                    exception.ExceptionFileTypes.GIFTI.value
                )
            
            gifti_out[GiftiFiles.LEFT_FUNC.value] = gii_left_func

            # load and validate left mesh
            try:
                gii_left_mesh = read_gii(
                    file_uploads[GiftiFiles.LEFT_MESH.value], 
                    self.method
                )
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading left hemisphere mesh (geometry) gifti file',
                    exception.ExceptionFileTypes.GIFTI.value, self.method
                ) from e
            
            if not validate.validate_gii_mesh(gii_left_mesh):
                raise exception.FileValidationError(
                    "The left hemisphere mesh (geometry) file should only contain "
                    "two data arrays, corresponding to coordinate and face arrays."
                     " Check format.",
                    validate.validate_gii_mesh.__name__,
                    exception.ExceptionFileTypes.GIFTI.value
                )
            
            gifti_out[GiftiFiles.LEFT_MESH.value] = gii_left_mesh

            # Process right hemisphere inputs
            if self.right_input:
                # load and validate right functional file
                try:
                    gii_right_func = read_gii(
                        file_uploads[GiftiFiles.RIGHT_FUNC.value], 
                        self.method
                    )
                except Exception as e:
                    raise exception.FileUploadError(
                        'Error in reading right functional gifti file',
                        exception.ExceptionFileTypes.GIFTI.value, self.method
                    ) from e
                
                if not validate.validate_gii_func(gii_right_func):
                    raise exception.FileValidationError(
                        "The right hemisphere func.gii file should have have 1d-array "
                        "per data array (timepoint). Check format.",
                        validate.validate_gii_func.__name__,
                        exception.ExceptionFileTypes.GIFTI.value
                    )
                
                gifti_out[GiftiFiles.RIGHT_FUNC.value] = gii_right_func

                # load and validate right mesh
                try:
                    gii_right_mesh = read_gii(
                        file_uploads[GiftiFiles.RIGHT_MESH.value], 
                        self.method
                    )
                except Exception as e:
                    raise exception.FileUploadError(
                        'Error in reading right hemisphere mesh (geometry) gifti file',
                        exception.ExceptionFileTypes.GIFTI.value, self.method
                    ) from e
                
                if not validate.validate_gii_mesh(gii_right_mesh):
                    raise exception.FileValidationError(
                        "The right hemisphere mesh (geometry) file should only contain "
                        "two data arrays, corresponding to coordinate and face arrays."
                        " Check format.",
                        validate.validate_gii_mesh.__name__,
                        exception.ExceptionFileTypes.GIFTI
                    )
            
                gifti_out[GiftiFiles.RIGHT_MESH.value] = gii_left_mesh
            
            return gifti_out

    def _check_file_inputs(
        self, file_inputs: dict
    ) -> None:
        """
        check left and right hemisphere file uploads
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
                msg, exception.ExceptionFileTypes.GIFTI.value, self.method
            )

    def _get_browser_input() -> dict:
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

    def _get_cli_input() -> dict:
        raise NotImplementedError(
            'cli upload for nifti inputs not implemented yet'
        )


def read_gii(
    file,
    method=Literal['cli', 'browser']
) -> nib.GiftiImage:
    """
    Read gifti file based on method of upload (cli or browser)

    Parameters:
    file: either a gifti file from the browser or full path to file from CLI.
    method str: whether the file was uploaded through browser or CLI

    Returns:
    nib.GiftiImage: nibabel image
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
