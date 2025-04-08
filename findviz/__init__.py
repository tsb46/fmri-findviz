"""
FIND Viewer: FMRI Interactive Navigation and Discovery Viewer

This package provides tools for visualizing and discovering patterns in fMRI data.
"""

from flask import Flask
from findviz.logger_config import setup_logger
from findviz.viz.io.cache import Cache

# Import core findviz module
from findviz import viz

# Set up package-level logger
logger = setup_logger(__name__)


def create_app(clear_cache=False, testing=False):
    """Application factory function."""
    app = Flask(__name__)

    # Clean up any existing cache on startup
    if clear_cache:
        cache = Cache()
        if cache.exists():
            cache.clear()
            logger.info("Cache cleared on startup")
    
    if testing:
        app.config.update({
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        })
        
    # Import the blueprints
    from findviz.routes.file import file_bp
    from findviz.routes.main import main_bp
    from findviz.routes.viewer.analysis import analysis_bp
    from findviz.routes.viewer.color import color_bp
    from findviz.routes.viewer.data import data_bp
    from findviz.routes.viewer.io import io_bp
    from findviz.routes.viewer.plot import plot_bp
    from findviz.routes.viewer.preprocess import preprocess_bp
    from findviz.routes.viewer.logs import logs_bp


    # Register the blueprints
    app.register_blueprint(file_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(color_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(io_bp)
    app.register_blueprint(plot_bp)
    app.register_blueprint(preprocess_bp)
    app.register_blueprint(logs_bp)

    return app

# Version information
__version__ = '0.1.0'

__all__ = [
    # Core functionality
    'viz',

    # Utilities
    'setup_logger',
    
    # Version
    '__version__'
]
