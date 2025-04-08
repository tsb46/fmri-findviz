"""Tests for NIFTI file handling utilities"""
import pytest
import nibabel as nib
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import gzip

from findviz.viz.io.nifti import (
    NiftiUpload, 
    read_nii, 
    NiftiFiles
)
from findviz.viz.exception import (
    FileInputError,
    FileUploadError,
    FileValidationError
)


@pytest.fixture
def mock_nifti_3d():
    """Create a mock 3D NIFTI image for testing"""
    data = np.random.rand(10, 10, 10)
    return nib.Nifti1Image(data, np.eye(4))


@pytest.fixture
def mock_nifti_4d():
    """Create a mock 4D NIFTI image for testing"""
    data = np.random.rand(10, 10, 10, 5)
    return nib.Nifti1Image(data, np.eye(4))


@pytest.fixture
def mock_nifti_mask():
    """Create a mock NIFTI mask for testing"""
    data = np.zeros((10, 10, 10))
    data[2:8, 2:8, 2:8] = 1
    return nib.Nifti1Image(data, np.eye(4))


@pytest.fixture
def mock_nifti_invalid_mask():
    """Create an invalid NIFTI mask (not just 0s and 1s)"""
    data = np.zeros((10, 10, 10))
    data[2:8, 2:8, 2:8] = 2  # Invalid value
    return nib.Nifti1Image(data, np.eye(4))


def test_nifti_upload_init():
    """Test NiftiUpload initialization"""
    uploader = NiftiUpload(method='browser')
    assert uploader.method == 'browser'
    
    uploader = NiftiUpload(method='cli')
    assert uploader.method == 'cli'


@patch('findviz.viz.io.nifti.read_nii')
def test_nifti_upload_browser_func_only(mock_read_nii, mock_nifti_4d):
    """Test successful browser upload with only functional file"""
    mock_read_nii.return_value = mock_nifti_4d
    
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': Mock(filename='test.nii.gz'),
        'nii_anat': None,
        'nii_mask': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload()
        assert result['nii_func'] is not None
        assert result['nii_anat'] is None
        assert result['nii_mask'] is None
        
        # Verify read_nii was called with correct parameters
        mock_read_nii.assert_called_once_with(mock_files['nii_func'], 'browser')


@patch('findviz.viz.io.nifti.read_nii')
def test_nifti_upload_cli_all_files(mock_read_nii, mock_nifti_4d, mock_nifti_3d, mock_nifti_mask):
    """Test successful CLI upload with all files"""
    # Configure mock to return different values for different calls
    mock_read_nii.side_effect = [mock_nifti_4d, mock_nifti_3d, mock_nifti_mask]
    
    uploader = NiftiUpload(method='cli')
    cli_files = {
        'nii_func': '/path/to/func.nii.gz',
        'nii_anat': '/path/to/anat.nii.gz',
        'nii_mask': '/path/to/mask.nii.gz'
    }
    
    result = uploader.upload(fmri_files=cli_files)
    
    assert result['nii_func'] is not None
    assert result['nii_anat'] is not None
    assert result['nii_mask'] is not None
    
    # Verify read_nii was called for each file
    assert mock_read_nii.call_count == 3


def test_nifti_upload_missing_func():
    """Test error when functional file is missing"""
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': None,
        'nii_anat': Mock(filename='anat.nii.gz'),
        'nii_mask': Mock(filename='mask.nii.gz')
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileInputError):
            uploader.upload()


def test_nifti_upload_invalid_func_extension():
    """Test error when functional file has invalid extension"""
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': Mock(filename='func.txt'),  # Invalid extension
        'nii_anat': None,
        'nii_mask': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileInputError):
            uploader.upload()


@patch('findviz.viz.io.nifti.read_nii')
@patch('findviz.viz.io.validate.validate_nii_4d')
def test_nifti_upload_invalid_func_dimensions(mock_validate_4d, mock_read_nii, mock_nifti_3d):
    """Test error when functional file doesn't have 4 dimensions"""
    mock_read_nii.return_value = mock_nifti_3d
    mock_validate_4d.return_value = False
    # Add __name__ attribute to the mock
    mock_validate_4d.__name__ = 'validate_nii_4d'
    
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': Mock(filename='func.nii.gz'),
        'nii_anat': None,
        'nii_mask': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.nifti.read_nii')
def test_nifti_upload_func_read_error(mock_read_nii):
    """Test error when reading functional file fails"""
    mock_read_nii.side_effect = Exception("Read error")
    
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': Mock(filename='func.nii.gz'),
        'nii_anat': None,
        'nii_mask': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileUploadError):
            uploader.upload()


@patch('findviz.viz.io.nifti.read_nii')
@patch('findviz.viz.io.validate.validate_nii_3d')
def test_nifti_upload_invalid_anat_dimensions(mock_validate_3d, mock_read_nii, mock_nifti_4d):
    """Test error when anatomical file doesn't have 3 dimensions"""
    # First call for func, second for anat
    mock_read_nii.side_effect = [mock_nifti_4d, mock_nifti_4d]
    # First call for anat validation
    mock_validate_3d.return_value = False
    # Add __name__ attribute to the mock
    mock_validate_3d.__name__ = 'validate_nii_3d'
    
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': Mock(filename='func.nii.gz'),
        'nii_anat': Mock(filename='anat.nii.gz'),
        'nii_mask': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.nifti.read_nii')
@patch('findviz.viz.io.validate.validate_nii_3d')
@patch('findviz.viz.io.validate.validate_nii_4d')
@patch('findviz.viz.io.validate.validate_nii_same_dim_len')
def test_nifti_upload_anat_dimension_mismatch(
    mock_validate_same_dim, mock_validate_4d, mock_validate_3d, mock_read_nii, 
    mock_nifti_4d, mock_nifti_3d
):
    """Test error when anatomical dimensions don't match functional"""
    # First call for func, second for anat
    mock_read_nii.side_effect = [mock_nifti_4d, mock_nifti_3d]
    mock_validate_4d.return_value = True
    mock_validate_3d.return_value = True
    mock_validate_same_dim.return_value = False
    
    # Add __name__ attributes to the mocks
    mock_validate_4d.__name__ = 'validate_nii_4d'
    mock_validate_3d.__name__ = 'validate_nii_3d'
    mock_validate_same_dim.__name__ = 'validate_nii_same_dim_len'
    
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': Mock(filename='func.nii.gz'),
        'nii_anat': Mock(filename='anat.nii.gz'),
        'nii_mask': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


@patch('findviz.viz.io.nifti.read_nii')
@patch('findviz.viz.io.validate.validate_nii_3d')
@patch('findviz.viz.io.validate.validate_nii_4d')
@patch('findviz.viz.io.validate.validate_nii_same_dim_len')
@patch('findviz.viz.io.validate.validate_nii_brain_mask')
def test_nifti_upload_invalid_mask(
    mock_validate_mask, mock_validate_same_dim, mock_validate_4d, 
    mock_validate_3d, mock_read_nii, mock_nifti_4d, mock_nifti_3d, mock_nifti_invalid_mask
):
    """Test error when mask is not valid (not just 0s and 1s)"""
    # Configure mocks for successful validation until mask check
    mock_read_nii.side_effect = [mock_nifti_4d, mock_nifti_3d, mock_nifti_invalid_mask]
    mock_validate_4d.return_value = True
    mock_validate_3d.return_value = True
    mock_validate_same_dim.return_value = True
    mock_validate_mask.return_value = False
    
    # Add __name__ attributes to the mocks
    mock_validate_4d.__name__ = 'validate_nii_4d'
    mock_validate_3d.__name__ = 'validate_nii_3d'
    mock_validate_same_dim.__name__ = 'validate_nii_same_dim_len'
    mock_validate_mask.__name__ = 'validate_nii_brain_mask'
    
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'nii_func': Mock(filename='func.nii.gz'),
        'nii_anat': Mock(filename='anat.nii.gz'),
        'nii_mask': Mock(filename='mask.nii.gz')
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(FileValidationError):
            uploader.upload()


def test_get_browser_input():
    """Test _get_browser_input method"""
    mock_request = MagicMock()
    mock_request.files.get.side_effect = lambda key: Mock(filename=f"{key}.nii.gz") if key == 'nii_func' else None
    
    with patch('findviz.viz.io.nifti.request', mock_request):
        uploader = NiftiUpload(method='browser')
        result = uploader._get_browser_input()
        
        assert result['nii_func'] is not None
        assert result['nii_func'].filename == 'nii_func.nii.gz'
        assert result['nii_anat'] is None
        assert result['nii_mask'] is None


def test_read_nii_cli(tmp_path):
    """Test read_nii with CLI method"""
    # Create a temporary NIFTI file
    data = np.zeros((5, 5, 5))
    img = nib.Nifti1Image(data, np.eye(4))
    filepath = tmp_path / "test.nii"
    nib.save(img, filepath)
    
    # Test reading the file
    result = read_nii(filepath, method='cli')
    assert isinstance(result, nib.Nifti1Image)
    assert result.shape == (5, 5, 5)


def test_read_nii_cli_error():
    """Test read_nii with CLI method and nonexistent file"""
    with pytest.raises(Exception):
        read_nii("nonexistent_file.nii", method='cli')


def test_read_nii_browser_nii():
    """Test read_nii with browser method and .nii file"""
    # Create mock file with .nii extension
    mock_file = Mock()
    mock_file.filename = "test.nii"
    mock_file.read.return_value = b'dummy_data'
    
    with patch('findviz.viz.io.utils.parse_nifti_file_ext', return_value='.nii'):
        with patch('nibabel.Nifti1Image.from_bytes', return_value=Mock(spec=nib.Nifti1Image)):
            result = read_nii(mock_file, method='browser')
            assert isinstance(result, Mock)


def test_read_nii_browser_nii_gz():
    """Test read_nii with browser method and .nii.gz file"""
    # Create mock file with .nii.gz extension
    mock_file = Mock()
    mock_file.filename = "test.nii.gz"
    
    # Create a simple NIFTI file in memory
    data = np.zeros((5, 5, 5))
    img = nib.Nifti1Image(data, np.eye(4))
    
    # Compress it
    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
        f.write(img.to_bytes())
    
    mock_file.read.return_value = buffer.getvalue()
    
    with patch('findviz.viz.io.utils.parse_nifti_file_ext', return_value='.nii.gz'):
        with patch('nibabel.Nifti1Image.from_bytes', return_value=Mock(spec=nib.Nifti1Image)):
            result = read_nii(mock_file, method='browser')
            assert isinstance(result, Mock)


def test_read_nii_browser_invalid():
    """Test read_nii with invalid browser file"""
    mock_file = Mock()
    mock_file.filename = "test.nii"
    mock_file.read.side_effect = Exception('Read error')
    
    with patch('findviz.viz.io.utils.parse_nifti_file_ext', return_value='.nii'):
        with pytest.raises(Exception):
            read_nii(mock_file, method='browser')


def test_nifti_files_enum():
    """Test NiftiFiles enum values"""
    assert NiftiFiles.FUNC.value == 'nii_func'
    assert NiftiFiles.ANAT.value == 'nii_anat'
    assert NiftiFiles.MASK.value == 'nii_mask'