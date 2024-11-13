"""Register routes"""

from flask import Flask

# Rename the Flask app instance to avoid conflict with 'app' directory
flask_app = Flask(__name__)

# Import the blueprints
from app.routes.nifti import nifti_bp
from app.routes.gifti import gifti_bp
from app.routes.common import common_bp

# Register the blueprints
flask_app.register_blueprint(nifti_bp)
flask_app.register_blueprint(gifti_bp)
flask_app.register_blueprint(common_bp)