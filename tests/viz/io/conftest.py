"""
Pytest fixtures for IO module tests.
"""
import pytest
import numpy as np
import nibabel as nib

@pytest.fixture
def mock_nifti_4d():
    """Create a mock 4D nifti image"""
    data = np.random.rand(10, 10, 10, 100)  # 4D data
    return nib.Nifti1Image(data, affine=np.eye(4))

@pytest.fixture
def mock_nifti_3d():
    """Create a mock 3D nifti image"""
    data = np.random.rand(10, 10, 10)  # 3D data
    return nib.Nifti1Image(data, affine=np.eye(4))

@pytest.fixture
def mock_gifti_func():
    """Create a mock functional gifti image"""
    data = [np.random.rand(100).astype(np.float32) for _ in range(10)]  # 10 timepoints
    arrays = [nib.gifti.GiftiDataArray(d) for d in data]
    return nib.gifti.GiftiImage(darrays=arrays)

@pytest.fixture
def mock_gifti_mesh():
    """Create a mock mesh gifti image"""
    coords = np.random.rand(100, 3).astype(np.float32)  # 100 vertices
    faces = np.random.randint(0, 99, (50, 3)).astype(np.int32)  # 50 triangles
    arrays = [
        nib.gifti.GiftiDataArray(coords),
        nib.gifti.GiftiDataArray(faces)
    ]
    return nib.gifti.GiftiImage(darrays=arrays)

@pytest.fixture
def mock_csv_data():
    """Create mock CSV data"""
    return "1.0\n2.0\n3.0\n4.0\n"

@pytest.fixture
def mock_task_data():
    """Create mock task design data"""
    return "onset,duration,trial_type\n0,1,A\n2,1,B\n4,1,A\n"