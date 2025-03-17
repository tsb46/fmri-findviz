import nibabel as nib
import numpy as np
import pytest
import signal
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from findviz.viz.io.cache import Cache, cleanup_handler

@pytest.fixture
def mock_temp_dir(tmp_path):
    """Create a temporary directory for testing"""
    test_dir = tmp_path / 'findviz'
    test_dir.mkdir()
    return test_dir

@pytest.fixture
def cache(mock_temp_dir):
    """Create a Cache instance with mocked temp directory"""
    with patch('tempfile.gettempdir', return_value=str(mock_temp_dir.parent)):
        return Cache()

def test_cache_init(cache, mock_temp_dir):
    """Test Cache initialization"""
    assert cache.temp_dir == mock_temp_dir
    assert cache.cache_file == mock_temp_dir / 'cache.json'
    assert mock_temp_dir.exists()

def test_save_cache(cache):
    """Test saving data to cache"""
    test_data = {'key': 'value'}
    
    mock_file = mock_open()
    with patch('builtins.open', mock_file):
        cache.save(test_data)
        mock_file.assert_called_once_with(cache.cache_file, 'w')
        # Check if the full JSON string was written
        written_data = ''.join(call.args[0] 
                             for call in mock_file().write.call_args_list)
        assert written_data == json.dumps(test_data)

def test_save_cache_error(cache):
    """Test error handling when saving cache"""
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = Exception('Mock error')
        with pytest.raises(IOError) as exc_info:
            cache.save({'key': 'value'})
        assert 'Failed to save cache' in str(exc_info.value)


def test_serialize_nifti_data(cache):
    """Test serialization of NIfTI data"""
    # Create mock NIfTI image
    affine = np.eye(4)
    data = np.random.rand(10, 10, 10, 100)
    nifti_img = nib.Nifti1Image(data, affine)
    
    test_data = {'nifti': nifti_img}
    serialized = cache._serialize_data(test_data)

    assert serialized['nifti']['_type'] == 'Nifti1Image'
    assert list(serialized['nifti']['shape']) == list(data.shape)
    assert isinstance(serialized['nifti']['affine'], list)
    assert 'header' in serialized['nifti']

def test_serialize_gifti_data(cache):
    """Test serialization of GIFTI data"""
    # Create mock GIFTI image
    arrays = [
        nib.gifti.GiftiDataArray(np.random.rand(10, 1).astype(np.float32)) 
        for _ in range(5)
    ]
    gifti_img = nib.gifti.GiftiImage(darrays=arrays)
    
    test_data = {'gifti': gifti_img}
    serialized = cache._serialize_data(test_data)
    
    assert serialized['gifti']['_type'] == 'GiftiImage'
    assert len(serialized['gifti']['darrays']) == 5

def test_load_cache(cache):
    """Test loading data from cache"""
    test_data = {'key': 'value'}
    
    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))) as mock_file:
        with patch.object(Path, 'exists', return_value=True):
            loaded_data = cache.load()
            assert loaded_data == test_data
            mock_file.assert_called_once_with(cache.cache_file, 'r')

def test_load_cache_nonexistent(cache):
    """Test loading when cache doesn't exist"""
    with patch.object(Path, 'exists', return_value=False):
        assert cache.load() is None

def test_load_cache_error(cache):
    """Test error handling when loading cache"""
    with patch('builtins.open', mock_open()) as mock_file:
        with patch.object(Path, 'exists', return_value=True):
            mock_file.side_effect = Exception('Mock error')
            with pytest.raises(IOError) as exc_info:
                cache.load()
            assert 'Failed to load cache' in str(exc_info.value)

def test_clear_cache(cache):
    """Test clearing cache"""
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'unlink') as mock_unlink:
        cache.clear()
        mock_unlink.assert_called_once()

def test_clear_cache_error(cache):
    """Test error handling when clearing cache"""
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'unlink', side_effect=Exception('Mock error')):
        with pytest.raises(IOError) as exc_info:
            cache.clear()
        assert 'Failed to clear cache' in str(exc_info.value)

def test_exists(cache):
    """Test checking if cache exists"""
    with patch.object(Path, 'exists', return_value=True):
        assert cache.exists() is True
    with patch.object(Path, 'exists', return_value=False):
        assert cache.exists() is False

def test_get_cache_path(cache, mock_temp_dir):
    """Test getting cache file path"""
    assert cache.get_cache_path() == mock_temp_dir / 'cache.json'

def test_cleanup(cache):
    """Test cleanup functionality"""
    with patch.object(Cache, 'clear') as mock_clear, \
         patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'iterdir', return_value=[]), \
         patch.object(Path, 'rmdir') as mock_rmdir:
        cache.cleanup()
        mock_clear.assert_called_once()
        mock_rmdir.assert_called_once()

def test_cleanup_handler():
    """Test cleanup handler function"""
    mock_cache = Cache()
    with patch.object(Cache, 'cleanup') as mock_cleanup, \
         patch('findviz.viz.io.cache.exit') as mock_exit:
        handler = cleanup_handler(mock_cache)
        handler(signal.SIGINT, None)
        mock_cleanup.assert_called_once()
        mock_exit.assert_called_once_with(0)