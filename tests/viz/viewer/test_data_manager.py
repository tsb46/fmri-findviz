"""Tests for the DataManager singleton class."""

import pytest
import numpy as np
import nibabel as nib

from findviz.viz.viewer.data_manager import DataManager
from tests.viz.conftest import (
    mock_nifti_4d,
    mock_nifti_3d,
    mock_gifti_func,
    mock_task_data
)

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    DataManager._instance = None
    yield

def test_singleton_pattern():
    """Test that DataManager implements singleton pattern correctly."""
    dm1 = DataManager()
    dm2 = DataManager()
    assert dm1 is dm2
    assert DataManager._instance is dm1

def test_initial_state():
    """Test initial state of DataManager."""
    dm = DataManager()
    assert dm.state is None
    assert dm.file_type is None

def test_create_nifti_state(mock_nifti_4d, mock_nifti_3d):
    """Test creation of NIFTI visualization state."""
    dm = DataManager()
    dm.create_nifti_state(
        func_img=mock_nifti_4d,
        anat_img=mock_nifti_3d,
        mask_img=mock_nifti_3d
    )
    
    assert dm.state is not None
    assert dm.state.file_type == 'nifti'
    assert dm.state.anat_input is True
    assert dm.state.mask_input is True
    assert 'func' in dm.state.nifti_data
    assert 'anat' in dm.state.nifti_data
    assert 'mask' in dm.state.nifti_data

def test_create_gifti_state(mock_gifti_func, mock_gifti_mesh):
    """Test creation of GIFTI visualization state."""
    dm = DataManager()
    dm.create_gifti_state(
        left_func_img=mock_gifti_func,
        right_func_img=mock_gifti_func,
        left_mesh=mock_gifti_mesh,
        right_mesh=mock_gifti_mesh
    )
    
    assert dm.state is not None
    assert dm.state.file_type == 'gifti'
    assert dm.state.left_input is True
    assert dm.state.right_input is True
    assert dm.state.vertices_left is not None
    assert dm.state.faces_left is not None
    assert dm.state.vertices_right is not None
    assert dm.state.faces_right is not None

def test_add_timeseries(mock_nifti_4d):
    """Test adding timeseries data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    
    ts_data = {
        'ROI1': [1.0, 2.0, 3.0],
        'ROI2': [4.0, 5.0, 6.0]
    }
    
    dm.add_timeseries(ts_data)
    assert dm.state.ts_enabled is True
    assert dm.state.ts_data == ts_data
    assert len(dm.state.ts_labels) == 2
    assert 'ROI1' in dm.state.ts_labels

def test_add_task_design(mock_nifti_4d):
    """Test adding task design data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)

    task_data = {
        'tr': 2.0,
        'slicetime_ref': 0.5,
        'task_regressors': {
            'A': {
                'block': [1, 1, 0, 0],
                'hrf': [0.1, 0.2, 0.1, 0]
            },
            'B': {
                'block': [0, 0, 1, 1],
                'hrf': [0, 0.1, 0.2, 0.1]
            }
        }
    }

    dm.add_task_design(task_data)
    
    assert dm.state.task_enabled
    assert set(dm.state.conditions) == {'A', 'B'}
    assert dm.state.task_data == task_data

def test_get_viewer_metadata_nifti(mock_nifti_4d, mock_nifti_3d):
    """Test getting viewer metadata for NIFTI state."""
    dm = DataManager()
    dm.create_nifti_state(mock_nifti_4d, mock_nifti_3d)
    
    metadata = dm.get_viewer_metadata()
    assert metadata['file_type'] == 'nifti'
    assert 'timepoints' in metadata
    assert 'global_min' in metadata
    assert 'global_max' in metadata
    assert 'slice_len' in metadata
    assert metadata['anat_input'] is True

def test_get_viewer_metadata_gifti(mock_gifti_func, mock_gifti_mesh):
    """Test getting viewer metadata for GIFTI state."""
    dm = DataManager()
    dm.create_gifti_state(mock_gifti_func, None, mock_gifti_mesh)
    
    metadata = dm.get_viewer_metadata()
    assert metadata['file_type'] == 'gifti'
    assert 'timepoints' in metadata
    assert 'global_min' in metadata
    assert 'global_max' in metadata
    assert metadata['left_input'] is True
    assert metadata['right_input'] is False
    assert metadata['vertices_left'] is not None
    assert metadata['faces_left'] is not None

def test_get_viewer_nifti_data_preprocessed(mock_nifti_4d):
    """Test getting viewer data with preprocessed data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    dm.store_fmri_preprocessed({'func': mock_nifti_4d})
    viewer_data = dm.get_viewer_data()
    assert viewer_data['is_fmri_preprocessed'] is True
    assert viewer_data['func_img'] == mock_nifti_4d

def test_get_viewer_gifti_data_preprocessed(mock_gifti_func, mock_gifti_mesh):
    """Test getting viewer data with preprocessed data."""
    dm = DataManager()
    dm.create_gifti_state(mock_gifti_func, None, mock_gifti_mesh)
    dm.store_fmri_preprocessed(
        {'left_func_img': mock_gifti_func, 'right_func_img': None}
        )
    viewer_data = dm.get_viewer_data()
    assert viewer_data['is_fmri_preprocessed'] is True
    assert viewer_data['left_func_img'] == mock_gifti_func
    assert viewer_data['right_func_img'] is None
    
def test_get_viewer_data_empty():
    """Test getting viewer data with no state."""
    dm = DataManager()
    viewer_data = dm.get_viewer_data()
    assert viewer_data == {}

def test_store_and_clear_preprocessed(mock_nifti_4d):
    """Test storing and clearing preprocessed data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    
    # Store preprocessed data
    preprocessed_data = {'func': mock_nifti_4d}
    dm.store_fmri_preprocessed(preprocessed_data)
    assert dm.state.fmri_preprocessed is True
    
    # Clear preprocessed data
    dm.clear_fmri_preprocessed()
    assert dm.state.fmri_preprocessed is False

def test_store_and_clear_ts_preprocessed(mock_nifti_4d):
    """Test storing and clearing preprocessed timecourse data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    dm.add_timeseries({'ROI1': [1.0, 2.0, 3.0]})
    
    # Store preprocessed data
    preprocessed_data = {'ROI1': [1.0, 2.0, 3.0]}
    dm.store_timecourse_preprocessed(preprocessed_data)
    assert dm.state.ts_preprocessed is True
    assert dm.state.ts_data_preprocessed == preprocessed_data

    # Clear preprocessed data
    dm.clear_timecourse_preprocessed()
    assert dm.state.ts_preprocessed is False
    assert dm.state.ts_data_preprocessed is None

def test_update_timecourse(mock_nifti_4d):
    """Test updating timecourse data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    
    # initialize timecourse data
    dm.add_timeseries({
        'ROI1': [1.0, 2.0, 3.0],
        'ROI2': [4.0, 5.0, 6.0]
    })
    
    timecourse = [1.0, 2.0, 3.0]
    label = "New ROI"
    dm.update_timecourse(timecourse, label)
    
    assert label in dm.state.ts_labels
    assert dm.state.ts_data[label] == timecourse

def test_pop_timecourse(mock_nifti_4d):
    """Test popping timecourse data."""
    dm = DataManager()
    dm.create_nifti_state(func_img=mock_nifti_4d)
    
    # initialize timecourse data
    dm.add_timeseries({
        'ROI1': [1.0, 2.0, 3.0],
        'ROI2': [4.0, 5.0, 6.0]
    })

    # Add two timecourses
    dm.update_timecourse([1.0, 2.0, 3.0], "ROI3")
    dm.update_timecourse([4.0, 5.0, 6.0], "ROI4")
    
    # Pop the last one
    dm.pop_timecourse()
    
    assert "ROI4" not in dm.state.ts_labels
    assert len(dm.state.ts_labels) == 3
    assert "ROI1" in dm.state.ts_labels
    assert "ROI2" in dm.state.ts_labels
    assert "ROI3" in dm.state.ts_labels
