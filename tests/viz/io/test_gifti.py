import pytest
from unittest.mock import Mock, patch
from findviz.viz.io.gifti import GiftiUpload, read_gii
from findviz.viz import exception

def test_gifti_upload_init():
    """Test GiftiUpload initialization"""
    uploader = GiftiUpload(method='browser')
    assert uploader.method == 'browser'

@patch('findviz.viz.io.gifti.read_gii')
def test_gifti_upload_valid_left_only(mock_read_gii, mock_gifti_func, mock_gifti_mesh):
    """Test successful gifti file upload with left hemisphere only"""
    mock_read_gii.side_effect = [mock_gifti_func, mock_gifti_mesh]
    
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

def test_gifti_upload_invalid_combination():
    """Test gifti upload with invalid file combination"""
    uploader = GiftiUpload(method='browser')
    mock_files = {
        'left_gii_func': Mock(filename='left.func.gii'),
        'left_gii_mesh': None,  # Missing required mesh file
        'right_gii_func': None,
        'right_gii_mesh': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        with pytest.raises(exception.FileValidationError):
            uploader.upload()

def test_read_gii_browser():
    """Test reading gifti file from browser upload"""
    mock_file = Mock()
    mock_file.read.return_value = b'mock_gifti_data'
    
    with patch('nibabel.GiftiImage.from_bytes') as mock_from_bytes:
        read_gii(mock_file, method='browser')
        mock_from_bytes.assert_called_once_with(b'mock_gifti_data')

def test_read_gii_browser_error():
    """Test error handling when reading gifti file from browser"""
    mock_file = Mock()
    mock_file.read.side_effect = Exception('Read error')
    
    with pytest.raises(Exception):
        read_gii(mock_file, method='browser')