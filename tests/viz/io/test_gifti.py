import pytest
import numpy as np
import nibabel as nib
from nibabel.gifti import GiftiImage, GiftiDataArray
from unittest.mock import Mock, patch, MagicMock

from findviz.viz.io.gifti import (
    GiftiUpload, 
    read_gii,
    GiftiFiles
)
from findviz.viz.exception import (
    FileInputError,
    FileUploadError,
    FileValidationError
)


@pytest.fixture
def mock_gifti_func():
    """Create a mock functional GIFTI image for testing"""
    # Create a GIFTI with 5 data arrays (timepoints)
    data_arrays = []
    for i in range(5):
        data = np.random.rand(100).astype(np.float32)  # 100 vertices
        darray = GiftiDataArray(data)
        data_arrays.append(darray)
    return GiftiImage(darrays=data_arrays)


@pytest.fixture
def mock_gifti_mesh():
    """Create a mock mesh GIFTI image for testing"""
    # Create a GIFTI with 2 data arrays (coordinates and triangles)
    coords = np.random.rand(100, 3).astype(np.float32)  # 100 vertices
    triangles = np.random.randint(0, 100, (50, 3)).astype(np.int32)  # 50 triangles
    
    coord_array = GiftiDataArray(coords)
    triangle_array = GiftiDataArray(triangles)
    
    return GiftiImage(darrays=[coord_array, triangle_array])


def test_gifti_upload_init():
    """Test GiftiUpload initialization"""
    uploader = GiftiUpload(method='browser')
    assert uploader.method == 'browser'
    
    uploader = GiftiUpload(method='cli')
    assert uploader.method == 'cli'
    
    # Test invalid method
    with pytest.raises(ValueError):
        GiftiUpload(method='invalid')


@patch('findviz.viz.io.gifti.read_gii')
@patch('findviz.viz.io.validate.validate_gii_func')
@patch('findviz.viz.io.validate.validate_gii_mesh')
@patch('findviz.viz.io.validate.validate_gii_func_mesh_len')
def test_gifti_upload_valid_left_only(
    mock_validate_len, mock_validate_mesh, mock_validate_func, 
    mock_read_gii, mock_gifti_func, mock_gifti_mesh
):
    """Test successful gifti file upload with left hemisphere only"""
    mock_read_gii.side_effect = [mock_gifti_func, mock_gifti_mesh]
    mock_validate_func.return_value = True
    mock_validate_mesh.return_value = True
    mock_validate_len.return_value = True
    
    # Add __name__ attributes to the mocks
    mock_validate_func.__name__ = 'validate_gii_func'
    mock_validate_mesh.__name__ = 'validate_gii_mesh'
    mock_validate_len.__name__ = 'validate_gii_func_mesh_len'
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': Mock(filename='left.surf.gii'),
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload()
        assert result['left_gii_func'] is not None
        assert result['left_gii_mesh'] is not None
        assert result['right_gii_func'] is None
        assert result['right_gii_mesh'] is None


@patch('findviz.viz.io.gifti.read_gii')
@patch('findviz.viz.io.validate.validate_gii_func')
@patch('findviz.viz.io.validate.validate_gii_mesh')
@patch('findviz.viz.io.validate.validate_gii_func_mesh_len')
@patch('findviz.viz.io.validate.validate_gii_func_len')
def test_gifti_upload_valid_both_hemispheres(
    mock_validate_func_len, mock_validate_len, mock_validate_mesh, 
    mock_validate_func, mock_read_gii, mock_gifti_func, mock_gifti_mesh
):
    """Test successful gifti file upload with both hemispheres"""
    # Configure mocks for successful validation
    mock_read_gii.side_effect = [
        mock_gifti_func, mock_gifti_mesh,  # Left hemisphere
        mock_gifti_func, mock_gifti_mesh   # Right hemisphere
    ]
    mock_validate_func.return_value = True
    mock_validate_mesh.return_value = True
    mock_validate_len.return_value = True
    mock_validate_func_len.return_value = True
    
    # Add __name__ attributes to the mocks
    mock_validate_func.__name__ = 'validate_gii_func'
    mock_validate_mesh.__name__ = 'validate_gii_mesh'
    mock_validate_len.__name__ = 'validate_gii_func_mesh_len'
    mock_validate_func_len.__name__ = 'validate_gii_func_len'
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': Mock(filename='left.surf.gii'),
        'right_gii_func': Mock(filename='right.func.gii'),
        'right_gii_mesh': Mock(filename='right.surf.gii')
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload()
        assert result['left_gii_func'] is not None
        assert result['left_gii_mesh'] is not None
        assert result['right_gii_func'] is not None
        assert result['right_gii_mesh'] is not None


@patch('findviz.viz.io.validate.validate_gii_file_inputs')
def test_gifti_upload_invalid_combination(mock_validate_inputs):
    """Test gifti upload with invalid file combination"""
    # Configure mock to indicate validation failure
    mock_validate_inputs.return_value = (
        "Missing required mesh file for left hemisphere", 
        ["left_mesh"], 
        False
    )
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': None,  # Missing required mesh file
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.gifti.read_gii')
@patch('findviz.viz.io.validate.validate_gii_func')
def test_gifti_upload_invalid_func(mock_validate_func, mock_read_gii, mock_gifti_func):
    """Test error when functional file is invalid"""
    mock_read_gii.return_value = mock_gifti_func
    mock_validate_func.return_value = False
    
    # Add __name__ attribute to the mock
    mock_validate_func.__name__ = 'validate_gii_func'
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': Mock(filename='left.surf.gii'),
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.gifti.read_gii')
@patch('findviz.viz.io.validate.validate_gii_func')
@patch('findviz.viz.io.validate.validate_gii_mesh')
def test_gifti_upload_invalid_mesh(
    mock_validate_mesh, mock_validate_func, mock_read_gii, 
    mock_gifti_func, mock_gifti_mesh
):
    """Test error when mesh file is invalid"""
    mock_read_gii.side_effect = [mock_gifti_func, mock_gifti_mesh]
    mock_validate_func.return_value = True
    mock_validate_mesh.return_value = False
    
    # Add __name__ attributes to the mocks
    mock_validate_func.__name__ = 'validate_gii_func'
    mock_validate_mesh.__name__ = 'validate_gii_mesh'
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': Mock(filename='left.surf.gii'),
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.gifti.read_gii')
@patch('findviz.viz.io.validate.validate_gii_func')
@patch('findviz.viz.io.validate.validate_gii_mesh')
@patch('findviz.viz.io.validate.validate_gii_func_mesh_len')
def test_gifti_upload_length_mismatch(
    mock_validate_len, mock_validate_mesh, mock_validate_func, 
    mock_read_gii, mock_gifti_func, mock_gifti_mesh
):
    """Test error when func and mesh lengths don't match"""
    mock_read_gii.side_effect = [mock_gifti_func, mock_gifti_mesh]
    mock_validate_func.return_value = True
    mock_validate_mesh.return_value = True
    mock_validate_len.return_value = False
    
    # Add __name__ attributes to the mocks
    mock_validate_func.__name__ = 'validate_gii_func'
    mock_validate_mesh.__name__ = 'validate_gii_mesh'
    mock_validate_len.__name__ = 'validate_gii_func_mesh_len'
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': Mock(filename='left.surf.gii'),
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.gifti.read_gii')
@patch('findviz.viz.io.validate.validate_gii_func')
@patch('findviz.viz.io.validate.validate_gii_mesh')
@patch('findviz.viz.io.validate.validate_gii_func_mesh_len')
@patch('findviz.viz.io.validate.validate_gii_func_len')
def test_gifti_upload_hemisphere_length_mismatch(
    mock_validate_func_len, mock_validate_len, mock_validate_mesh, 
    mock_validate_func, mock_read_gii, mock_gifti_func, mock_gifti_mesh
):
    """Test error when left and right hemisphere lengths don't match"""
    mock_read_gii.side_effect = [
        mock_gifti_func, mock_gifti_mesh,  # Left hemisphere
        mock_gifti_func, mock_gifti_mesh   # Right hemisphere
    ]
    mock_validate_func.return_value = True
    mock_validate_mesh.return_value = True
    mock_validate_len.return_value = True
    mock_validate_func_len.return_value = False
    
    # Add __name__ attributes to the mocks
    mock_validate_func.__name__ = 'validate_gii_func'
    mock_validate_mesh.__name__ = 'validate_gii_mesh'
    mock_validate_len.__name__ = 'validate_gii_func_mesh_len'
    mock_validate_func_len.__name__ = 'validate_gii_func_len'
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': Mock(filename='left.surf.gii'),
        'right_gii_func': Mock(filename='right.func.gii'),
        'right_gii_mesh': Mock(filename='right.surf.gii')
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.validate.validate_gii_func_ext')
def test_gifti_upload_invalid_func_extension(mock_validate_func_ext):
    """Test error when functional file has invalid extension"""
    # Configure mock to indicate invalid extension
    mock_validate_func_ext.return_value = False
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.invalid.gii'),  # Invalid extension
        'left_gii_mesh': Mock(filename='left.surf.gii'),
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileInputError):
            uploader.upload()


@patch('findviz.viz.io.validate.validate_gii_mesh_ext')
@patch('findviz.viz.io.validate.validate_gii_func_ext')
def test_gifti_upload_invalid_mesh_extension(mock_validate_mesh_ext, mock_validate_func_ext):
    """Test error when mesh file has invalid extension"""
    # Configure mock to indicate invalid extension
    mock_validate_mesh_ext.return_value = False
    mock_validate_func_ext.return_value = True
    
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': Mock(filename='left.invalid.gii'),  # Invalid extension
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileInputError):
            uploader.upload()


def test_read_gii_browser():
    """Test reading gifti file from browser upload"""
    mock_file = Mock()
    mock_file.read.return_value = b'mock_gifti_data'
    
    with patch('nibabel.GiftiImage.from_bytes') as mock_from_bytes:
        read_gii(mock_file, method='browser')
        mock_from_bytes.assert_called_once_with(b'mock_gifti_data')


def test_read_gii_cli(tmp_path):
    """Test reading gifti file from CLI"""
    # Create a simple GIFTI file
    data = np.zeros((10, 3), dtype=np.float32)
    darray = GiftiDataArray(data)
    img = GiftiImage(darrays=[darray])
    
    # Save to temporary file
    filepath = tmp_path / "test.gii"
    img.to_filename(str(filepath))
    
    # Test reading the file
    result = read_gii(filepath, method='cli')
    assert isinstance(result, GiftiImage)
    assert len(result.darrays) == 1


def test_read_gii_browser_error():
    """Test error handling when reading gifti file from browser"""
    mock_file = Mock()
    mock_file.read.side_effect = Exception('Read error')
    
    with pytest.raises(Exception):
        read_gii(mock_file, method='browser')


def test_read_gii_cli_error():
    """Test error handling when reading gifti file from CLI"""
    with pytest.raises(Exception):
        read_gii("nonexistent_file.gii", method='cli')


def test_get_browser_input():
    """Test _get_browser_input method"""
    mock_request = MagicMock()
    mock_request.files.get.side_effect = lambda key: Mock(filename=f"{key}.gii") if key == 'left_gii_func' else None
    
    with patch('findviz.viz.io.gifti.request', mock_request):
        uploader = GiftiUpload(method='browser')
        result = uploader._get_browser_input()
        
        assert result['left_gii_func'] is not None
        assert result['left_gii_func'].filename == 'left_gii_func.gii'
        assert result['left_gii_mesh'] is None
        assert result['right_gii_func'] is None
        assert result['right_gii_mesh'] is None


def test_gifti_files_enum():
    """Test GiftiFiles enum values"""
    assert GiftiFiles.LEFT_FUNC.value == 'left_gii_func'
    assert GiftiFiles.RIGHT_FUNC.value == 'right_gii_func'
    assert GiftiFiles.LEFT_MESH.value == 'left_gii_mesh'
    assert GiftiFiles.RIGHT_MESH.value == 'right_gii_mesh'