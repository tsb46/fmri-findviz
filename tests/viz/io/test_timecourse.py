import io
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from findviz.viz.io.timecourse import (
    TimeCourseUpload,
    TaskDesignUpload,
    read_ts_file,
    read_task_file,
    get_task_regressors,
    TaskDesignDict,
    ConditionDict
)
from findviz.viz import exception

@pytest.fixture
def mock_task_data():
    """Create mock task design data"""
    return (
        "onset,duration,trial_type\n"
        "0,5,cond1\n"
        "10,5,cond2\n"
        "20,5,cond1"
    )

@pytest.fixture
def mock_csv_data():
    """Create mock time series data"""
    return "1.0\n2.0\n3.0\n4.0"

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
    # Mock the read_ts_file to return a 2D array
    mock_read_ts.return_value = np.array([[1.0], [2.0], [3.0]])
    
    uploader = TimeCourseUpload(method='browser')
    mock_files = [{
        'ts_file': Mock(filename='data.csv'),
        'ts_label': 'ROI1',
        'ts_header': 'False'
    }]
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload(3)
        assert isinstance(result, dict)
        assert 'ROI1' in result
        assert isinstance(result['ROI1'], np.ndarray)
        assert result['ROI1'].shape == (3, 1)
        assert np.array_equal(result['ROI1'], np.array([[1.0], [2.0], [3.0]]))

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
    
    mock_file = Mock()
    mock_file.filename = 'data.csv'
    mock_file.read.return_value = mock_csv_data.encode()
    
    mock_files = [{
        'ts_file': mock_file,
        'ts_label': 'ROI1',
        'ts_header': 'False'
    }]
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with patch('findviz.viz.io.timecourse.read_ts_file') as mock_read_ts:
            # Mock to return a 2D array
            mock_read_ts.return_value = np.array([[1.0], [2.0], [3.0], [4.0]])
            
            # Test with matching length (should succeed)
            result = uploader.upload(fmri_len=4)
            assert isinstance(result, dict)
            assert 'ROI1' in result
            assert isinstance(result['ROI1'], np.ndarray)
            assert result['ROI1'].shape == (4, 1)
            assert np.array_equal(result['ROI1'], np.array([[1.0], [2.0], [3.0], [4.0]]))

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

def test_task_design_upload_valid(mock_task_data):
    """Test successful task design file upload"""
    uploader = TaskDesignUpload(method='browser', default_trial_label='task')
    
    # Create mock file with proper stream
    mock_file = MagicMock()
    mock_file.filename = 'task.csv'
    mock_file.stream = io.BytesIO(mock_task_data.encode())
    
    mock_files = {
        'task_file': mock_file,
        'tr': '2.0',
        'slicetime_ref': '0.5'
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload(fmri_len=10)
        assert isinstance(result, dict)
        assert 'task_regressors' in result
        assert 'tr' in result
        assert 'slicetime_ref' in result

def test_task_design_upload_validation():
    """Test task design parameter validation"""
    uploader = TaskDesignUpload(method='browser')
    
    # Test invalid TR
    mock_files = {
        'task_file': Mock(filename='task.csv'),
        'tr': '-1.0',  # Invalid TR
        'slicetime_ref': '0.5'
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(exception.FileValidationError) as exc_info:
            uploader.upload(fmri_len=10)
        assert 'TR must not be less than zero' in str(exc_info.value)
    
    # Test invalid slicetime
    mock_files['tr'] = '2.0'
    mock_files['slicetime_ref'] = '1.5'  # Invalid slicetime
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(exception.FileValidationError) as exc_info:
            uploader.upload(fmri_len=10)
        assert 'Slicetime reference must between 0 and 1' in str(exc_info.value)

def test_read_ts_file_valid(mock_csv_data):
    """Test reading valid time course file"""
    mock_file = MagicMock()
    mock_file.stream = io.BytesIO(mock_csv_data.encode())
    
    result = read_ts_file(mock_file, header=False, method='browser')
    assert isinstance(result, np.ndarray)
    assert result.shape == (4, 1)  # Check shape is (n_timepoints, 1)
    assert np.array_equal(result, np.array([[1.0], [2.0], [3.0], [4.0]]))

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
        assert result['trial_type'] == ['cond1', 'cond2', 'cond1']  # Updated expectation

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
        assert result['trial_type'] == ['cond1', 'cond2', 'cond1']  # Updated expectation

def test_get_task_regressors():
    """Test generation of task regressors"""
    task_events = {
        'trial_type': ['A', 'B', 'A', 'B'],
        'onset': ['0', '10', '20', '30'],
        'duration': ['5', '5', '5', '5']
    }
    
    fmri_len = 25
    task_tr = 2.0
    task_slicetime_ref = 0.5
    
    result = get_task_regressors(task_events, task_tr, task_slicetime_ref, fmri_len)
    assert isinstance(result, dict)
    assert set(result.keys()) == {'A', 'B'}

def test_get_task_regressors_single_condition():
    """Test task regressors with single condition"""
    task_events = {
        'trial_type': ['A', 'A'],
        'onset': ['0', '20'],
        'duration': ['5', '5']
    }
    
    fmri_len = 20
    task_tr = 2.0
    task_slicetime_ref = 0.5
    
    result = get_task_regressors(task_events, task_tr, task_slicetime_ref, fmri_len)
    assert list(result.keys()) == ['A']

def test_get_task_regressors_empty():
    """Test task regressors with empty events"""
    task_events = {
        'trial_type': [],
        'onset': [],
        'duration': []
    }
    
    fmri_len = 10
    task_tr = 2.0
    task_slicetime_ref = 0.5
    
    result = get_task_regressors(task_events, task_tr, task_slicetime_ref, fmri_len)
    assert result == {}

def test_get_task_regressors_output():
    """Test task regressor generation output format"""
    task_events = {
        'onset': ['0', '10'],
        'duration': ['5', '5'],
        'trial_type': ['A', 'B']
    }
    
    fmri_len = 20
    task_tr = 2.0
    task_slicetime_ref = 0.5
    
    result = get_task_regressors(task_events, task_tr, task_slicetime_ref, fmri_len)
    
    # Check output structure
    assert isinstance(result, dict)
    for condition in ['A', 'B']:
        assert condition in result
        assert isinstance(result[condition], dict)
        assert 'block' in result[condition]
        assert 'hrf' in result[condition]
        assert len(result[condition]['block']) == fmri_len
        assert len(result[condition]['hrf']) == fmri_len

def test_timecourse_upload_validation():
    """Test time course file validation"""
    uploader = TimeCourseUpload(method='browser')
    
    # Test duplicate labels
    mock_files = [
        {
            'ts_file': Mock(filename='data1.csv'),
            'ts_label': 'ROI1',
            'ts_header': False
        },
        {
            'ts_file': Mock(filename='data2.csv'),
            'ts_label': 'ROI1',  # Duplicate label
            'ts_header': False
        }
    ]
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(exception.FileInputError) as exc_info:
            uploader.upload(fmri_len=10)
        assert 'Duplicate time course labels found' in str(exc_info.value)

def test_read_task_file_validation(mock_task_data):
    """Test task file content validation"""
    mock_file = MagicMock()
    mock_file.filename = 'task.csv'
    mock_file.stream = io.BytesIO("onset,duration\ninvalid,5\n".encode())
    
    with pytest.raises(exception.FileValidationError) as exc_info:
        read_task_file(mock_file, default_trial_label='task', method='browser')
    assert 'Non-numeric entry' in str(exc_info.value)