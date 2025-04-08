"""
Utilities for loading and validating file uploads
"""
from enum import Enum
from typing import Literal, List, Dict, Optional, Union, TypedDict
from pathlib import Path

from findviz.logger_config import setup_logger
from findviz.viz import exception
from findviz.viz.io import cifti
from findviz.viz.io import gifti
from findviz.viz.io import nifti
from findviz.viz.io import timecourse

# Set up a logger for the app
logger = setup_logger(__name__)

# HTML Div IDs for upload modal 
browser_fields = {
    'nifti': nifti.browser_fields,
    'gifti': gifti.browser_fields,
    'ts': timecourse.browser_fields
}


class FileUpload:
    """
    Class for handling file uploads through browser or CLI.
    
    File inputs are not stored in class.

    Attributes
    ----------
    fmri_file_type : Literal['nifti', 'gifti', 'cifti']
        The fMRI file type
    ts_status : bool
        Whether time course files were provided
    task_status : bool
        Whether task design files were provided
    method : Literal['cli', 'browser']
        The method used for file uploads
    upload_status : Union[bool, Dict[str, bool]]
        State variable tracking upload status
    fmri_uploader : Union[NiftiUpload, GiftiUpload]
        Uploader for fMRI files
    fmri_file_labels : Union[NiftiFiles, GiftiFiles]
        File labels for fMRI files
    ts_uploader : Optional[TimeCourseUpload]
        Uploader for time series files
    ts_files : Optional[SingleTimeCourseFiles]
        File labels for time series
    task_uploader : Optional[TaskDesignUpload]
        Uploader for task design files
    task_files : Optional[TaskDesignFiles]
        File labels for task design
    """

    def __init__(
        self,
        fmri_file_type: Literal['nifti', 'gifti', 'cifti'],
        ts_status: bool,
        task_status: bool,
        method: Literal['cli', 'browser']
    ):
        """
        Initialize FileUpload instance.

        Parameters
        ----------
        fmri_file_type : Literal['nifti', 'gifti', 'cifti']
            Type of fMRI files to process
        ts_status : bool
            Whether time series files will be uploaded
        task_status : bool
            Whether task design files will be uploaded
        method : Literal['cli', 'browser']
            Method of file upload (command line or browser)

        Raises
        ------
        ValueError
            If fmri_file_type is not 'nifti', 'gifti', or 'cifti'
        """
        self.fmri_file_type = fmri_file_type
        self.ts_status = ts_status
        self.task_status = task_status
        self.method = method
        # state variable for whether files have been uploaded
        self.upload_status = False
        # get fmri file uploaders and file labels
        if fmri_file_type == 'gifti':
            self.fmri_uploader = gifti.GiftiUpload(method)
            self.fmri_file_labels = gifti.GiftiFiles
        elif fmri_file_type == 'nifti':
            self.fmri_uploader = nifti.NiftiUpload(method)
            self.fmri_file_labels = nifti.NiftiFiles
        elif fmri_file_type == 'cifti':
            self.fmri_uploader = cifti.CiftiUpload(method)
            self.fmri_file_labels = cifti.CiftiFiles
        else:
            raise ValueError('unrecognized fmri file type [nifti, gifti, cifti]')

        # get time course file uploaders and file labels
        if self.ts_status:
            self.ts_uploader = timecourse.TimeCourseUpload(method)
            self.ts_files = timecourse.SingleTimeCourseFiles
        else:   
            self.ts_uploader = None
            self.ts_files = None

        # get task design file uploaders and file labels
        if self.task_status:
            self.task_uploader = timecourse.TaskDesignUpload(method)
            self.task_files = timecourse.TaskDesignFiles
        else:
            self.task_uploader = None
            self.task_files = None

    def check_files(
        self, 
        key: Literal['gifti', 'nifti', 'cifti', 'ts', 'task']
    ) -> bool:
        """
        Check whether file type was uploaded by user.

        Parameters
        ----------
        key : Literal['gifti', 'nifti', 'cifti', 'ts', 'task']
            The file type to check

        Returns
        -------
        bool
            Whether files of the specified type were uploaded

        Raises
        ------
        AttributeError
            If no files have been uploaded yet
        KeyError
            If key is not a recognized file label
        """
        if not self.upload_status:
            raise AttributeError('No files have been uploaded!')

        try:
            return self.upload_status[key]
        except KeyError as e:
            raise Exception(f'{key} is not a recognized file label') from e

    def hemisphere(self) -> Literal['left', 'right', 'both']:
        """
        Check which hemispheres were uploaded in GIFTI file upload.

        Returns
        -------
        Literal['left', 'right', 'both']
            Which hemisphere(s) were uploaded

        Raises
        ------
        AttributeError
            If no files have been uploaded yet or if using NIFTI files
        """
        if not self.upload_status:
            raise AttributeError('No files have been uploaded!')

        if self.fmri_file_type == 'nifti':
            raise AttributeError(
                'hemisphere function not supported for nifti file inputs'
            )

        if self.fmri_file_type == 'gifti':
            if self.fmri_uploader.left_input & self.fmri_uploader.right_input:
                return 'both'
            elif self.fmri_uploader.left_input:
                return 'left'
            elif self.fmri_uploader.right_input:
                return 'right'

    def upload(
        self,
        fmri_files: Optional[Dict[str, Union[str, Path]]] = None,
        ts_files: Optional[List[Union[str, Path]]] = None,
        ts_labels: Optional[List[str]] = None,
        ts_headers: Optional[List[bool]] = None,
        task_file: Optional[Union[str, Path]] = None,
        tr: Optional[float] = None,
        slicetime_ref: Optional[float] = None
    ) -> Dict:
        """
        Upload and validate files from either browser or CLI.

        Parameters
        ----------
        fmri_files : Dict[str, Union[str, Path]], optional
            Dictionary of FMRI file paths. For NIFTI: {'nii_func': path, 'nii_anat': path, 'nii_mask': path}
            For GIFTI: {'left_gii_func': path, 'right_gii_func': path, 'left_gii_mesh': path, 'right_gii_mesh': path}
            For CIFTI: {'dtseries': path, 'left_gii_mesh': path, 'right_gii_mesh': path}
        ts_files : List[Union[str, Path]], optional
            List of paths to time series files
        ts_labels : List[str], optional
            List of labels for time series files
        ts_headers : List[bool], optional
            List of boolean flags indicating if time series files have headers
        task_file : Union[str, Path], optional
            Path to task design file
        tr : float, optional
            Repetition time value
        slicetime_ref : float, optional
            Slice timing reference value (0-1)
            
        Returns
        -------
        FileOutput
            Dictionary containing processed and validated file data
        
        Raises
        ------
        FileInputError
            If required files are missing
        FileUploadError
            If there are issues uploading files
        FileValidationError
            If files fail validation
        """
        # init output dictionary
        file_out = {
            "gifti": None,
            "nifti": None,
            "ts": None,
            "task": None
        }
        
        # init upload status dictionary
        self.upload_status: Dict[str, bool] = {
            "gifti": False,
            "nifti": False,
            "ts": False,
            "task": False
        }
        
        # get files from CLI or browser
        try:
            # upload fmri files
            fmri_files = self.fmri_uploader.upload(fmri_files)
            # store fmri files
            if self.fmri_file_type == 'gifti' or self.fmri_file_type == 'cifti':
                file_out['gifti'] = fmri_files
                self.upload_status['gifti'] = True
            elif self.fmri_file_type == 'nifti':
                file_out['nifti'] = fmri_files
                self.upload_status['nifti'] = True
            
            # get # of volumes from functional MRI
            if self.fmri_file_type == 'nifti':
                fmri_len = file_out['nifti'][nifti.NiftiFiles.FUNC.value].shape[-1]
            elif self.fmri_file_type == 'gifti' or self.fmri_file_type == 'cifti':
                if self.fmri_uploader.left_input:
                    gifti_out = file_out['gifti'][gifti.GiftiFiles.LEFT_FUNC.value].darrays
                else:
                    gifti_out = file_out['gifti'][gifti.GiftiFiles.RIGHT_FUNC.value].darrays
                fmri_len = len(gifti_out)

            # get time series files
            if self.ts_status:
                ts_files = self.ts_uploader.upload(
                    fmri_len=fmri_len,
                    ts_files=ts_files,
                    ts_labels=ts_labels,
                    ts_headers=ts_headers
                )
                file_out['ts'] = ts_files
                self.upload_status['ts'] = True

            # get task design files
            if self.task_status:
                task_files = self.task_uploader.upload(
                    fmri_len=fmri_len,
                    task_file=task_file,
                    tr=tr,
                    slicetime_ref=slicetime_ref
                )
                file_out['task'] = task_files
                self.upload_status['task'] = True

        except (
            exception.FileInputError,
            exception.FileUploadError,
            exception.FileValidationError
        ) as e:
            # propagate file error returned from upload function
            raise e

        # update state variable
        self.upload_status = True

        return file_out

        