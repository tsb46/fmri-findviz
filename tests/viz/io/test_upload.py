import pytest
from findviz.viz.io.upload import FileUpload

def test_file_upload_init_valid():
    """Test FileUpload initialization with valid parameters"""
    upload = FileUpload(
        fmri_file_type='nifti',
        ts_status=True,
        task_status=True,
        method='browser'
    )
    assert upload.fmri_file_type == 'nifti'
    assert upload.ts_status is True
    assert upload.task_status is True
    assert upload.method == 'browser'
    assert upload.upload_status is False

def test_file_upload_init_invalid_fmri_type():
    """Test FileUpload initialization with invalid fMRI file type"""
    with pytest.raises(ValueError, match='unrecognized fmri file type'):
        FileUpload(
            fmri_file_type='invalid',
            ts_status=True,
            task_status=True,
            method='browser'
        )

def test_check_files_no_upload():
    """Test check_files when no files have been uploaded"""
    upload = FileUpload(
        fmri_file_type='nifti',
        ts_status=True,
        task_status=True,
        method='browser'
    )
    with pytest.raises(AttributeError, match='No files have been uploaded!'):
        upload.check_files('nifti')

def test_check_files_invalid_key():
    """Test check_files with invalid key"""
    upload = FileUpload(
        fmri_file_type='nifti',
        ts_status=True,
        task_status=True,
        method='browser'
    )
    upload.upload_status = {'nifti': True}  # Mock upload status
    with pytest.raises(Exception, match='invalid is not a recognized file label'):
        upload.check_files('invalid')