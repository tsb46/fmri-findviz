import io
import pytest
import numpy as np
from unittest.mock import Mock, patch
from findviz.viz.io.timecourse import (
    TimeCourseUpload,
    TaskDesignUpload,
    read_ts_file,
    read_task_file
)
from findviz.viz import exception

def test_timecourse_upload_init():
    """Test TimeCourseUpload initialization"""
    uploader = TimeCourseUpload(method='browser')
    assert uploader.method == 'browser'

def test_task_design_upload_init():
    """Test TaskDesignUpload initialization"""
    uploader = TaskDesignUpload(method='browser', default_trial_label='task')
    assert uploader.method == 'browser'
    assert uploader.default_trial_label == 'task'

@patch('findviz.viz.io.timecourse.read_ts_file')
def test_timecourse_upload_valid(mock_read_ts):
    """Test successful time course file upload"""
    mock_read_ts.return_value = np.array([[1.0], [2.0], [3.0]])
    
    uploader = TimeCourseUpload(method='browser')
    mock_files = [{
        'ts_file': Mock(filename='data.csv'),
        'ts_label': 'ROI1',
        'ts_header': 'False'
    }]
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload(3)
        assert len(result) == 1
        label = list(result[0].keys())[0]
        assert label == 'ROI1'
        assert result[0][label].shape == (3, 1)

def test_timecourse_upload_duplicate_labels():
    """Test time course upload with duplicate labels"""
    uploader = TimeCourseUpload(method='browser')
    mock_files = [
        {
            'ts_file': Mock(filename='data1.csv'),
            'ts_label': 'ROI1',
            'ts_header': 'False'
        },
        {
            'ts_file': Mock(filename='data2.csv'),
            'ts_label': 'ROI1',  # Duplicate label
            'ts_header': 'False'
        }
    ]
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(exception.FileInputError):
            uploader.upload(10)

def test_timecourse_upload_length_mismatch(mock_csv_data):
    """Test time course upload with length mismatch"""
    uploader = TimeCourseUpload(method='browser')
    
    # Create mock file with length 4 (from mock_csv_data)
    mock_file = Mock()
    mock_file.filename = 'data.csv'
    mock_file.read.return_value = mock_csv_data.encode()
    
    # Create mock files list with one time course
    mock_files = [{
        'ts_file': mock_file,
        'ts_label': 'ROI1',
        'ts_header': 'False'
    }]
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with patch('findviz.viz.io.timecourse.read_ts_file') as mock_read_ts:
            # Mock read_ts_file to return array of length 4
            mock_read_ts.return_value = np.array([[1.0], [2.0], [3.0], [4.0]])
            
            # Test with matching length (should succeed)
            result = uploader.upload(fmri_len=4)
            assert len(result) == 1
            label = list(result[0].keys())[0]
            assert label == 'ROI1'
            assert result[0][label].shape == (4, 1)
            
            # Test with mismatched length (should raise error)
            with pytest.raises(exception.FileValidationError) as exc_info:
                uploader.upload(fmri_len=10)
                assert "length of ts_file (4) is not the same length as fmri volumes (10)" in str(exc_info.value)

def test_timecourse_upload_multiple_length_mismatch():
    """Test multiple time course uploads with length mismatch"""
    uploader = TimeCourseUpload(method='browser')
    
    # Create mock files with different lengths
    mock_files = [
        {
            'ts_file': Mock(filename='data1.csv'),
            'ts_label': 'ROI1',
            'ts_header': 'False'
        },
        {
            'ts_file': Mock(filename='data2.csv'),
            'ts_label': 'ROI2',
            'ts_header': 'False'
        }
    ]
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with patch('findviz.viz.io.timecourse.read_ts_file') as mock_read_ts:
            # Mock read_ts_file to return arrays of different lengths
            mock_read_ts.side_effect = [
                np.array([[1.0], [2.0], [3.0]]),  # Length 3
                np.array([[1.0], [2.0], [3.0], [4.0]])  # Length 4
            ]
            
            # Test with mismatched length
            with pytest.raises(exception.FileValidationError) as exc_info:
                uploader.upload(fmri_len=3)
                assert "length of ts_file (4) is not the same length as fmri volumes (3)" in str(exc_info.value)

@patch('findviz.viz.io.timecourse.read_task_file')
def test_task_design_upload_valid(mock_read_task):
    """Test successful task design file upload"""
    mock_read_task.return_value = {
        'onset': [0, 2, 4],
        'duration': [1, 1, 1],
        'trial_type': ['A', 'B', 'A']
    }
    
    uploader = TaskDesignUpload(method='browser')
    mock_files = {
        'task_file': Mock(filename='task.csv'),
        'tr': '2.0',
        'slicetime_ref': '0.5'
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload()
        assert 'onset' in result
        assert 'duration' in result
        assert 'trial_type' in result

def test_task_design_upload_invalid_tr():
    """Test task design upload with invalid TR"""
    uploader = TaskDesignUpload(method='browser')
    mock_files = {
        'task_file': Mock(filename='task.csv'),
        'tr': '-1.0',  # Invalid TR
        'slicetime_ref': '0.5'
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(exception.FileValidationError):
            uploader.upload()

def test_read_ts_file_valid(mock_csv_data):
    """Test reading valid time course file"""
    mock_file = Mock()
    mock_file.read.return_value = mock_csv_data.encode()
    
    with patch('findviz.viz.io.utils.get_csv_reader') as mock_reader:
        mock_reader.return_value = [[x] for x in mock_csv_data.strip().split('\n')]
        result = read_ts_file(mock_file, header=False, method='browser')
        assert isinstance(result, np.ndarray)
        assert result.shape == (4, 1)

def test_read_task_file_valid(mock_task_data):
    """Test reading valid task design file"""
    # Create a mock file object with proper attributes
    mock_file = Mock()
    mock_file.filename = 'task.csv'
    mock_file.name = 'task.csv'
    mock_file.stream = io.BytesIO(mock_task_data.encode())
    
    with patch('findviz.viz.io.utils.get_csv_reader') as mock_reader:
        # Mock the CSV reader to return an iterator of rows
        mock_reader.return_value = iter([
            row.split(',') 
            for row in mock_task_data.strip().split('\n')
        ])
        
        result = read_task_file(mock_file, default_trial_label='task', method='browser')
        
        # Verify the result
        assert 'onset' in result
        assert 'duration' in result
        assert 'trial_type' in result
        assert len(result['onset']) == 3
        assert result['trial_type'] == ['A', 'B', 'A']

def test_read_task_file_valid_alternative(mock_task_data):
    """Test reading valid task design file with complete mocking"""
    class MockFile:
        def __init__(self, filename, content):
            self.filename = filename
            self.stream = io.BytesIO(content.encode('utf-8'))
        
        def read(self):
            return self.stream.read()
    
    # Create mock file with proper attributes
    mock_file = MockFile('task.csv', mock_task_data)
    
    with patch('findviz.viz.io.utils.get_csv_reader') as mock_reader:
        # Mock the CSV reader to return an iterator of rows
        mock_reader.return_value = iter([
            row.split(',') 
            for row in mock_task_data.strip().split('\n')
        ])
        
        result = read_task_file(mock_file, default_trial_label='task', method='browser')
        
        # Verify the result
        assert 'onset' in result
        assert 'duration' in result
        assert 'trial_type' in result
        assert len(result['onset']) == 3
        assert result['trial_type'] == ['A', 'B', 'A']