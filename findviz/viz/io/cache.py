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

from findviz.logger_config import setup_logger

logger = setup_logger(__name__)
class Cache:
    """Class for managing temporary cache of uploaded files and data"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            # Initialize instance attributes here
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the cache instance"""
        self.temp_dir = Path(tempfile.gettempdir()) / "findviz_cache"
        self.temp_dir.mkdir(exist_ok=True)
        self.cache_file = self.temp_dir / "viewer_cache.json"
        
        # Register cleanup on exit
        atexit.register(self.cleanup)

        # Register signal handlers
        try:
            # Handle Ctrl+C (SIGINT)
            signal.signal(signal.SIGINT, cleanup_handler(self))
            # Handle termination (SIGTERM)
            signal.signal(signal.SIGTERM, cleanup_handler(self))
        except (ValueError, AttributeError):
            pass

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
            # Create parent directory if it doesn't exist
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            # serialize data
            serialized_data = self._serialize_data(data)
            # save to cache file
            with open(self.cache_file, 'w') as f:
                json.dump(serialized_data, f)
            logger.info(f"Viewer metadata saved to cache at {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")
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
            logger.error(f"Failed to load cache: {str(e)}")
            raise IOError(f"Failed to load cache: {str(e)}") from e

    def clear(self, during_shutdown=False):
        """Clear all cached data"""
        if not during_shutdown:
            logger.info("Clearing cache...")
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                if not during_shutdown:
                    logger.info("Cache cleared successfully")
        except Exception as e:
            if not during_shutdown:
                logger.error(f"Failed to clear cache: {str(e)}")
            else:
                print(f"Warning: Failed to clear cache: {str(e)}")
            if not during_shutdown:
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
            self.clear(during_shutdown=True)  # Pass flag to avoid logging
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
        cache.clear(during_shutdown=True)  # Pass the flag here too
        # Exit gracefully
        exit(0)
    return handler
