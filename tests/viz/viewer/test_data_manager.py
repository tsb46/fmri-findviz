"""Tests for the DataManager singleton class."""

import pytest
import numpy as np
import nibabel as nib

from findviz.viz.viewer.data_manager import DataManager, ImageMetadata

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    DataManager._instance = None
    yield

@pytest.fixture
def mock_nifti_4d():
    """Create a mock 4D NIFTI image."""
    data = np.random.rand(10, 10, 10, 5)  # 5 timepoints
    return nib.Nifti1Image(data, np.eye(4))

@pytest.fixture
def mock_nifti_3d():
    """Create a mock 3D NIFTI image."""
    data = np.random.rand(10, 10, 10)
    return nib.Nifti1Image(data, np.eye(4))

@pytest.fixture
def mock_gifti_func():
    """Create a mock GIFTI functional image."""
    arrays = [
        nib.gifti.GiftiDataArray(np.random.rand(100).astype(np.float32))
        for _ in range(5)  # 5 timepoints
    ]
    return nib.gifti.GiftiImage(darrays=arrays)

@pytest.fixture
def mock_gifti_mesh():
    """Create a mock GIFTI mesh."""
    vertices = nib.gifti.GiftiDataArray(np.random.rand(100, 3).astype(np.float32))
    faces = nib.gifti.GiftiDataArray(np.random.randint(0, 99, (50, 3)).astype(np.int32))
    return nib.gifti.GiftiImage(darrays=[vertices, faces])

def test_singleton_pattern():
    """Test that DataManager implements singleton pattern correctly."""
    dm1 = DataManager()
    dm2 = DataManager()
    assert dm1 is dm2
    assert DataManager._instance is dm1

def test_initial_state():
    """Test initial state of DataManager."""
    dm = DataManager()
    assert dm._state is None
    assert isinstance(dm._preprocessed, dict)
    assert len(dm._preprocessed) == 0

def test_create_nifti_state(mock_nifti_4d, mock_nifti_3d):
    """Test creation of NIFTI visualization state."""
    dm = DataManager()
    viewer_data = dm.create_nifti_state(
        func_img=mock_nifti_4d,
        anat_img=mock_nifti_3d,
        mask_img=mock_nifti_3d
    )
    
    assert dm._state is not None
    assert dm._state.file_type == 'nifti'
    assert isinstance(dm._state.metadata, ImageMetadata)
    assert len(dm._state.metadata.timepoints) == 5
    assert dm._state.anat_input is True
    assert dm._state.mask_input is True

def test_create_gifti_state(mock_gifti_func, mock_gifti_mesh):
    """Test creation of GIFTI visualization state."""
    dm = DataManager()
    dm.create_gifti_state(
        left_func=mock_gifti_func,
        right_func=mock_gifti_func,
        left_mesh=mock_gifti_mesh,
        right_mesh=mock_gifti_mesh
    )
    
    assert dm._state is not None
    assert dm._state.file_type == 'gifti'
    assert isinstance(dm._state.metadata, ImageMetadata)
    assert len(dm._state.metadata.timepoints) == 5
    assert dm._state.left_input is True
    assert dm._state.right_input is True
    assert dm._state.vertices_left is not None
    assert dm._state.faces_left is not None

def test_add_timeseries(mock_nifti_4d):
    """Test adding timeseries data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    
    ts_data = {
        'ROI1': np.random.rand(5),
        'ROI2': np.random.rand(5)
    }
    
    dm.add_timeseries(ts_data)
    assert dm._state.ts_enabled is True
    assert len(dm._state.timeseries) == 2
    assert len(dm._state.ts_labels) == 2
    assert 'ROI1' in dm._state.ts_labels

def test_add_task_design(mock_nifti_4d):
    """Test adding task design data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    
    task_data = {
        'onset': [0, 10, 20],
        'duration': [5, 5, 5],
        'trial_type': ['A', 'B', 'A']
    }
    
    dm.add_task_design(task_data)
    assert dm._state.task_enabled is True
    assert dm._state.task_data == task_data

def test_get_viewer_data_nifti(mock_nifti_4d, mock_nifti_3d):
    """Test getting viewer data for NIFTI state."""
    dm = DataManager()
    dm.create_nifti_state(mock_nifti_4d, mock_nifti_3d)
    
    viewer_data = dm.get_viewer_data()
    assert viewer_data['file_type'] == 'nifti'
    assert 'timepoints' in viewer_data
    assert 'global_min' in viewer_data
    assert 'global_max' in viewer_data
    assert 'slice_len' in viewer_data
    assert viewer_data['anat_input'] is True

def test_get_viewer_data_gifti(mock_gifti_func, mock_gifti_mesh):
    """Test getting viewer data for GIFTI state."""
    dm = DataManager()
    dm.create_gifti_state(mock_gifti_func, None, mock_gifti_mesh)
    
    viewer_data = dm.get_viewer_data()
    assert viewer_data['file_type'] == 'gifti'
    assert 'timepoints' in viewer_data
    assert 'global_min' in viewer_data
    assert 'global_max' in viewer_data
    assert viewer_data['left_input'] is True
    assert viewer_data['right_input'] is False
    assert viewer_data['vertices_left'] is not None
    assert viewer_data['faces_left'] is not None

def test_get_viewer_data_empty():
    """Test getting viewer data with no state."""
    dm = DataManager()
    dm._state = None  # Explicitly set state to None
    viewer_data = dm.get_viewer_data()
    assert viewer_data == {}

def test_state_property():
    """Test the state property getter."""
    dm = DataManager()
    dm._state = None  # Explicitly set state to None
    assert dm.state is None
