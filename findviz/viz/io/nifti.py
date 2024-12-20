"""
Utilities for handling nifti file uploads
"""
import gzip

from enum import Enum
from io import BytesIO
from typing import Literal

import nibabel as nib

from flask import request
from nilearn.image import reorder_img

from findviz.viz import exception
from findviz.viz.io import validate
from findviz.viz.io import utils


# Expected file upload inputs
class NiftiFiles(Enum):
    FUNC = 'func_file'
    ANAT = 'anat_file'
    MASK = 'mask_file'


class NiftiUpload:
    """
    Class for handling nifti file uploads.

    Attributes:
        method (str): The method used for file uploads (cli , browser)
    """

    def __init__(
        self,
        method: Literal['cli', 'browser']
    ):
        self.method = method

    def upload(self) -> dict:
        """
        Get nifti files uploaded from cli or browser

        Returns:
        dict: uploaded files
        """
        if self.method == 'cli':
            file_uploads = self._get_cli_input()
        elif self.method == 'browser':
            file_uploads = self._get_browser_input()

        # nifti file is not optional
        if file_uploads[NiftiFiles.FUNC.value] is None:
            raise exception.FileInputError(
                'Please upload a Nifti file (.nii or .nii.gz). for '
                'functional file',
                exception.ExceptionFileTypes.NIFTI.value, self.method
            )

        # Initialize output dictionary
        nifti_out = {
            NiftiFiles.FUNC.value: None,
            NiftiFiles.ANAT.value: None,
            NiftiFiles.MASK.value: None
        }
        # Load and validate functional
        try:
            nii_func = read_nii(file_uploads[NiftiFiles.FUNC.value], self.method)
        except Exception as e:
            raise exception.FileUploadError(
                'Error in reading functional nifti file',
                exception.ExceptionFileTypes.NIFTI.value, self.method
            ) from e
        # validate functional is 4d
        if not validate.validate_nii_4d(nii_func):
            raise exception.FileValidationError(
                "The functional file must have 4-dimensions (x,y,z,time). "
                 " Please check file.",
                validate.validate_nii_4d.__name__,
                exception.ExceptionFileTypes.NIFTI.value
            )

        # Reorient to RAS
        nii_func = reorder_img(nii_func)
        
        nifti_out[NiftiFiles.FUNC.value] = nii_func

        # Load and validate anatomical
        if file_uploads[NiftiFiles.ANAT.value] is not None:
            try:
                nii_anat = read_nii(file_uploads[NiftiFiles.ANAT.value], self.method)
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading anatomical nifti file',
                    exception.ExceptionFileTypes.NIFTI.value, self.method
                ) from e
            # validate anat is 3d
            if not validate.validate_nii_3d(nii_anat):
                raise exception.FileValidationError(
                    "The anat file must have only 3-dimensions (x,y,z). Please "
                    "check file.",
                    validate.validate_nii_3d.__name__,
                    exception.ExceptionFileTypes.NIFTI.value
                )
            # validate that anat and func voxel dimension lengths are consistent
            if not validate.validate_nii_same_dim_len(nii_anat, nii_func):
                raise exception.FileValidationError(
                    "The anat file does not have the same voxel dimension "
                    "lengths as the functional file. Please check file.",
                    validate.validate_nii_same_dim_len.__name__,
                    exception.ExceptionFileTypes.NIFTI.value
                )
            
            # Reorient to RAS
            nii_anat = reorder_img(nii_anat)
            nifti_out[NiftiFiles.ANAT.value] = nii_anat
        
        # load and validate mask 
        if file_uploads[NiftiFiles.MASK.value] is not None:
            try:
                nii_mask = read_nii(file_uploads[NiftiFiles.MASK.value], self.method)
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading mask nifti file',
                    exception.ExceptionFileTypes.NIFTI.value, self.method
                ) from e
            # validate mask is 3d
            if not validate.validate_nii_3d(nii_mask):
                raise exception.FileValidationError(
                    "The mask file must have only 3-dimensions (x,y,z). Please "
                    "check file.",
                    validate.validate_nii_3d.__name__,
                    exception.ExceptionFileTypes.NIFTI.value
                )
            # validate that mask and func voxel dimension lengths are consistent
            if not validate.validate_nii_same_dim_len(nii_mask, nii_func):
                raise exception.FileValidationError(
                    "The mask file does not have the same voxel dimension "
                    "lengths as the functional file. Please check file.",
                    validate.validate_nii_same_dim_len.__name__,
                    exception.ExceptionFileTypes.NIFTI.value
                )
            # validate that mask only contains 1s and 0s
            if not validate.validate_nii_brain_mask(nii_anat, nii_func):
                raise exception.FileValidationError(
                    "The mask file must only contain 1s and 0s. Please check file.",
                    validate.validate_nii_brain_mask.__name__,
                    exception.ExceptionFileTypes.NIFTI.value
                )
            # Reorient to RAS
            nii_mask = reorder_img(nii_mask)
            nifti_out[NiftiFiles.MASK.value] = nii_mask

        return nifti_out

    def _get_browser_input() -> dict:
        nifti_file = request.files.get(NiftiFiles.FUNC.value)
        anatomical_file = request.files.get(NiftiFiles.ANAT.value)
        mask_file = request.files.get(NiftiFiles.MASK.value)

        file_upload = {
            NiftiFiles.FUNC.value: nifti_file,
            NiftiFiles.ANAT.value: anatomical_file,
            NiftiFiles.MASK.value: mask_file
        }
        return file_upload

    def _get_cli_input() -> dict:
        raise NotImplementedError(
            'cli upload for nifti inputs not implemented yet'
        )


def read_nii(
    file,
    method=Literal['cli', 'browser']
) -> nib.Nifti1Image:
    """
    Read nifti file based on method of upload (cli or browser)

    Parameters:
    file: either a nifti file from the browser or full path to file from CLI.
    method str: whether the file was uploaded through browser or CLI

    Returns:
    nib.Nifti1Image: nibabel image
    """
    if method =='cli':
        try:
            nifti_img = nib.load(file)
        # raise generic exception to be handled higher in stack
        except Exception as e:
            raise e
    elif method == 'browser':
        # get file extension
        ext = utils.parse_nifti_file_ext(file.filename)
        try:
            nifti_img = _read_nii_browser(file, ext=ext)
        except Exception as e:
            raise e
    return nifti_img


def _read_nii_browser(file, ext=Literal['.nii', '.nii.gz']) -> nib.Nifti1Image:
    """
    read .nii or .nii.gz compressed nifti file from browser
    """
    file_stream = BytesIO(file.read())
    try:
        if ext == '.nii.gz':
            with gzip.GzipFile(fileobj=file_stream, mode="rb") as d_stream:
                nifti_data = BytesIO(d_stream.read())
            file_stream.close()
            nifti_img = nib.Nifti1Image.from_bytes(nifti_data.read())
        elif ext == '.nii':
            nifti_img = nib.Nifti1Image.from_bytes(file_stream.read())
    # raise generic exception to be handled higher in stack
    except Exception as e:
        raise e
    return nifti_img









