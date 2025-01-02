"""
Module for caching uploaded files and data
"""
import atexit
import json
import signal
import tempfile

from pathlib import Path

import nibabel as nib
import numpy as np

class Cache:
    """Class for managing temporary cache of uploaded files and data"""
    
    def __init__(self):
        """Initialize cache with temporary directory"""
        self.temp_dir = Path(tempfile.gettempdir()) / 'findviz'
        self.cache_file = self.temp_dir / 'cache.json'
        self._ensure_temp_dir()

    def _ensure_temp_dir(self):
        """Ensure temporary directory exists"""
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data):
        """Save data to cache file.
        
        Parameters
        ----------
        data : dict
            Data to cache
            
        Raises
        ------
        IOError
            If saving fails
        """
        try:
            serialized_data = self._serialize_data(data)
            with open(self.cache_file, 'w') as f:
                json.dump(serialized_data, f)
        except Exception as e:
            raise IOError(f"Failed to save cache: {str(e)}") from e

    def load(self):
        """
        Load data from cache file
        
        Returns
        -------
        dict
            Cached data if exists, None otherwise
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            raise IOError(f"Failed to load cache: {str(e)}")

    def clear(self):
        """Clear all cached data"""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception as e:
            raise IOError(f"Failed to clear cache: {str(e)}")

    def exists(self):
        """
        Check if cache exists
        
        Returns
        -------
        bool
            True if cache exists, False otherwise
        """
        return self.cache_file.exists()

    def get_cache_path(self):
        """
        Get path to cache file
        
        Returns
        -------
        Path
            Path to cache file
        """
        return self.cache_file
    

    def cleanup(self):
        """Clean up temporary files on exit"""
        try:
            self.clear()
            if self.temp_dir.exists():
                # Only remove if empty
                if not any(self.temp_dir.iterdir()):
                    self.temp_dir.rmdir()
        except Exception as e:
            print(f"Warning: Failed to clean up cache: {str(e)}")
    
    def _serialize_data(self, data):
        """Serialize data before saving to cache.
        
        Handles Nifti1Image and GiftiImage objects by converting them to 
        serializable dictionaries containing essential information.
        """
        if isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_data(item) for item in data]
        elif isinstance(data, nib.Nifti1Image):
            return {
                '_type': 'Nifti1Image',
                'shape': data.shape,
                'affine': data.affine.tolist(),
                'header': {
                    'dim': data.header['dim'].tolist(),
                    'pixdim': data.header['pixdim'].tolist()
                }
            }
        elif isinstance(data, nib.GiftiImage):
            return {
                '_type': 'GiftiImage',
                'darrays': [arr.data.shape for arr in data.darrays]
            }
        elif isinstance(data, np.ndarray):
            return data.tolist()
        return data

def cleanup_handler(cache):
    """Handler for cleanup on exit"""
    def handler(signum, frame):
        print("\nCleaning up cache...")
        cache.cleanup()
        # Exit gracefully
        exit(0)
    return handler

# Create single cache instance
cache = Cache()

# Register cleanup for normal exit
atexit.register(cache.cleanup)

# Register signal handlers
try:
    # Handle Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, cleanup_handler(cache))
    # Handle termination (SIGTERM)
    signal.signal(signal.SIGTERM, cleanup_handler(cache))
except (ValueError, AttributeError):
    pass