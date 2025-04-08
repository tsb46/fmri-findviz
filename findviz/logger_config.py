import logging
import os
from pathlib import Path
import time

def setup_logger(name=__name__, disable_file_logging=False):
    """
    Logger set up for findviz app
    
    Parameters
    ----------
    name : str
        Logger name
    disable_file_logging : bool
        If True, only console logging will be enabled (useful for testing)
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        # Create a formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        # Create a file handler if not disabled
        if not disable_file_logging:
            # Get the current working directory and ensure logs directory exists
            current_dir = os.getcwd()
            log_dir = os.path.join(current_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Create a run-specific log file with timestamp
            run_timestamp = time.strftime("%Y%m%d-%H%M%S")
            log_file_path = os.path.join(log_dir, f'app-run-{run_timestamp}.log')
            
            # Set up a file handler for this run
            file_handler = logging.FileHandler(
                filename=log_file_path,
                encoding='utf-8'
            )
            
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)
    
    return logger