import logging

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
            file_handler = logging.FileHandler('app.log')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)
    
    return logger
