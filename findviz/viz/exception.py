"""
Findviz error classes
"""
from enum import Enum
from typing import Literal, Optional, List


class ExceptionFileTypes(Enum):
    NIFTI='nifti'
    GIFTI='gifti'
    TIMECOURSE='timecourse'
    TASK='task'
    NIFTI_GIFTI='nifti/gifti'

class Routes(Enum):
    GET_DATA_UPDATE='get_data_update'
    GET_FUNCTIONAL_TIMECOURSE='get_functional_timecourse'
    PREPROCESS_FMRI='preprocess_fmri'

class FileInputError(Exception):
    """
    Error in file inputs provided by user

    Attributes
    ----------
    message : str
        custom error message to display to user
    file_type : str
        what type of file (e.g. nifti, timecourse) the error occured with
    method : str
        whether the error occured from a file upload via the web browser
          or the command line (cli)
    field: Optional[List[str]]
        the HTML Div id of the form field(s) the file came from, if upload 
            method is web browser. Optional. Default: None
    index: Optional[List[int]]
        the index of the HTML div in the document, if multiple elements 
        for the same field label (e.g. time course inputs). Index starts at
        zero. Optional. Default: None.
    """
    def __init__(
        self, 
        message: str, 
        file_type: Literal[
            ExceptionFileTypes.NIFTI, 
            ExceptionFileTypes.GIFTI, 
            ExceptionFileTypes.TIMECOURSE, 
            ExceptionFileTypes.TASK,
            ExceptionFileTypes.NIFTI_GIFTI
        ], 
        method: Literal['cli', 'browser'],
        field: Optional[List[str]] = None,
        index: Optional[List[int] | int] = None
    ):
        super().__init__(message)
        self.message = message
        self.file_type = file_type
        self.method = method
        self.field = field

        if index is None:
            self.index=index
        else:
            # handle single integer, non-list inputs
            if not isinstance(index, list):
                # if not integer-like, raise value error
                try:
                    index = int(index)
                except ValueError:
                    raise AttributeError(
                        'input for index parameter must be list or integer'
                    )
                self.index = [index]
            else:
                self.index = index

    def __str__(self):
        return f"{self.message} - {self.file_type.value} via {self.method}"


class FileUploadError(Exception):
    """
    Error in file upload

     Attributes
    ----------
    message : str
        custom error message to display to user
    file_type : str
        what type of file (e.g. nifti, timecourse) the error occured with
    method : str
        whether the error occured from a file upload via the web browser
          or the command line (cli)
    field: Optional[List[str]]
        the HTML Div id of the form field(s) the file came from, if upload 
            method is web browser. Optional. Default: None
    index: Optional[List[int]]
        the index of the HTML div in the document, if multiple elements 
        for the same field label (e.g. time course inputs). Index starts at
        zero. Optional. Default: None.
    """
    def __init__(
        self, 
        message: str, 
        file_type: Literal[
            ExceptionFileTypes.NIFTI, 
            ExceptionFileTypes.GIFTI, 
            ExceptionFileTypes.TIMECOURSE, 
            ExceptionFileTypes.TASK,
            ExceptionFileTypes.NIFTI_GIFTI
        ], 
        method: Literal['cli', 'browser'],
        field: Optional[List[str]] = None,
        index: Optional[List[int] | int] = None
    ):
        super().__init__(message)
        self.message = message
        self.file_type = file_type
        self.method = method
        self.field = field

        if index is None:
            self.index=index
        else:
            # handle single integer, non-list inputs
            if not isinstance(index, list):
                # if not integer-like, raise value error
                try:
                    index = int(index)
                except ValueError:
                    raise AttributeError(
                        'input for index parameter must be list or integer'
                    )
                self.index = [index]
            else:
                self.index = index

    def __str__(self):
        return f"{self.message} - {self.file_type.value} via {self.method}"


class FileValidationError(Exception):
    """
    Error in file validation

     Attributes
    ----------
    message : str
        custom error message to display to user
    func_name : str
        the validator function name that raised the error
    file_type : str
        what type of file (e.g. nifti, timecourse) the error occured with
    field: Optional[List[str]]
        the HTML Div id of the form field(s) the file came from, if upload 
            method is web browser. Optional. Default: None
    index: Optional[List[int]]
        the index of the HTML div in the document, if multiple elements 
        for the same field label (e.g. time course inputs). Index starts at
        zero. Optional. Default: None.
    """
    def __init__(
        self, 
        message: str, 
        func_name: str,
        file_type: Literal[
            ExceptionFileTypes.NIFTI, 
            ExceptionFileTypes.GIFTI, 
            ExceptionFileTypes.TIMECOURSE, 
            ExceptionFileTypes.TASK,
            ExceptionFileTypes.NIFTI_GIFTI
        ],
        field: Optional[List[str]] = None,
        index: Optional[List[int] | int] = None
    ):
        super().__init__(message)
        self.message = message
        self.func_name = func_name
        self.file_type = file_type
        self.field = field

        if index is None:
            self.index=index
        else:
            # handle single integer, non-list inputs
            if not isinstance(index, list):
                # if not integer-like, raise value error
                try:
                    index = int(index)
                except ValueError:
                    raise AttributeError(
                        'input for index parameter must be list or integer'
                    )
                self.index = [index]
            else:
                self.index = index

    def __str__(self):
        return f"{self.message} - validation error in {self.func_name} for {self.file_type.value} file"


class DataRequestError(Exception):
    """
    Missing data in request for data update

    Attributes
    ----------
    message : str
        custom error message to display to user
    fmri_file_type : str
        what type of file (e.g. nifti, timecourse) the error occured with
    route : Routes
        the route that the error occured in
    input_field: str
        the input field that was not available in request.form
    """
    def __init__(
        self, 
        message: str, 
        fmri_file_type: Literal['nifti', 'gifti'], 
        route: Routes,
        input_field: str
    ):
        super().__init__(message)
        self.message = message
        self.input_field = input_field
        self.fmri_file_type = fmri_file_type
        self.route = route

    def __str__(self):
        if self.input_field:    
            return (f"{self.message} - missing input field: "
                   f"{self.input_field} for {self.fmri_file_type} "
                   f"via {self.route.value}")
        

class NiftiMaskError(Exception):
    """
    Error raised when mask is not provided for nifti processing

    Attributes
    ----------
    message : str
        custom error message to display to user
    """
    def __init__(
        self, 
        message: str
    ):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"Nifti mask error: {self.message}"
