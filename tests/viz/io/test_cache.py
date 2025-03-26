import nibabel as nib
import numpy as np
import pytest
import signal
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, call
from findviz.viz.io.cache import Cache, cleanup_handler
import logging

@pytest.fixture
def mock_temp_dir(tmp_path):
    """Create a temporary directory for testing"""
    test_dir = tmp_path / 'findviz'
    test_dir.mkdir()
    return test_dir

@pytest.fixture(autouse=True)
def disable_logging():
    """Disable all logging during tests"""
    # Disable all loggers
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(logging.NullHandler())
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # Specifically disable the cache logger
    cache_logger = logging.getLogger('findviz.viz.io.cache')
    cache_logger.handlers = []
    cache_logger.addHandler(logging.NullHandler())
    cache_logger.setLevel(logging.CRITICAL)
    
    # Also patch the logger setup to prevent new loggers from being created
    with patch('findviz.logger_config.setup_logger') as mock_setup:
        mock_logger = MagicMock()
        mock_setup.return_value = mock_logger
        yield mock_logger

    # Clean up
    logging.getLogger().handlers = []
    cache_logger.handlers = []

@pytest.fixture(autouse=True)
def cleanup_singleton():
    """Clean up singleton instance after each test"""
    yield
    Cache._instance = None

@pytest.fixture
def cache(mock_temp_dir):
    """Create a Cache instance with mocked temp directory"""
    with patch('tempfile.gettempdir', return_value=str(mock_temp_dir)):
        cache = Cache()
        # Mock the signal handlers to avoid issues in testing environment
        with patch('signal.signal'):
            cache._initialize()
        return cache

def test_cache_init(cache, mock_temp_dir):
    """Test Cache initialization"""
    assert cache.temp_dir == mock_temp_dir / 'findviz_cache'
    assert cache.cache_file == mock_temp_dir / 'findviz_cache' / 'viewer_cache.json'
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

def test_clear_cache(cache, caplog):
    """Test clearing cache"""
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'unlink') as mock_unlink:
        cache.clear()
        mock_unlink.assert_called_once()

def test_clear_cache_error(cache, caplog):
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
    assert cache.get_cache_path() == mock_temp_dir / 'findviz_cache' / 'viewer_cache.json'

def test_cleanup(cache, caplog):
    """Test cleanup functionality"""
    with patch.object(Cache, 'clear') as mock_clear, \
         patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'iterdir', return_value=[]), \
         patch.object(Path, 'rmdir') as mock_rmdir:
        cache.cleanup()
        mock_clear.assert_called_once()
        mock_rmdir.assert_called_once()

def test_cleanup_handler(caplog):
    """Test cleanup handler function"""
    with patch('findviz.viz.io.cache.Cache') as MockCache:
        mock_cache = MockCache()
        with patch('findviz.viz.io.cache.exit') as mock_exit:
            handler = cleanup_handler(mock_cache)
            handler(signal.SIGINT, None)
            mock_cache.clear.assert_called_once()
            mock_exit.assert_called_once_with(0)

def test_singleton_pattern():
    """Test that Cache follows singleton pattern"""
    with patch('signal.signal'):  # Mock signal handlers
        cache1 = Cache()
        cache2 = Cache()
        assert cache1 is cache2
        assert Cache._instance is cache1

def test_ensure_temp_dir(cache):
    """Test _ensure_temp_dir method"""
    with patch.object(Path, 'mkdir') as mock_mkdir:
        cache._ensure_temp_dir()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

def test_cleanup_with_non_empty_dir(cache, caplog):
    """Test cleanup when directory is not empty"""
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'iterdir', return_value=[MagicMock()]), \
         patch.object(Path, 'rmdir') as mock_rmdir, \
         patch.object(Cache, 'clear') as mock_clear:
        cache.cleanup()
        mock_clear.assert_called_once()
        mock_rmdir.assert_not_called()

def test_signal_handler_registration():
    """Test signal handler registration"""
    with patch('signal.signal') as mock_signal:
        cache = Cache()
        cache._initialize()
        
        # Get all the signal types that were registered
        signal_types = [args[0] for args, _ in mock_signal.call_args_list]
        
        # Verify that SIGINT and SIGTERM were registered
        assert signal.SIGINT in signal_types
        assert signal.SIGTERM in signal_types
        
        # Verify that each handler is a cleanup handler
        for args, _ in mock_signal.call_args_list:
            handler = args[1]
            assert callable(handler)