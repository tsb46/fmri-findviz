"""
Viewer IO routes
"""

from io import BytesIO

from flask import Blueprint, request, send_file, make_response

from findviz.logger_config import setup_logger
from findviz.routes.utils import (
    Routes
)
from findviz.routes.shared import data_manager

# Set up a logger for the app
logger = setup_logger(__name__)
io_bp = Blueprint('io', __name__)


@io_bp.route(Routes.SAVE_SCENE.value, methods=['POST'])
def save_scene() -> dict:
    """
    Save the current scene
    """

    # Get serialized data from DataManager
    serialized_data = data_manager.save()
    
    # Create a BytesIO object from the serialized data
    mem_file = BytesIO(serialized_data)
    mem_file.seek(0)
    
    # Create a response with the file data
    response = send_file(
        mem_file,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='scene'
    )
    
    # Set headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # return response
    return response
