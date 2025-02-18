"""
Utilities for handling nifti file uploads
"""
import gzip

from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Literal, Optional, Dict, Union

import nibabel as nib

from flask import request
from nilearn.image import reorder_img
from werkzeug.datastructures import FileStorage

from findviz.viz import exception
from findviz.viz.io import validate
from findviz.viz.io import utils

# Type aliases
FilePath = Union[str, Path]
FileUploadDict = Dict[str, Optional[Union[FilePath, 'FileStorage']]]
NiftiDict = Dict[str, Optional[nib.Nifti1Image]]

# Expected file upload inputs
class NiftiFiles(Enum):
    FUNC = 'nii_func'
    ANAT = 'nii_anat'
    MASK = 'nii_mask'

# Browser fields type definition
browser_fields: Dict[str, str] = {
    NiftiFiles.FUNC.value: 'nifti-func',
    NiftiFiles.ANAT.value: 'nifti-anat',
    NiftiFiles.MASK.value: 'nifti-mask',
}

class NiftiUpload:
    """
    Class for handling nifti file uploads.

    Attributes
    ----------
    method : Literal['cli', 'browser']
        The method used for file uploads
    """

    def __init__(
        self,
        method: Literal['cli', 'browser']
    ):
        self.method = method

    def upload(
        self,
        fmri_files: Optional[Dict[str, Union[str, Path]]] = None,
    ) -> NiftiDict:
        """
        Get and validate nifti files uploaded from cli or browser.

        Parameters
        ----------
        fmri_files : Optional[Dict[str, FilePath]]
            Dictionary of Nifti file paths: 
            {'nii_func': path, 'nii_anat': path, 'nii_mask': path}

        Returns
        -------
        NiftiDict
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

        # nifti file is not optional
        if file_uploads[NiftiFiles.FUNC.value] is None:
            raise exception.FileInputError(
                'Please upload a Nifti file (.nii or .nii.gz). for '
                'functional file',
                exception.ExceptionFileTypes.NIFTI.value, self.method,
                [browser_fields[NiftiFiles.FUNC.value]]
            )
        
        # validate func file extension
        if not validate.validate_nii_ext(
            utils.get_filename(file_uploads[NiftiFiles.FUNC.value])
        ):
            raise exception.FileInputError(
                'File extension is not recognized. Please upload a Nifti file '
                 ' (.nii or .nii.gz). for functional file',
                exception.ExceptionFileTypes.NIFTI.value, self.method,
                [browser_fields[NiftiFiles.FUNC.value]]
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
                'Error in reading functional nifti file. Please check format.',
                exception.ExceptionFileTypes.NIFTI.value, self.method,
                [browser_fields[NiftiFiles.FUNC.value]]
            ) from e
        # validate functional is 4d
        if not validate.validate_nii_4d(nii_func):
            raise exception.FileValidationError(
                "The functional file must have 4-dimensions (x,y,z,time). "
                 " Please check file.",
                validate.validate_nii_4d.__name__,
                exception.ExceptionFileTypes.NIFTI.value,
                [browser_fields[NiftiFiles.FUNC.value]]
            )

        # Reorient to RAS
        nii_func = reorder_img(nii_func)
        
        nifti_out[NiftiFiles.FUNC.value] = nii_func

        # Load and validate anatomical
        if file_uploads[NiftiFiles.ANAT.value] is not None:
            # validate anat file extension
            if not validate.validate_nii_ext(
                utils.get_filename(file_uploads[NiftiFiles.ANAT.value])
            ):
                raise exception.FileInputError(
                    'File extension is not recognized. Please upload a Nifti file '
                    ' (.nii or .nii.gz). for anatomical file',
                    exception.ExceptionFileTypes.NIFTI.value, self.method,
                    [browser_fields[NiftiFiles.ANAT.value]]
                )
            
            try:
                nii_anat = read_nii(file_uploads[NiftiFiles.ANAT.value], self.method)
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading anatomical nifti file',
                    exception.ExceptionFileTypes.NIFTI.value, self.method,
                    [browser_fields[NiftiFiles.ANAT.value]]
                ) from e
            # validate anat is 3d
            if not validate.validate_nii_3d(nii_anat):
                raise exception.FileValidationError(
                    "The anat file must have only 3-dimensions (x,y,z). Please "
                    "check file.",
                    validate.validate_nii_3d.__name__,
                    exception.ExceptionFileTypes.NIFTI.value,
                    [browser_fields[NiftiFiles.ANAT.value]]
                )
            # validate that anat and func voxel dimension lengths are consistent
            if not validate.validate_nii_same_dim_len(nii_anat, nii_func):
                raise exception.FileValidationError(
                    "The anat file does not have the same voxel dimension "
                    "lengths as the functional file. Please check file.",
                    validate.validate_nii_same_dim_len.__name__,
                    exception.ExceptionFileTypes.NIFTI.value,
                    [browser_fields[NiftiFiles.ANAT.value]]
                )
            
            # Reorient to RAS
            nii_anat = reorder_img(nii_anat)
            nifti_out[NiftiFiles.ANAT.value] = nii_anat
        
        # load and validate mask 
        if file_uploads[NiftiFiles.MASK.value] is not None:
             # validate mask file extension
            if not validate.validate_nii_ext(
                utils.get_filename(file_uploads[NiftiFiles.MASK.value])
            ):
                raise exception.FileInputError(
                    'File extension is not recognized. Please upload a Nifti file '
                    ' (.nii or .nii.gz). for mask file',
                    exception.ExceptionFileTypes.NIFTI.value, self.method,
                    [browser_fields[NiftiFiles.MASK.value]]
                )
            
            try:
                nii_mask = read_nii(file_uploads[NiftiFiles.MASK.value], self.method)
            except Exception as e:
                raise exception.FileUploadError(
                    'Error in reading mask nifti file',
                    exception.ExceptionFileTypes.NIFTI.value, self.method,
                    [browser_fields[NiftiFiles.MASK.value]]
                ) from e
            # validate mask is 3d
            if not validate.validate_nii_3d(nii_mask):
                raise exception.FileValidationError(
                    "The mask file must have only 3-dimensions (x,y,z). Please "
                    "check file.",
                    validate.validate_nii_3d.__name__,
                    exception.ExceptionFileTypes.NIFTI.value,
                    [browser_fields[NiftiFiles.MASK.value]]
                )
            # validate that mask and func voxel dimension lengths are consistent
            if not validate.validate_nii_same_dim_len(nii_mask, nii_func):
                raise exception.FileValidationError(
                    "The mask file does not have the same voxel dimension "
                    "lengths as the functional file. Please check file.",
                    validate.validate_nii_same_dim_len.__name__,
                    exception.ExceptionFileTypes.NIFTI.value,
                    [browser_fields[NiftiFiles.MASK.value]]
                )
            # validate that mask only contains 1s and 0s
            if not validate.validate_nii_brain_mask(nii_mask):
                raise exception.FileValidationError(
                    "The mask file must only contain 1s and 0s. Please check file.",
                    validate.validate_nii_brain_mask.__name__,
                    exception.ExceptionFileTypes.NIFTI.value,
                    [browser_fields[NiftiFiles.MASK.value]]
                )
            # Reorient to RAS
            nii_mask = reorder_img(nii_mask)
            nifti_out[NiftiFiles.MASK.value] = nii_mask

        return nifti_out

    @staticmethod
    def _get_browser_input() -> dict:
        """
        Get file uploads from browser request.

        Returns
        -------
        FileUploadDict
            Dictionary containing file upload objects
        """
        nifti_file = request.files.get(NiftiFiles.FUNC.value)
        anatomical_file = request.files.get(NiftiFiles.ANAT.value)
        mask_file = request.files.get(NiftiFiles.MASK.value)

        file_upload = {
            NiftiFiles.FUNC.value: nifti_file,
            NiftiFiles.ANAT.value: anatomical_file,
            NiftiFiles.MASK.value: mask_file
        }
        return file_upload


def read_nii(
    file: Union[FilePath, 'FileStorage'],
    method: Literal['cli', 'browser']
) -> nib.Nifti1Image:
    """
    Read nifti file based on method of upload.

    Parameters
    ----------
    file : Union[FilePath, FileStorage]
        Either a nifti file from the browser or full path to file from CLI
    method : Literal['cli', 'browser']
        Whether the file was uploaded through browser or CLI

    Returns
    -------
    nib.Nifti1Image
        Loaded nibabel image

    Raises
    ------
    Exception
        If there are issues reading the file
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


def _read_nii_browser(
    file: 'FileStorage',
    ext: Literal['.nii', '.nii.gz']
) -> nib.Nifti1Image:
    """
    Read .nii or .nii.gz compressed nifti file from browser.

    Parameters
    ----------
    file : FileStorage
        File upload object from browser
    ext : Literal['.nii', '.nii.gz']
        File extension

    Returns
    -------
    nib.Nifti1Image
        Loaded nibabel image

    Raises
    ------
    Exception
        If there are issues reading the file
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









