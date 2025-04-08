"""
Tests for exception.py module
"""
import pytest
from findviz.viz.exception import (
    ExceptionFileTypes,
    DataRequestError,
    FileInputError,
    FileUploadError,
    FileValidationError,
    FVStateVersionIncompatibleError,
    NiftiMaskError,
    ParameterInputError,
    PreprocessInputError,
    PeakFinderNoPeaksFoundError
)


def test_exception_file_types_enum():
    """Test ExceptionFileTypes enum values"""
    assert ExceptionFileTypes.NIFTI.value == 'nifti'
    assert ExceptionFileTypes.GIFTI.value == 'gifti'
    assert ExceptionFileTypes.TIMECOURSE.value == 'timecourse'
    assert ExceptionFileTypes.TASK.value == 'task'
    assert ExceptionFileTypes.NIFTI_GIFTI_CIFTI.value == 'nifti/gifti/cifti'
    assert ExceptionFileTypes.CIFTI.value == 'cifti'


def test_data_request_error():
    """Test DataRequestError class"""
    error = DataRequestError(
        message="Missing data in request",
        fmri_file_type="nifti",
        route="upload",
        input_field="file-input"
    )
    
    assert error.message == "Missing data in request"
    assert error.fmri_file_type == "nifti"
    assert error.route == "upload"
    assert error.input_field == "file-input"
    
    # Test string representation
    error_str = str(error)
    assert "Missing data in request" in error_str
    assert "file-input" in error_str
    assert "nifti" in error_str
    assert "upload" in error_str


def test_file_input_error():
    """Test FileInputError class"""
    # Test with all parameters
    error = FileInputError(
        message="Invalid file input",
        file_type=ExceptionFileTypes.NIFTI.value,
        method="browser",
        field=["file-input"],
        index=[0]
    )
    
    assert error.message == "Invalid file input"
    assert error.file_type == "nifti"
    assert error.method == "browser"
    assert error.field == ["file-input"]
    assert error.index == [0]
    
    # Test string representation
    error_str = str(error)
    assert "Invalid file input" in error_str
    assert "nifti" in error_str
    assert "browser" in error_str
    
    # Test with minimal parameters
    error = FileInputError(
        message="Invalid file input",
        file_type=ExceptionFileTypes.GIFTI.value,
        method="cli"
    )
    
    assert error.message == "Invalid file input"
    assert error.file_type == "gifti"
    assert error.method == "cli"
    assert error.field is None
    assert error.index is None
    
    # Test with integer index
    error = FileInputError(
        message="Invalid file input",
        file_type=ExceptionFileTypes.TIMECOURSE.value,
        method="browser",
        field=["time-course"],
        index=2
    )
    
    assert error.index == [2]
    
    # Test with invalid index type
    with pytest.raises(AttributeError):
        FileInputError(
            message="Invalid file input",
            file_type=ExceptionFileTypes.TIMECOURSE.value,
            method="browser",
            field=["time-course"],
            index="not-an-integer"
        )


def test_file_upload_error():
    """Test FileUploadError class"""
    # Test with all parameters
    error = FileUploadError(
        message="File upload failed",
        file_type=ExceptionFileTypes.TASK.value,
        method="browser",
        field=["task-file"],
        index=[0]
    )
    
    assert error.message == "File upload failed"
    assert error.file_type == "task"
    assert error.method == "browser"
    assert error.field == ["task-file"]
    assert error.index == [0]
    
    # Test string representation
    error_str = str(error)
    assert "File upload failed" in error_str
    assert "task" in error_str
    assert "browser" in error_str
    
    # Test with minimal parameters
    error = FileUploadError(
        message="File upload failed",
        file_type=ExceptionFileTypes.CIFTI.value,
        method="cli"
    )
    
    assert error.message == "File upload failed"
    assert error.file_type == "cifti"
    assert error.method == "cli"
    assert error.field is None
    assert error.index is None
    
    # Test with integer index
    error = FileUploadError(
        message="File upload failed",
        file_type=ExceptionFileTypes.NIFTI_GIFTI_CIFTI.value,
        method="browser",
        field=["file-input"],
        index=1
    )
    
    assert error.index == [1]
    
    # Test with invalid index type
    with pytest.raises(AttributeError):
        FileUploadError(
            message="File upload failed",
            file_type=ExceptionFileTypes.NIFTI.value,
            method="browser",
            field=["file-input"],
            index="not-an-integer"
        )


def test_file_validation_error():
    """Test FileValidationError class"""
    # Test with all parameters
    error = FileValidationError(
        message="File validation failed",
        func_name="validate_nifti",
        file_type=ExceptionFileTypes.NIFTI.value,
        field=["nifti-file"],
        index=[0]
    )
    
    assert error.message == "File validation failed"
    assert error.func_name == "validate_nifti"
    assert error.file_type == "nifti"
    assert error.field == ["nifti-file"]
    assert error.index == [0]
    
    # Test string representation
    error_str = str(error)
    assert "File validation failed" in error_str
    assert "validate_nifti" in error_str
    assert "nifti" in error_str
    
    # Test with minimal parameters
    error = FileValidationError(
        message="File validation failed",
        func_name="validate_gifti",
        file_type=ExceptionFileTypes.GIFTI.value
    )
    
    assert error.message == "File validation failed"
    assert error.func_name == "validate_gifti"
    assert error.file_type == "gifti"
    assert error.field is None
    assert error.index is None
    
    # Test with integer index
    error = FileValidationError(
        message="File validation failed",
        func_name="validate_timecourse",
        file_type=ExceptionFileTypes.TIMECOURSE.value,
        field=["time-course"],
        index=3
    )
    
    assert error.index == [3]
    
    # Test with invalid index type
    with pytest.raises(AttributeError):
        FileValidationError(
            message="File validation failed",
            func_name="validate_task",
            file_type=ExceptionFileTypes.TASK.value,
            field=["task-file"],
            index="not-an-integer"
        )


def test_fv_state_version_incompatible_error():
    """Test FVStateVersionIncompatibleError class"""
    error = FVStateVersionIncompatibleError(
        message="State file version incompatible",
        expected_version="2.0",
        current_version="1.0"
    )
    
    assert error.message == "State file version incompatible"
    assert error.expected_version == "2.0"
    assert error.current_version == "1.0"
    
    # Test string representation
    error_str = str(error)
    assert "State file version incompatible" in error_str
    assert "expected version: 2.0" in error_str
    assert "current version: 1.0" in error_str


def test_nifti_mask_error():
    """Test NiftiMaskError class"""
    error = NiftiMaskError(
        message="Mask not provided for nifti processing"
    )
    
    assert error.message == "Mask not provided for nifti processing"
    
    # Test string representation
    error_str = str(error)
    assert "Nifti mask error: Mask not provided for nifti processing" in error_str


def test_parameter_input_error():
    """Test ParameterInputError class"""
    # Test with parameters
    error = ParameterInputError(
        message="Invalid parameter input",
        parameters=["param1", "param2"]
    )
    
    assert error.message == "Invalid parameter input"
    assert error.parameters == ["param1", "param2"]
    
    # Test string representation
    error_str = str(error)
    assert "Parameter input error: Invalid parameter input" in error_str
    assert "param1" in error_str
    assert "param2" in error_str
    
    # Test without parameters
    error = ParameterInputError(
        message="Invalid parameter input"
    )
    
    assert error.message == "Invalid parameter input"
    assert error.parameters is None
    
    # Test string representation without parameters
    error_str = str(error)
    assert "Parameter input error: Invalid parameter input" in error_str


def test_preprocess_input_error():
    """Test PreprocessInputError class"""
    # Test with preprocess_method
    error = PreprocessInputError(
        message="Invalid preprocessing input",
        preprocess_method="normalization"
    )
    
    assert error.message == "Invalid preprocessing input"
    assert error.preprocess_method == "normalization"
    
    # Test string representation
    error_str = str(error)
    assert "Preprocess input error: Invalid preprocessing input" in error_str
    assert "normalization" in error_str
    
    # Test without preprocess_method
    error = PreprocessInputError(
        message="Invalid preprocessing input"
    )
    
    assert error.message == "Invalid preprocessing input"
    assert error.preprocess_method is None
    
    # Test string representation without preprocess_method
    error_str = str(error)
    assert "Preprocess input error: Invalid preprocessing input" in error_str


def test_peak_finder_no_peaks_found_error():
    """Test PeakFinderNoPeaksFoundError class"""
    # Test with default message
    error = PeakFinderNoPeaksFoundError()
    
    assert error.message == "No peaks found. Please check your input parameters."
    
    # Test string representation
    error_str = str(error)
    assert "Peak finder error: No peaks found" in error_str
    
    # Test with custom message
    error = PeakFinderNoPeaksFoundError(
        message="Custom peak finder error message"
    )
    
    assert error.message == "Custom peak finder error message"
    
    # Test string representation with custom message
    error_str = str(error)
    assert "Peak finder error: Custom peak finder error message" in error_str
