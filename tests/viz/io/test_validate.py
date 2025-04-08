import pytest
import numpy as np
import nibabel as nib
from findviz.viz.io.validate import (
    validate_gii_func_ext,
    validate_gii_mesh_ext,
    validate_gii_file_inputs,
    validate_gii_func,
    validate_gii_mesh,
    validate_gii_func_len,
    validate_nii_ext,
    validate_nii_4d,
    validate_nii_3d,
    validate_nii_same_dim_len,
    validate_nii_brain_mask,
    validate_task_ext,
    validate_task_header_required_cols,
    validate_task_header_duplicates,
    validate_task_tr,
    validate_task_slicetime,
    validate_ts_task_length,
    validate_ts_ext,
    validate_ts_single_col,
    validate_ts_numeric,
    validate_ts_fmri_length,
    validate_cii_brainmodel_axis,
    validate_cii_dtseries_ext,
    validate_cii_file_inputs,
    validate_cii_hemisphere,
    validate_gii_func_mesh_len
)
from unittest.mock import Mock, patch

# GIFTI validation tests
def test_validate_gii_func_ext():
    """Test validation of GIFTI functional file extensions"""
    assert validate_gii_func_ext('data.func.gii') is True
    assert validate_gii_func_ext('data.gii') is False
    assert validate_gii_func_ext('data.surf.gii') is False
    assert validate_gii_func_ext('data.txt') is False
    assert validate_gii_func_ext('data.func.gii.gz') is False

def test_validate_gii_mesh_ext():
    """Test validation of GIFTI mesh file extensions"""
    assert validate_gii_mesh_ext('data.surf.gii') is True
    assert validate_gii_mesh_ext('data.gii') is False
    assert validate_gii_mesh_ext('data.func.gii') is False
    assert validate_gii_mesh_ext('data.txt') is False
    assert validate_gii_mesh_ext('data.surf.gii.gz') is False

def test_validate_gii_file_inputs():
    """Test validation of GIFTI file input combinations"""
    # Create mock file objects
    left_mesh = object()
    right_mesh = object()
    left_func = object()
    right_func = object()
    
    # Test valid combinations
    msg, missing, valid = validate_gii_file_inputs(left_mesh, None, left_func, None)
    assert valid is True
    assert missing == []
    
    msg, missing, valid = validate_gii_file_inputs(left_mesh, right_mesh, left_func, right_func)
    assert valid is True
    assert missing == []
    
    # Test invalid combinations
    msg, missing, valid = validate_gii_file_inputs(None, None, left_func, None)
    assert valid is False
    assert "mesh file must be provided" in msg
    assert 'left_mesh' in missing or 'right_mesh' in missing
    
    msg, missing, valid = validate_gii_file_inputs(left_mesh, None, None, right_func)
    assert valid is False
    assert "func file must be provided" in msg
    assert 'left_func' in missing or 'right_func' in missing

def test_validate_gii_func(mock_gifti_func):
    """Test validation of GIFTI functional data structure"""
    assert validate_gii_func(mock_gifti_func) is True
    
    # Test invalid case with 2D data arrays
    invalid_arrays = [
        nib.gifti.GiftiDataArray(np.random.rand(10, 10).astype(np.float32)) for _ in range(5)
    ]
    invalid_gii = nib.gifti.GiftiImage(darrays=invalid_arrays)
    assert validate_gii_func(invalid_gii) is False

def test_validate_gii_mesh(mock_gifti_mesh):
    """Test validation of GIFTI mesh data structure"""
    assert validate_gii_mesh(mock_gifti_mesh) is True
    
    # Test invalid case with wrong number of arrays
    invalid_arrays = [nib.gifti.GiftiDataArray(np.random.rand(10, 3).astype(np.int32))]
    invalid_gii = nib.gifti.GiftiImage(darrays=invalid_arrays)
    assert validate_gii_mesh(invalid_gii) is False

def test_validate_gii_func_len():
    """test validation of left and right hemisphere func equal length"""
    data_len10 = [np.random.rand(100).astype(np.float32) for _ in range(10)]
    data_len20 = [np.random.rand(100).astype(np.float32) for _ in range(20)]
    gii_len10 = nib.gifti.GiftiImage(
        darrays=[nib.gifti.GiftiDataArray(d) for d in data_len10]
    )
    gii_len20 = nib.gifti.GiftiImage(
        darrays=[nib.gifti.GiftiDataArray(d) for d in data_len20]
    )
    assert validate_gii_func_len(gii_len10, gii_len10) is True
    assert validate_gii_func_len(gii_len20, gii_len10) is False

# NIFTI validation tests
def test_validate_nii_ext():
    """Test validation of NIFTI file extensions"""
    assert validate_nii_ext('data.nii') is True
    assert validate_nii_ext('data.nii.gz') is True
    assert validate_nii_ext('data.txt') is False
    assert validate_nii_ext('data.gz') is False
    assert validate_nii_ext('data.nii.txt') is False

def test_validate_nii_4d(mock_nifti_4d, mock_nifti_3d):
    """Test validation of 4D NIFTI structure"""
    assert validate_nii_4d(mock_nifti_4d) is True
    assert validate_nii_4d(mock_nifti_3d) is False

def test_validate_nii_3d(mock_nifti_4d, mock_nifti_3d):
    """Test validation of 3D NIFTI structure"""
    assert validate_nii_3d(mock_nifti_3d) is True
    assert validate_nii_3d(mock_nifti_4d) is False

def test_validate_nii_same_dim_len(mock_nifti_4d, mock_nifti_3d):
    """Test validation of NIFTI dimension consistency"""
    # Create images with same and different dimensions
    same_dims = nib.Nifti1Image(np.random.rand(10, 10, 10), np.eye(4))
    diff_dims = nib.Nifti1Image(np.random.rand(8, 8, 8), np.eye(4))
    
    assert validate_nii_same_dim_len(same_dims, mock_nifti_3d) is True
    assert validate_nii_same_dim_len(diff_dims, mock_nifti_3d) is False

def test_validate_nii_brain_mask():
    """Test validation of NIFTI brain mask"""
    # Create valid mask with only 0s and 1s
    valid_mask = nib.Nifti1Image(np.random.choice([0.0, 1.0], size=(10, 10, 10)), np.eye(4))
    assert validate_nii_brain_mask(valid_mask) is True
    
    # Create invalid mask with other values
    invalid_mask = nib.Nifti1Image(np.random.rand(10, 10, 10), np.eye(4))
    assert validate_nii_brain_mask(invalid_mask) is False

# Task design validation tests
def test_validate_task_ext():
    """Test validation of task design file extensions"""
    assert validate_task_ext('task.csv') is True
    assert validate_task_ext('task.tsv') is True
    assert validate_task_ext('task.txt') is False
    assert validate_task_ext('task') is False

def test_validate_task_header_required_cols():
    """Test validation of task design header required columns"""
    required_cols = ['onset', 'duration']
    
    # Test valid headers
    assert validate_task_header_required_cols(
        ['onset', 'duration', 'trial_type'], required_cols
    ) is True
    assert validate_task_header_required_cols(
        ['ONSET', 'Duration'], required_cols
    ) is True
    
    # Test invalid headers
    assert validate_task_header_required_cols(
        ['onset'], required_cols
    ) is False
    assert validate_task_header_required_cols(
        ['duration', 'trial_type'], required_cols
    ) is False

def test_validate_task_header_duplicates():
    """Test validation of task design header duplicates"""
    required_cols = ['onset', 'duration']
    
    # Test valid headers
    assert validate_task_header_duplicates(
        ['onset', 'duration', 'trial_type'], required_cols
    ) is True
    
    # Test invalid headers with duplicates
    assert validate_task_header_duplicates(
        ['onset', 'onset', 'duration'], required_cols
    ) is False
    assert validate_task_header_duplicates(
        ['onset', 'duration', 'duration'], required_cols
    ) is False

def test_validate_task_tr():
    """Test validation of TR values"""
    assert validate_task_tr(2.0) is True
    assert validate_task_tr(0.5) is True
    assert validate_task_tr(0.0) is False
    assert validate_task_tr(-1.0) is False

def test_validate_task_slicetime():
    """Test validation of slice timing reference"""
    assert validate_task_slicetime(0.5) is True
    assert validate_task_slicetime(0.0) is True
    assert validate_task_slicetime(1.0) is True
    assert validate_task_slicetime(-0.1) is False
    assert validate_task_slicetime(1.1) is False

# Time series validation tests
def test_validate_ts_task_length():
    """Test validation of time series/task design file length"""
    # Create lists with different lengths
    empty_list = []
    single_row = [['1.0']]
    multiple_rows = [['1.0'], ['2.0'], ['3.0']]
    
    assert validate_ts_task_length(empty_list) is False
    assert validate_ts_task_length(single_row) is True
    assert validate_ts_task_length(multiple_rows) is True

def test_validate_ts_ext():
    """Test validation of time series file extensions"""
    assert validate_ts_ext('data.csv') is True
    assert validate_ts_ext('data.txt') is True
    assert validate_ts_ext('data.tsv') is False
    assert validate_ts_ext('data') is False

def test_validate_ts_single_col():
    """Test validation of time series single column requirement"""
    assert validate_ts_single_col(['1.0']) is True
    assert validate_ts_single_col(['1.0', '2.0']) is False
    assert validate_ts_single_col([]) is True

@pytest.mark.parametrize("value,expected", [
    ('1.0', True),
    ('-1.0', True),
    ('0.0', True),
    ('abc', False),
    ('', False),
    ('1.2.3', False),
    ('1e-10', True),
    ('-1.23e+4', True),
])
def test_validate_ts_numeric(value, expected):
    """Test validation of numeric values in time series"""
    assert validate_ts_numeric(value) is expected

def test_validate_ts_fmri_length():
    """Test validation of equal length between time course and fmri"""
    ts = np.array([0,1,2])
    assert validate_ts_fmri_length(3, ts) is True
    assert validate_ts_fmri_length(4, ts) is False

# CIFTI validation tests
@pytest.fixture
def mock_cifti_image():
    """Create a mock CIFTI image with a BrainModelAxis"""
    # This is a simplified mock - in real tests you'd need a more complex fixture
    mock_cifti = Mock(spec=nib.Cifti2Image)
    mock_cifti.ndim = 2
    
    # Mock BrainModelAxis
    mock_axis = Mock(spec=nib.cifti2.BrainModelAxis)
    
    # Setup header to return the mock axis
    mock_header = Mock()
    mock_header.get_axis.return_value = mock_axis
    mock_cifti.header = mock_header
    
    return mock_cifti

def test_validate_cii_brainmodel_axis(mock_cifti_image):
    """Test validation of CIFTI brain model axis"""
    assert validate_cii_brainmodel_axis(mock_cifti_image) is True
    
    # Test with non-BrainModelAxis
    mock_cifti_image.header.get_axis.return_value = Mock()  # Not a BrainModelAxis
    assert validate_cii_brainmodel_axis(mock_cifti_image) is False

def test_validate_cii_dtseries_ext():
    """Test validation of CIFTI dtseries file extension"""
    assert validate_cii_dtseries_ext('data.dtseries.nii') is True
    assert validate_cii_dtseries_ext('data.nii') is False
    assert validate_cii_dtseries_ext('data.dscalar.nii') is False
    assert validate_cii_dtseries_ext('data.txt') is False

def test_validate_cii_file_inputs():
    """Test validation of CIFTI file input combinations"""
    # Test valid combinations
    msg, valid = validate_cii_file_inputs(
        dtseries='data.dtseries.nii',
        left_mesh='left.surf.gii',
        right_mesh=None
    )
    assert valid is True
    
    msg, valid = validate_cii_file_inputs(
        dtseries='data.dtseries.nii',
        left_mesh=None,
        right_mesh='right.surf.gii'
    )
    assert valid is True
    
    # Test invalid combinations
    msg, valid = validate_cii_file_inputs(
        dtseries=None,
        left_mesh='left.surf.gii',
        right_mesh=None
    )
    assert valid is False
    assert "dtseries.nii file must be provided" in msg
    
    msg, valid = validate_cii_file_inputs(
        dtseries='data.dtseries.nii',
        left_mesh=None,
        right_mesh=None
    )
    assert valid is False
    assert "hemisphere mesh file must be provided" in msg

def test_validate_cii_hemisphere():
    """Test validation of CIFTI hemisphere"""
    # Create a mock BrainModelAxis that will return the expected structure
    mock_axis = Mock(spec=nib.cifti2.BrainModelAxis)
    
    # Setup the iter_structures method to return appropriate values
    mock_axis.iter_structures.return_value = [
        ('CIFTI_STRUCTURE_CORTEX_LEFT', None),
        ('CIFTI_STRUCTURE_CORTEX_RIGHT', None)
    ]
    
    # Test left hemisphere
    assert validate_cii_hemisphere(
        mock_axis, 'left', 'CIFTI_STRUCTURE_CORTEX_LEFT'
    ) is True
    
    # Test right hemisphere
    assert validate_cii_hemisphere(
        mock_axis, 'right', 'CIFTI_STRUCTURE_CORTEX_RIGHT'
    ) is True
    
    # Test missing hemisphere
    assert validate_cii_hemisphere(
        mock_axis, 'left', 'CIFTI_STRUCTURE_CEREBELLUM'
    ) is False

# Additional GIFTI validation tests
def test_validate_gii_func_mesh_len(mock_gifti_func, mock_gifti_mesh):
    """Test validation of GIFTI functional and mesh length compatibility"""
    # Create mock GIFTI images with matching vertex counts
    vertices = np.random.rand(100, 3).astype(np.float32)  # Explicitly cast to float32
    faces = np.random.randint(0, 100, (50, 3)).astype(np.int32)  # Explicitly cast to int32
    
    # Create mesh with 100 vertices
    mesh_arrays = [
        nib.gifti.GiftiDataArray(vertices),
        nib.gifti.GiftiDataArray(faces)
    ]
    mesh_gii = nib.gifti.GiftiImage(darrays=mesh_arrays)
    
    # Create func with data for 100 vertices
    func_data = np.random.rand(100).astype(np.float32)  # Explicitly cast to float32
    func_arrays = [nib.gifti.GiftiDataArray(func_data)]
    func_gii = nib.gifti.GiftiImage(darrays=func_arrays)
    
    # Test matching lengths
    assert validate_gii_func_mesh_len(func_gii, mesh_gii) is True
    
    # Create func with mismatched length
    func_data_mismatched = np.random.rand(80).astype(np.float32)  # Explicitly cast to float32
    func_arrays_mismatched = [nib.gifti.GiftiDataArray(func_data_mismatched)]
    func_gii_mismatched = nib.gifti.GiftiImage(darrays=func_arrays_mismatched)
    
    # Test mismatched lengths
    assert validate_gii_func_mesh_len(func_gii_mismatched, mesh_gii) is False