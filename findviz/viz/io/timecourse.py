"""
Utilities for handling time course and task design uploads
"""
from enum import Enum
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union, TypedDict, Any, Tuple
from werkzeug.datastructures import FileStorage

import numpy as np
import numpy.typing as npt

from flask import request
from nilearn.glm.first_level import compute_regressor

from findviz.viz import exception
from findviz.viz.io import validate
from findviz.viz.io import utils


# Type aliases
FilePath = Union[str, Path]
FileInput = Union[FilePath, FileStorage]


# task design output fields
class ConditionDict(TypedDict):
    block: List[float]
    hrf: List[float]

class TaskDesignDict(TypedDict):
    task_regressors: Dict[str, ConditionDict]
    tr: float
    slicetime_ref: float

# time course output fields
class TimeCourseDict(TypedDict):
    ts_label: List[float]


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


# timecourse/task form fields in upload modal
browser_fields = {
    TimeCourseFiles.FILES.value: 'time-series-file',
    TimeCourseFiles.LABELS.value: 'time-series-label',
    TimeCourseFiles.HEADERS.value: 'has-header',
    TaskDesignFiles.FILE.value: 'task-design-file',
    TaskDesignFiles.TR.value: 'task-design-tr',
    TaskDesignFiles.SLICETIME.value: 'task-design-slicetime'
}

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

    def upload(
        self,
        fmri_len: int,
        task_file: Optional[Union[str, Path]] = None,
        tr: Optional[float] = None,
        slicetime_ref: Optional[float] = None
    ) -> TaskDesignDict:
        """
        Get task design files and fields uploaded from cli or browser.

        Parameters
        ----------
        fmri_len : int
            Length of functional MRI time course
        task_file : Union[str, Path], optional
            Path to task design file
        tr : float, optional
            Repetition time value
        slicetime_ref : float, optional
            Slice timing reference value (0-1)

        Returns
        -------
        TaskDesignDict
            Dictionary containing task design data and parameters

        Raises
        ------
        FileInputError
            If required files are missing or invalid
        FileValidationError
            If file contents fail validation
        FileUploadError
            If there are issues reading the files
        """
        try:
            if self.method == 'cli':
                file_uploads = {
                    TaskDesignFiles.FILE.value: task_file,
                    TaskDesignFiles.TR.value: tr,
                    TaskDesignFiles.SLICETIME.value: slicetime_ref
                }
            elif self.method == 'browser':
                file_uploads = self._get_browser_input()
        except exception.FileInputError as e:
            # propagate file input returned from get files function
            raise e

        task_tr = file_uploads[TaskDesignFiles.TR.value]
        task_slicetime = file_uploads[TaskDesignFiles.SLICETIME.value]

        # first, validate tr and slicetime values are provided
        if task_tr == '' or task_tr is None:
            raise exception.FileInputError(
                'TR is required for task design file',
                exception.ExceptionFileTypes.TASK.value,
                self.method,
                [browser_fields[TaskDesignFiles.TR.value]]
            )
        if task_slicetime == '' or task_slicetime is None:
            raise exception.FileInputError(
                'Slicetime reference is required for task design file',
                exception.ExceptionFileTypes.TASK.value,
                self.method,
                [browser_fields[TaskDesignFiles.SLICETIME.value]]
            )

        # validate tr and slicetime values are numeric
        if not validate.validate_ts_numeric(task_tr):
            raise exception.FileValidationError(
                'Provided TR for task design file is not numeric: '
                f'{task_tr}. Please check entry',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TASK.value,
                [browser_fields[TaskDesignFiles.FILE.value]]
            )

        if not validate.validate_ts_numeric(task_slicetime):
            raise exception.FileValidationError(
                f'Provided slicetime reference for task design file is not '
                f'numeric: {task_slicetime}. Please check entry',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TASK.value,
                [browser_fields[TaskDesignFiles.FILE.value]]
            )

        task_tr = float(task_tr)
        task_slicetime = float(task_slicetime)
        # validate tr is not negative
        if not validate.validate_task_tr(task_tr):
            raise exception.FileValidationError(
                f'TR must not be less than zero: {task_tr}. '
                'Please check entry',
                validate.validate_task_tr.__name__,
                exception.ExceptionFileTypes.TASK.value,
                [browser_fields[TaskDesignFiles.FILE.value]]
            )

        # validate slicetime is b/w 0 and 1
        if not validate.validate_task_slicetime(task_slicetime):
            raise exception.FileValidationError(
                f'Slicetime reference must between 0 and 1: {task_slicetime}. '
                'Please check entry',
                validate.validate_task_slicetime.__name__,
                exception.ExceptionFileTypes.TASK.value,
                [browser_fields[TaskDesignFiles.FILE.value]]
            )

        # read task design file
        try:
            task_data = read_task_file(
                file_uploads[TaskDesignFiles.FILE.value],
                self.default_trial_label,
                self.method
            )
        # raise exception to be handled higher in stack
        except Exception as e:
            raise e

        # get task regressors
        task_reg = get_task_regressors(
            task_data, 
            task_tr, 
            task_slicetime, 
            fmri_len
        )
        task_out = {
            TaskDesignFiles.SLICETIME.value: task_slicetime,
            TaskDesignFiles.TR.value: task_tr,
            'task_regressors': task_reg
        }

        return task_out

    def _get_browser_input(self) -> Dict[str, Any]:
        """
        Get task design inputs from browser request.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing file and parameter inputs

        Raises
        ------
        FileInputError
            If file extension is invalid
        """
        task_file = request.files.get(TaskDesignFiles.FILE.value)
        task_tr = request.form.get(TaskDesignFiles.TR.value)
        task_slicetime = request.form.get(TaskDesignFiles.SLICETIME.value)

        file_upload = {
            TaskDesignFiles.FILE.value: task_file,
            TaskDesignFiles.TR.value: task_tr,
            TaskDesignFiles.SLICETIME.value: task_slicetime
        }
        # check file extension
        if not validate.validate_task_ext(
            utils.get_filename(task_file.filename)
        ):
            raise exception.FileInputError(
                f'Unrecognized file extension for {task_file.filename}. '
                'Only .csv or .tsv are allowed.',
                exception.ExceptionFileTypes.TASK.value, 
                self.method,
                [browser_fields[TaskDesignFiles.FILE.value]]
            )

        return file_upload


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

    def upload(
        self, 
        fmri_len: int, 
        ts_files: Optional[List[Union[str, Path]]] = None,
        ts_labels: Optional[List[str]] = None,
        ts_headers: Optional[List[bool]] = None,
    ) -> TimeCourseDict:
        """
        Get time course files and fields uploaded from cli or browser.

        Parameters
        ----------
        fmri_len : int
            Length of functional MRI time course
        ts_files : List[Union[str, Path]], optional
            List of paths to time series files
        ts_labels : List[str], optional
            List of labels for time series files
        ts_headers : List[bool], optional
            List of boolean flags indicating if time series files have headers

        Returns
        -------
        List[TimeCourseDict]
            List of dictionaries containing time course arrays and labels

        Raises
        ------
        FileInputError
            If files are missing or invalid
        FileValidationError
            If file contents fail validation
        """
        try:
            if self.method == 'cli':
                file_uploads = []
                for file, label, header in zip(ts_files, ts_labels, ts_headers):
                    single_upload = {
                        SingleTimeCourseFiles.FILE.value: file,
                        SingleTimeCourseFiles.LABEL.value: label,
                        SingleTimeCourseFiles.HEADER.value: header
                    }
                    file_uploads.append(single_upload)
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
            # get indices of duplicate labels
            dups_indx = [indx for indx, label in enumerate(ts_labels)
                          if label == dups[0]]
            raise exception.FileInputError(
                f'Duplicate time course labels found: {dups}. '
                'Please use unique labels.',
                'task', self.method,
                [browser_fields[TimeCourseFiles.FILES.value]],
                index=dups_indx
            )

        # Loop through timecourses and read
        ts_out = {}
        for i, file_package in enumerate(file_uploads):
            ts_file = file_package[SingleTimeCourseFiles.FILE.value]
            ts_label = file_package[SingleTimeCourseFiles.LABEL.value]
            ts_header = file_package[SingleTimeCourseFiles.HEADER.value]
            # check file extension
            if not validate.validate_ts_ext(
                utils.get_filename(ts_file.filename)
            ):
                raise exception.FileInputError(
                    'Unrecognized file extension for '
                    f'{utils.get_filename(ts_file)}.'
                     ' Only .csv or .txt are allowed.',
                    exception.ExceptionFileTypes.TIMECOURSE.value, self.method,
                    [browser_fields[TimeCourseFiles.FILES.value]],
                    index=[i]
                )
            # read time course file
            try:
                ts_array = read_ts_file(ts_file, ts_header, self.method, index=i)
            # raise exception to be handled higher in stack
            except Exception as e:
                raise e
                
            # check time course is the same length as fmri time course
            if not validate.validate_ts_fmri_length(fmri_len, ts_array):
                raise exception.FileValidationError(
                    f"length of {SingleTimeCourseFiles.FILE.value} "
                    f"({len(ts_array)}) is not the same length as "
                    f" fmri volumes ({fmri_len})",
                    validate.validate_ts_fmri_length.__name__,
                    exception.ExceptionFileTypes.TIMECOURSE.value,
                    [browser_fields[TimeCourseFiles.FILES.value]],
                    index=[i]
                )
            
            # package array in dict
            ts_out[ts_label] = ts_array

        return ts_out

    def _get_browser_input(self) -> List[Dict[str, Any]]:
        ts_file = request.files.getlist(TimeCourseFiles.FILES.value)
        ts_labels = request.form.getlist(TimeCourseFiles.LABELS.value)
        ts_headers = request.form.getlist(TimeCourseFiles.HEADERS.value)
        file_uploads = []
        for file, label, header in zip(ts_file, ts_labels, ts_headers):
            # convert header form data to boolean
            header_bool = True if header == 'true' else False
            single_upload = {
                SingleTimeCourseFiles.FILE.value: file,
                SingleTimeCourseFiles.LABEL.value: label,
                SingleTimeCourseFiles.HEADER.value: header_bool
            }
            file_uploads.append(single_upload)

        return file_uploads

    def _check_duplicate_labels(self, labels: List[str]) -> List[str]:
        """
        Check for duplicate time series labels.

        Parameters
        ----------
        labels : List[str]
            List of time series labels

        Returns
        -------
        List[str]
            List of duplicate labels found
        """
        duplicates = []
        seen = set()

        for element in labels:
            if element in seen:
                duplicates.append(element)
            else:
                seen.add(element)

        return duplicates


def get_ts_header(
    file: FileInput,
    file_index: int
) -> str:
    """
    Get first row of time course file as header and validate time course file.

    Parameters
    ----------
    file : FileInput
        Time course file from browser or CLI
    file_index : int
        Index of the time course file in multi-file upload

    Returns
    -------
    str
        The first row (representing the header)

    Raises
    ------
    FileInputError
        If file extension is invalid
    FileUploadError
        If there are issues reading the file
    """
    # load time course file and validate
    # check file extension
    filename = utils.get_filename(file)
    if not validate.validate_ts_ext(filename):
        raise exception.FileInputError(
            f'Unrecognized file extension for {filename}.'
                ' Only .csv or .txt are allowed.',
            exception.ExceptionFileTypes.TIMECOURSE.value, 'browser',
            [browser_fields[TimeCourseFiles.FILES.value]],
            index=[file_index]
        )
    # get header
    try:
        delimiter = ','
        reader = utils.get_csv_reader(file, delimiter, 'browser')
        header = next(reader)
    # raise generic exception to be handled higher in stack
    except Exception as e:
        raise exception.FileUploadError(
            f'Error in reading time course file:  {filename}',
            exception.ExceptionFileTypes.TIMECOURSE.value, 'browser',
            [browser_fields[TimeCourseFiles.FILES.value]],
            index=[file_index]
        ) from e

    # return first row
    return str(header[0])


def read_task_file(
    file: FileInput,
    default_trial_label: str,
    method: Literal['cli', 'browser']
) -> Dict[str, Any]:
    """
    Read task design file based on method of upload.

    Parameters
    ----------
    file : FileInput
        Task design file from browser or CLI
    default_trial_label : str
        Default label for trials without type
    method : Literal['cli', 'browser']
        Upload method

    Returns
    -------
    TaskDesignDict
        Dictionary containing task design data

    Raises
    ------
    ValueError
        If file object is invalid
    FileValidationError
        If file contents fail validation
    """
     # Get filename from file object
    filename = utils.get_filename(file)
    
    # get file extension (should be .tsv or .csv)
    ext = utils.get_file_ext(filename)

    if ext == '.tsv':
        delimiter = '\t'
    elif ext == '.csv':
        delimiter = ','

    # get reader for file input
    try:
        reader = utils.get_csv_reader(file, delimiter, method)
    # raise generic exception to be handled higher in stack
    except Exception as e:
        raise e

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
            exception.ExceptionFileTypes.TASK.value,
            [browser_fields[TaskDesignFiles.FILE.value]]
        )

    # validate there are no duplicate 'onset' or 'duration' columns
    if not validate.validate_task_header_duplicates(header, required_cols):
        raise exception.FileValidationError(
            f'Task design file has multiple "{required_cols[0]}" or '
            f'"{required_cols[1]}" column:  {filename}',
            validate.validate_task_header_duplicates.__name__,
            exception.ExceptionFileTypes.TASK.value,
            [browser_fields[TaskDesignFiles.FILE.value]]
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
                exception.ExceptionFileTypes.TASK.value,
                [browser_fields[TaskDesignFiles.FILE.value]]
            )

        if not validate.validate_ts_numeric(row[duration_idx]):
            raise exception.FileValidationError(
                f'Non-numeric entry - {row[duration_idx]} - found in onset '
                f'column of task design file {filename}. All elements must be numeric.',
                validate.validate_ts_numeric.__name__,
                exception.ExceptionFileTypes.TASK.value,
                [browser_fields[TaskDesignFiles.FILE.value]]
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
    file: FileInput,
    header: bool,
    method: Literal['cli', 'browser'],
    index: Optional[int] = None,
    validate_numeric: bool = True
) -> List[float]:
    """
    Read time course file based on method of upload.

    Parameters
    ----------
    file : FileInput
        Time course file from browser or CLI
    header : bool
        Whether file has a header row
    method : Literal['cli', 'browser']
        Upload method
    index : Optional[int]
        Index of file in multi-file upload
    validate_numeric : bool
        Whether to validate numeric content

    Returns
    -------
    List[float]
        Time course as list of floats
    """
    filename = utils.get_filename(file)

    # get file reader for file input
    delimiter = ','
    try:
        reader = utils.get_csv_reader(file, delimiter, method)
    # raise generic exception to be handled higher in stack
    except Exception as e:
        raise exception.FileUploadError(
            f'Error in reading time course file:  {filename}',
            exception.ExceptionFileTypes.TIMECOURSE.value, method,
            [browser_fields[TimeCourseFiles.FILES.value]],
            index=index
        ) from e
    
    # skip first row, if header
    if header:
        next(reader)
    
    # read timecourse from list
    ts_raw = list(reader)
    # ensure there are rows in the data
    if not validate.validate_ts_task_length(ts_raw):
        raise exception.FileValidationError(
                f'No data found in time course file {filename}. '
                'Please check file',
                validate.validate_ts_task_length.__name__,
                exception.ExceptionFileTypes.TIMECOURSE.value,
                [browser_fields[TimeCourseFiles.FILES.value]],
                index=index
            )

    # Loop through rows of time course file and validate
    ts_array = []
    for i, row in enumerate(ts_raw):
        if not validate.validate_ts_single_col(row):
            raise exception.FileValidationError(
                f'Multiple columns found in time course file {filename}. '
                 'Only one column is allowed.',
                validate.validate_ts_single_col.__name__,
                exception.ExceptionFileTypes.TIMECOURSE.value,
                [browser_fields[TimeCourseFiles.FILES.value]],
                index=index
            )
        
        if validate_numeric:
            if not validate.validate_ts_numeric(row[0]):
                if header:
                    row_i = i
                else:
                    row_i = i+1
                raise exception.FileValidationError(
                    f'Non-numeric entry found in time course file {filename} on Line {row_i}.'
                    ' All elements must be numeric. If there is a header, '
                    'specify in input.',
                    validate.validate_ts_numeric.__name__,
                    exception.ExceptionFileTypes.TIMECOURSE.value,
                    [browser_fields[TimeCourseFiles.FILES.value]],
                    index=index
                )
        # if checks passed, append float of first index of row
        ts_array.append(float(row[0]))
    
    # return list of floats
    return ts_array

def get_task_regressors(
    task_events: Dict[str, Any], 
    task_tr: float,
    task_slicetime_ref: float,
    fmri_len: int
) -> Dict[str, Dict[str, List[float]]]:
    """
    Get task design regressors from task events dataframe

    Arguments:
    ----------
        task_events: task events dict with 'onset', 'duration', 'trial_type' keys
            (optional: 'trial_type')
        task_tr: float,
            TR of task design file
        task_slicetime_ref: float,
            Slicetime reference of task design file
        fmri_len: length of fmri
    
    Returns:
    --------
        task_reg: task design regressors
    """
    # calculate frame times based on lenght of fmri, slicetime ref and tr
    frame_times =  task_tr * (np.arange(fmri_len) + task_slicetime_ref)
    # initialize task regressors dict
    task_reg = {}

    trial_type = task_events['trial_type']
    onset = task_events['onset']
    duration = task_events['duration']

    # get conditions
    conditions = list(set(trial_type))

    # Loop through each condition and create regressors
    for c in conditions:
        task_reg[c] = {}
        # get row indices of condition events
        condition_idx = [
            i for i, r in enumerate(trial_type)
            if r == c
        ]
        # Get onset of events in condition
        c_onsets = [
            float(onset[i]) for i in condition_idx
        ]
        # Get duration of events in condition
        c_duration = [
            float(duration[i]) for i in condition_idx
        ]
        # generate dummy amplitude values of 1s
        c_amp = [1 for i in condition_idx]
        # package condition data into nested list
        conditions_desc = [c_onsets, c_duration, c_amp]

        # use nilearn to compute task regression w/o convolution
        cond_reg, _ = compute_regressor(
            conditions_desc, hrf_model=None, frame_times=frame_times
        )
        task_reg[c]['block'] = cond_reg[:,0].tolist()

        # use nilearn to compute task regression w hrf convolution
        cond_reg, _ = compute_regressor(
            conditions_desc, hrf_model='glover', frame_times=frame_times
        )
        task_reg[c]['hrf'] = cond_reg[:,0].tolist()
        
    return task_reg