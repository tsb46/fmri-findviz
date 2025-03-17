"""Shared fixtures for viz module tests"""
import pytest
import numpy as np
import nibabel as nib
from nibabel.gifti import GiftiImage, GiftiDataArray

@pytest.fixture
def mock_nifti_4d():
    """Create a mock 4D NIFTI image"""
    data = np.random.rand(10, 10, 10, 5)  # x, y, z, time
    return nib.Nifti1Image(data, affine=np.eye(4))

@pytest.fixture
def mock_nifti_3d():
    """Create a mock 3D NIFTI image"""
    data = np.random.rand(10, 10, 10)  # x, y, z
    return nib.Nifti1Image(data, affine=np.eye(4))

@pytest.fixture
def mock_gifti_func():
    """Create a mock functional GIFTI image"""
    # Create multiple data arrays to simulate time points
    darrays = []
    for _ in range(5):  # 5 timepoints
        data = np.random.rand(100).astype(np.float32)  # 100 vertices, 1D array
        darray = GiftiDataArray(data)
        darrays.append(darray)
    
    return GiftiImage(darrays=darrays)

@pytest.fixture
def mock_nifti_mask():
    """Create binary mock 3D NIFTI mask image"""
    data = np.zeros((10, 10, 10))  # x, y, z
    data[2:8, 2:8, 2:8] = 1  # 6x6x6 cube of 1s
    return nib.Nifti1Image(data, affine=np.eye(4))

@pytest.fixture
def mock_gifti_mesh():
    """Create a mock mesh GIFTI image"""
    # Create vertices array
    vertices = np.random.rand(100, 3).astype(np.float32)  # 100 vertices, 3 coordinates
    vertices_darray = GiftiDataArray(vertices)
    
    # Create faces array
    faces = np.random.randint(0, 100, (50, 3)).astype(np.float32)  # 50 faces, 3 vertices each
    faces_darray = GiftiDataArray(faces)
    
    return GiftiImage(darrays=[vertices_darray, faces_darray])

# IO-specific fixtures

@pytest.fixture
def mock_csv_data():
    """Create mock CSV data"""
    return "1.0\n2.0\n3.0\n4.0\n"

@pytest.fixture
def mock_task_events():
    """Create mock task events data"""
    return {
        'onset': [0, 30, 60],
        'duration': [15, 15, 15],
        'trial_type': ['cond1', 'cond2', 'cond1']
    }

@pytest.fixture
def mock_task_data():
    """Create mock task design data as CSV string"""
    return "onset,duration,trial_type\n0,15,cond1\n30,15,cond2\n60,15,cond1\n"

@pytest.fixture
def mock_task_design_dict():
    """Create mock task design dictionary"""
    return {
        'task_regressors': {
            'cond1': {
                'block': [1.0, 0.0, 1.0],
                'hrf': [0.8, 0.2, 0.8]
            },
            'cond2': {
                'block': [0.0, 1.0, 0.0],
                'hrf': [0.2, 0.8, 0.2]
            }
        },
        'tr': 2.0,
        'slicetime_ref': 0.5
    }

# Viewer-specific fixtures
@pytest.fixture
def mock_viewer_metadata_nifti():
    """Create mock viewer metadata for NIFTI"""
    return {
        'file_type': 'nifti',
        'anat_input': True,
        'mask_input': True,
        'x_slice_idx': 32,
        'y_slice_idx': 32,
        'z_slice_idx': 20,
        'view_state': 'ortho',
        'montage_slice_dir': 'z',
        'timepoints': [0, 1, 2],
        'preprocessed': False,
        'global_min': -1.0,
        'global_max': 1.0,
        'slice_len': {'x': 64, 'y': 64, 'z': 40},
        'ts_enabled': False,
        'task_enabled': False
    }

@pytest.fixture
def mock_viewer_metadata_gifti():
    """Create mock viewer metadata for GIFTI"""
    return {
        'file_type': 'gifti',
        'left_input': True,
        'right_input': True,
        'vertices_left': [0.0, 1.0, 2.0],
        'faces_left': [0, 1, 2],
        'vertices_right': [3.0, 4.0, 5.0],
        'faces_right': [3, 4, 5],
        'timepoints': [0, 1, 2],
        'preprocessed': False,
        'global_min': 0.0,
        'global_max': 1.0,
        'ts_enabled': False,
        'task_enabled': False
    } 