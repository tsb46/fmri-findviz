"""
Utilities for handling time course and task design uploads
"""
from enum import Enum
from typing import List, Literal

import numpy as np

from flask import request

from findviz.viz import exception
from findviz.viz.io import validate
from findviz.viz.io import utils


# Expected time course file upload inputs
class TimeCourseFiles(Enum):
    FILES = 'ts_files'
    LABELS = 'ts_labels'
    HEADERS = 'ts_headers'


# Time course fields for single time course upload
class SingleTimeCourseFiles(Enum):
    FILE = 'ts_file'
    LABEL = 'ts_label'
    HEADER = 'ts_header'


# Expected task design file upload inputs
class TaskDesignFiles(Enum):
    FILE = 'task_file'
    TR = 'tr'
    SLICETIME = 'slicetime_ref'


# Task Design Output Fields
class TaskDesignFields(Enum):
    ONSET = 'onset'
    DURATION = 'duration'
    TRIAL_TYPE = 'trial_type'


class TaskDesignUpload:
    """
    Class for handling task design file uploads.

    Attributes:
        method (str): The method used for file uploads (cli , browser)
        default_trial_label (str): The default trial label for task design files
        that did not have 'trial_type' field
    """

    def __init__(
        self,
        method: Literal['cli', 'browser'],
        default_trial_label: str = 'task'
    ):
        self.method = method
        self.default_trial_label = default_trial_label

    def upload(self) -> dict:
        """
        Get task design files and fields uploaded from cli or browser

        Returns:
        dict: uploaded files
        """
        if self.method == 'cli':
            file_uploads = self._get_cli_input()
        elif self.method == 'browser':
            file_uploads = self._get_browser_input()

        # Validate tr and slicetime entries is numeric
        task_tr = file_uploads[TaskDesignFiles.TR.value]
        task_slicetime = file_uploads[TaskDesignFiles.SLICETIME.value]
        # first, validate is numeric
        if not validate.validate_ts_numeric(task_tr):
            raise exception.FileValidationError(
                'Provided TR for task design file is not numeric: '
                f'{task_tr}. Please check entry',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TASK.value
            )

        if not validate.validate_ts_numeric(task_slicetime):
            raise exception.FileValidationError(
                f'Provided slicetime reference for task design file is not '
                f'numeric: {task_slicetime}. Please check entry',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TASK.value
            )

        task_tr = float(task_tr)
        task_slicetime = float(task_slicetime)
        # validate tr is not negative
        if not validate.validate_task_tr(task_tr):
            raise exception.FileValidationError(
                f'TR must not be less than zero: {task_tr}. '
                'Please check entry',
                validate.validate_task_tr.__name__,
                exception.ExceptionFileTypes.TASK.value
            )

        # validate slicetime is b/w 0 and 1
        if not validate.validate_task_slicetime(task_slicetime):
            raise exception.FileValidationError(
                f'Slicetime reference must between 0 and 1: {task_slicetime}. '
                'Please check entry',
                validate.validate_task_slicetime.__name__,
                exception.ExceptionFileTypes.TASK.value
            )

        # read task design file
        task_out = read_task_file(
            file_uploads[TaskDesignFiles.FILE.value],
            self.default_trial_label,
            self.method
        )
        task_out[TaskDesignFiles.SLICETIME.value] = task_slicetime
        task_out[TaskDesignFiles.TR.value] = task_tr

        return task_out

    def _get_browser_input(self) -> List[dict]:
        task_file = request.files.get(TaskDesignFiles.FILE.value)
        task_tr = request.form.get(TaskDesignFiles.TR.value)
        task_slicetime = request.form.get(TaskDesignFiles.SLICETIME.value)

        file_upload = {
            TaskDesignFiles.FILE.value: task_file,
            TaskDesignFiles.TR.value: task_tr,
            TaskDesignFiles.SLICETIME.value: task_slicetime
        }
        # check file extension
        if not validate.validate_task_ext(task_file.filename):
            raise exception.FileInputError(
                f'Unrecognized file extension for {task_file.filename}. '
                'Only .csv or .tsv are allowed.',
                exception.ExceptionFileTypes.TIMECOURSE.value, self.method
            )

        return file_upload

    def _get_cli_input() -> List[dict]:
        raise NotImplementedError(
            'cli upload for nifti inputs not implemented yet'
        )


class TimeCourseUpload:
    """
    Class for handling time course file uploads.

    Attributes:
        method (str): The method used for file uploads (cli , browser)
    """

    def __init__(
        self,
        method: Literal['cli', 'browser']
    ):
        self.method = method

    def upload(self) -> List[dict]:
        """
        Get time course files and fields uploaded from cli or browser

        Returns:
        List[dict]: list of dictionaries containing time course array and
        time course label
        """
        try:
            if self.method == 'cli':
                file_uploads = self._get_cli_input()
            elif self.method == 'browser':
                file_uploads = self._get_browser_input()
        except exception.FileInputError as e:
            # propagate file input returned from get files function
            raise e

        # check for duplicate time series labels in input
        ts_labels = [
            file[SingleTimeCourseFiles.LABEL.value]
            for file in file_uploads
        ]
        dups = self._check_duplicate_labels(ts_labels)
        if len(dups) > 0:
            raise exception.FileInputError(
                f'Duplicate time course labels found: {dups}. '
                'Please use unique labels.',
                'task', self.method
            )

        # Loop through timecourses and read
        ts_out = []
        for file_package in file_uploads:
            ts_file = file_package[SingleTimeCourseFiles.FILE.value]
            ts_label = file_package[SingleTimeCourseFiles.LABEL.value]
            ts_header = file_package[SingleTimeCourseFiles.HEADER.value]
            # read time course file
            ts_array = read_ts_file(ts_file, ts_header, self.method)
            # package array in dict
            ts_dict = {
                SingleTimeCourseFiles.FILE.value: ts_array,
                SingleTimeCourseFiles.LABEL.value: ts_label
            }
            ts_out.append(ts_dict)

        return ts_out


    def _get_browser_input(self) -> List[dict]:
        ts_file = request.files.getlist(TimeCourseFiles.FILES.value)
        ts_labels = request.form.getlist(TimeCourseFiles.LABELS.value)
        ts_headers = request.form.getlist(TimeCourseFiles.HEADERS.value)

        file_uploads = []
        for file, label, header in zip(ts_file, ts_labels, ts_headers):
            # check file extension
            if not validate.validate_ts_ext(file.filename):
                raise exception.FileInputError(
                    f'Unrecognized file extension for {file.filename}.'
                     ' Only .csv or .txt are allowed.',
                    'task', self.method
                )
            single_upload = {
                SingleTimeCourseFiles.FILE.value: file,
                SingleTimeCourseFiles.LABEL.value: label,
                SingleTimeCourseFiles.HEADER.value: header
            }
            file_uploads.append(single_upload)

        return file_uploads

    def _get_cli_input() -> List[dict]:
        raise NotImplementedError(
            'cli upload for time course inputs not implemented yet'
        )

    def _check_duplicate_labels(self, labels):
        """
        Check for duplicate time series labels
        """
        duplicates = []
        seen = set()

        for element in labels:
            if element in seen:
                duplicates.append(element)
            else:
                seen.add(element)

        return duplicates


def read_task_file(
    file,
    default_trial_label: str,
    method=Literal['cli', 'browser']
) -> dict:
    """
    Read task design file based on method of upload (cli or browser)

    Parameters:
    file: either a task file from the browser or full path to file from CLI.
    default_trial_label (str): The default trial label for task design files
    method (str): whether the file was uploaded through browser or CLI

    Returns:
    dict: task design dict with fields as keys and columns as lists
    """
     # Get filename from file object
    if hasattr(file, 'filename'):
        filename = file.filename
    elif hasattr(file, 'name'):
        filename = file.name
    else:
        raise ValueError("File object must have 'filename' or 'name' attribute")
    
    # get file extension (should be .tsv or .csv)
    ext = utils.get_file_ext(filename)

    if ext == '.tsv':
        delimiter = '\t'
    elif ext == '.csv':
        delimiter = ','

    # get reader for file input
    try:
        reader = utils.get_csv_reader(file, delimiter, method)
    # raise FileUpload error from generic exception
    except Exception as e:
        raise exception.FileUploadError(
            f'Error in reading task design file:  {filename}',
            exception.ExceptionFileTypes.TASK.value, method
        ) from e

    # get and validate header
    header = next(reader)
    required_cols = [
        TaskDesignFields.ONSET.value,
        TaskDesignFields.DURATION.value
    ]
    # validate required columns ('onset' and 'duration')
    if not validate.validate_task_header_required_cols(header, required_cols):
        raise exception.FileValidationError(
            f'Task design file is missing "{required_cols[0]}" or '
            f'"{required_cols[1]}" column:  {filename}',
            validate.validate_task_header_required_cols.__name__,
            exception.ExceptionFileTypes.TASK.value
        )

    # validate there are no duplicate 'onset' or 'duration' columns
    if not validate.validate_task_header_duplicates(header, required_cols):
        raise exception.FileValidationError(
            f'Task design file has multiple "{required_cols[0]}" or '
            f'"{required_cols[1]}" column:  {filename}',
            validate.validate_task_header_duplicates.__name__,
            exception.ExceptionFileTypes.TASK.value
        )

    # lower case and strip all columns in header
    header = [c.strip().lower() for c in header]
    # get indices of onset, duration columns
    onset_idx = header.index(TaskDesignFields.ONSET.value)
    duration_idx = header.index(TaskDesignFields.DURATION.value)

    # check whether optional trial type column is included
    try:
        trial_type_idx = header.index(TaskDesignFields.TRIAL_TYPE.value)
        trial_type = True
    except ValueError:
        trial_type_idx = None
        trial_type = False

    # Loop through rows of task design file
    task_out = {
        TaskDesignFields.ONSET.value: [],
        TaskDesignFields.DURATION.value: [],
        TaskDesignFields.TRIAL_TYPE.value: []
    }

    for i, row in enumerate(reader):
        # Check that onset and duration column are numeric
        if not validate.validate_ts_numeric(row[onset_idx]):
            raise exception.FileValidationError(
                f'Non-numeric entry - {row[onset_idx]} - found in '
                f'onset column of task design file {filename}. All '
                'elements must be numeric.',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TASK.value
            )

        if not validate.validate_ts_numeric(row[duration_idx]):
            raise exception.FileValidationError(
                f'Non-numeric entry - {row[duration_idx]} - found in onset '
                f'column of task design file {filename}. All elements must be numeric.',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TASK.value
            )
        # if checks passed, append to task out dict
        task_out[TaskDesignFields.ONSET.value].append(row[onset_idx])
        task_out[TaskDesignFields.DURATION.value].append(row[duration_idx])
        # append trial type if passed, otherwise default label
        if trial_type:
            task_out[TaskDesignFields.TRIAL_TYPE.value].append(
                row[trial_type_idx]
            )
        else:
            task_out[TaskDesignFields.TRIAL_TYPE.value].append(
                default_trial_label
            )
    return task_out


def read_ts_file(
    file,
    header: bool,
    method=Literal['cli', 'browser']
) -> np.ndarray:
    """
    Read time course file based on method of upload (cli or browser)

    Parameters:
    file: either a ts file from the browser or full path to file from CLI.
    header (bool): whether the file has a header
    method str: whether the file was uploaded through browser or CLI

    Returns:
    np.ndarray: time course as 2D (one column) numpy array
    """
    """Read task design file."""
    # Get filename from file object
    if hasattr(file, 'filename'):
        filename = file.filename
    elif hasattr(file, 'name'):
        filename = file.name
    else:
        raise ValueError("File object must have 'filename' or 'name' attribute")

    # get file reader for file input
    delimiter = ','
    try:
        reader = utils.get_csv_reader(file, delimiter, method)
    # raise FileUpload error from generic exception
    except Exception as e:
        raise exception.FileUploadError(
            f'Error in reading time course file:  {filename}',
            exception.ExceptionFileTypes.TIMECOURSE.value, method
        ) from e

    # Loop through rows of time course file and validate
    # skip first row, if header
    if header:
        next(reader)

    # ensure there are rows in the data
    if not validate.validate_ts_task_length(reader):
        raise exception.FileValidationError(
                f'No data found in time course file {filename}. '
                'Please check file',
                validate.validate_ts_task_length.__name__,
                exception.ExceptionFileTypes.TIMECOURSE.value
            )

    ts_array = []
    for i, row in enumerate(reader):
        if not validate.validate_ts_single_col(row):
            raise exception.FileValidationError(
                f'Multiple columns found in time course file {filename}. '
                 ' Only one column is allowed.',
                validate.validate_ts_single_col.__name__,
                exception.ExceptionFileTypes.TIMECOURSE.value
            )
        if not validate.validate_ts_numeric(row[0]):
            if header:
                row_i = i
            else:
                row_i = i+1
            raise exception.FileValidationError(
                f'Non-numeric entry found in time course file {filename} on {row_i}.'
                 ' All elements must be numeric. If there is a header, '
                 'specify in input.',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TIMECOURSE.value
            )
        # if checks passed, append
        ts_array.append(row[0])

    # convert to 2D numpy array with one column
    ts_array = np.array(ts_array)[:,np.newaxis]

    return ts_array












