"""
Findviz error classes
"""
from enum import Enum
from typing import Literal


class ExceptionFileTypes(Enum):
    NIFTI='nifti'
    GIFTI='gifti'
    TIMECOURSE='timecourse'
    TASK='task'


class FileInputError(Exception):
    """
    Error in file inputs provided by user
    """
    def __init__(
        self, 
        message: str, 
        file_type: Literal[
            ExceptionFileTypes.NIFTI, 
            ExceptionFileTypes.GIFTI, 
            ExceptionFileTypes.TIMECOURSE, 
            ExceptionFileTypes.TASK
        ], 
        method: str
    ):
        super().__init__(message)
        self.message = message
        self.filename = file_type
        self.method = method

    def __str__(self):
        return f"{self.message} - {self.file_type} via {self.method}"


class FileUploadError(Exception):
    """
    Error in file upload
    """
    def __init__(
        self, 
        message: str, 
        file_type: Literal[
            ExceptionFileTypes.NIFTI, 
            ExceptionFileTypes.GIFTI, 
            ExceptionFileTypes.TIMECOURSE, 
            ExceptionFileTypes.TASK
        ], 
        method: str
    ):
        super().__init__(message)
        self.message = message
        self.filename = file_type
        self.method = method

    def __str__(self):
        return f"{self.message} - {self.file_type} via {self.method}"


class FileValidationError(Exception):
    """
    Error in file validation
    """
    def __init__(
        self, 
        message: str, 
        func_name: str,
        file_type: Literal[
            ExceptionFileTypes.NIFTI, 
            ExceptionFileTypes.GIFTI, 
            ExceptionFileTypes.TIMECOURSE, 
            ExceptionFileTypes.TASK
        ]
    ):
        super().__init__(message)
        self.message = message
        self.func_name = func_name
        self.file_type = file_type

    def __str__(self):
        return f"{self.message} - validation error in {self.func_name} for {self.file_type} file"
