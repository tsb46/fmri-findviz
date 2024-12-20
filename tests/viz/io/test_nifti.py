import pytest
from unittest.mock import Mock, patch
from findviz.viz.io.nifti import NiftiUpload, read_nii

def test_nifti_upload_init():
    """Test NiftiUpload initialization"""
    uploader = NiftiUpload(method='browser')
    assert uploader.method == 'browser'

@patch('findviz.viz.io.nifti.read_nii')
def test_nifti_upload_valid(mock_read_nii, mock_nifti_4d):
    """Test successful nifti file upload"""
    mock_read_nii.return_value = mock_nifti_4d
    
    uploader = NiftiUpload(method='browser')
    mock_files = {
        'func_file': Mock(filename='test.nii.gz'),
        'anat_file': None,
        'mask_file': None
    }
    
    with patch.object(uploader, '_get_browser_input', return_value=mock_files):
        result = uploader.upload()
        assert result['func_file'] is not None
        assert result['anat_file'] is None
        assert result['mask_file'] is None

def test_read_nii_browser_invalid():
    """Test read_nii with invalid browser file"""
    mock_file = Mock()
    mock_file.read.side_effect = Exception('Read error')
    
    with pytest.raises(Exception):
        read_nii(mock_file, method='browser')