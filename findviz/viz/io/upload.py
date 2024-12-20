"""
Utilities for loading and validating file uploads
"""
from enum import Enum
from typing import Literal

from findviz.logger_config import setup_logger
from findviz.viz import exception
from findviz.viz.io import gifti
from findviz.viz.io import nifti
from findviz.viz.io import timecourse

# Set up a logger for the app
logger = setup_logger(__name__)


class FileUpload:
    """
    Class for handling file uploads through browser or CLI. File inputs 
    are not stored in class.

    Attributes:
        fmri_file_type (str): The fMRI file type (gifti, nifti)
        ts_status (bool): Whether time course files were provided
        task_status (bool): Whether task design files were provided
        method (str): The method used for file uploads (cli , browser)
    """
    def __init__(
        self,
        fmri_file_type: Literal['nifti', 'gifti'],
        ts_status: bool,
        task_status: bool,
        method: Literal['cli', 'browser']
    ):
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
        else:
            raise ValueError('unrecognized fmri file type [nifti, gifti]')

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

        ## define output fields
        # gifti output fields
        class Gifti(Enum):
            LEFT_FUNC = gifti.GiftiFiles.LEFT_FUNC.value
            RIGHT_FUNC = gifti.GiftiFiles.RIGHT_FUNC.value
            LEFT_MESH = gifti.GiftiFiles.LEFT_MESH.value
            RIGHT_MESH = gifti.GiftiFiles.RIGHT_MESH.value
        
        # nifti output fields
        class Nifti(Enum):
            FUNC = nifti.NiftiFiles.FUNC.value
            ANAT = nifti.NiftiFiles.ANAT.value
            MASK = nifti.NiftiFiles.MASK.value
        
        # time course output fields
        class TimeCourse(Enum):
            FILE = timecourse.SingleTimeCourseFiles.FILE.value
            LABEL = timecourse.SingleTimeCourseFiles.FILE.value

        # task design output fields
        class Task(Enum):
            ONSET = timecourse.TaskDesignFields.ONSET
            DURATION = timecourse.TaskDesignFields.DURATION
            TRIAL_TYPE = timecourse.TaskDesignFields.TRIAL_TYPE

    def check_files(
        self, 
        key: Literal['gifti', 'nifti', 'ts', 'task']
    ) -> bool:
        """
        Check whether file type was uploaded by user based on key
        Parameters:
        key (Literal['gifti', 'nifti', 'ts', 'task']): The file type key.
    
        Returns:
        bool: whether file was uploaded or not
        """
        if not self.upload_status:
            raise AttributeError('No files have been uploaded!')

        try:
            return self.upload_status[key]
        except KeyError as e:
            raise Exception(f'{key} is not a recognized file label') from e

    def hemisphere(self) -> Literal['left', 'right', 'both']:
        """
        Check whether left, right or both hemispheres were uploaded in
        gifti file upload. If nifti was uploaded, an exception is returned.

        Returns:
        str: whether left, right or both hemisphers
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

    def upload(self) -> dict:
        """
        Upload nifti or gifti files, along with time course and task design
        files passed through CLI or web browser.

        Returns:
        dict: uploaded files from cli or browser
        """
        # init output dictionary
        file_out = {
            "gifti": None,
            "nifti": None,
            "ts": None,
            "task": None
        }
        # init upload status dictionary
        self.upload_status = {
            "gifti": False,
            "nifti": False,
            "ts": False,
            "task": False
        }
        
        # get files from CLI or browser
        try:
            fmri_files = self.fmri_uploader.upload()
            if self.fmri_file_type == 'gifti':
                file_out['gifti'] = fmri_files
                self.upload_status['gifti'] = True
            elif self.fmri_file_type == 'nifti':
                file_out['nifti'] = fmri_files
                self.upload_status['nifti'] = True

            if self.ts_status:
                ts_files = self.ts_uploader.upload()
                file_out['ts'] = ts_files
                self.upload_status['ts'] = True

            if self.task_status:
                task_files = self.task_uploader.upload()
                file_out['ts'] = task_files
                self.upload_status['ts'] = True

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
