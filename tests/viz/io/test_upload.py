import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import nibabel as nib
from pathlib import Path
from findviz.viz.io.upload import FileUpload
from findviz.viz import exception
from findviz.viz.io import nifti, gifti, timecourse

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
    # Set upload_status to dictionary
    upload.upload_status = {
        "gifti": False,
        "nifti": True,
        "ts": False,
        "task": False
    }
    with pytest.raises(Exception, match='invalid is not a recognized file label'):
        upload.check_files('invalid')

def test_check_files_valid():
    """Test check_files with valid key"""
    upload = FileUpload(
        fmri_file_type='nifti',
        ts_status=True,
        task_status=True,
        method='browser'
    )
    # Set upload_status to dictionary
    upload.upload_status = {
        "gifti": False,
        "nifti": True,
        "ts": True,
        "task": False
    }
    assert upload.check_files('nifti') is True
    assert upload.check_files('ts') is True
    assert upload.check_files('task') is False

def test_hemisphere_no_upload():
    """Test hemisphere when no files have been uploaded"""
    upload = FileUpload(
        fmri_file_type='gifti',
        ts_status=False,
        task_status=False,
        method='browser'
    )
    with pytest.raises(AttributeError, match='No files have been uploaded!'):
        upload.hemisphere()

def test_hemisphere_nifti():
    """Test hemisphere with NIFTI files"""
    upload = FileUpload(
        fmri_file_type='nifti',
        ts_status=False,
        task_status=False,
        method='browser'
    )
    upload.upload_status = True  # Mock upload status
    with pytest.raises(AttributeError, match='hemisphere function not supported for nifti'):
        upload.hemisphere()

def test_hemisphere_gifti():
    """Test hemisphere with GIFTI files"""
    upload = FileUpload(
        fmri_file_type='gifti',
        ts_status=False,
        task_status=False,
        method='browser'
    )
    upload.upload_status = True  # Mock upload status
    
    # Test both hemispheres
    upload.fmri_uploader.left_input = True
    upload.fmri_uploader.right_input = True
    assert upload.hemisphere() == 'both'
    
    # Test left hemisphere only
    upload.fmri_uploader.left_input = True
    upload.fmri_uploader.right_input = False
    assert upload.hemisphere() == 'left'
    
    # Test right hemisphere only
    upload.fmri_uploader.left_input = False
    upload.fmri_uploader.right_input = True
    assert upload.hemisphere() == 'right'

@patch('findviz.viz.io.nifti.NiftiUpload.upload')
@patch('findviz.viz.io.timecourse.TimeCourseUpload.upload')
@patch('findviz.viz.io.timecourse.TaskDesignUpload.upload')
def test_upload_nifti_with_ts_and_task(mock_task_upload, mock_ts_upload, mock_nifti_upload):
    """Test upload with NIFTI files, time series, and task design"""
    # Create mock NIFTI data
    mock_nifti_data = MagicMock()
    mock_nifti_data.shape = (10, 10, 10, 20)  # 4D with 20 volumes
    
    # Setup mock returns
    mock_nifti_upload.return_value = {
        nifti.NiftiFiles.FUNC.value: mock_nifti_data,
        nifti.NiftiFiles.ANAT.value: MagicMock(),
        nifti.NiftiFiles.MASK.value: MagicMock()
    }
    mock_ts_upload.return_value = {'ROI1': np.random.rand(20, 1)}
    mock_task_upload.return_value = {
        'task_regressors': {'cond1': {'block': [0]*20, 'hrf': [0]*20}},
        'tr': 2.0,
        'slicetime_ref': 0.5
    }
    
    # Create uploader
    upload = FileUpload(
        fmri_file_type='nifti',
        ts_status=True,
        task_status=True,
        method='browser'
    )
    
    # Test upload
    result = upload.upload()
    
    # Verify calls and results
    mock_nifti_upload.assert_called_once()
    mock_ts_upload.assert_called_once_with(fmri_len=20, ts_files=None, ts_labels=None, ts_headers=None)
    mock_task_upload.assert_called_once_with(fmri_len=20, task_file=None, tr=None, slicetime_ref=None)
    
    assert 'nifti' in result
    assert 'ts' in result
    assert 'task' in result
    assert upload.upload_status is True

@patch('findviz.viz.io.gifti.GiftiUpload.upload')
def test_upload_gifti_error_handling(mock_gifti_upload):
    """Test error handling during upload"""
    # Setup mock to raise an error
    mock_gifti_upload.side_effect = exception.FileValidationError(
        'Mock validation error', 'test_func', 'gifti', ['left_gii_func']
    )
    
    # Create uploader
    upload = FileUpload(
        fmri_file_type='gifti',
        ts_status=False,
        task_status=False,
        method='browser'
    )
    
    # Test error propagation
    with pytest.raises(exception.FileValidationError) as exc_info:
        upload.upload()
    
    assert 'Mock validation error' in str(exc_info.value)
    assert upload.upload_status != True  # Should not be set to True on error