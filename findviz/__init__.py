"""Register routes"""

from flask import Flask

flask_app = Flask(__name__)

# Import the blueprints
from findviz.routes.nifti import nifti_bp
from findviz.routes.gifti import gifti_bp
from findviz.routes.common import common_bp

# Register the blueprints
flask_app.register_blueprint(nifti_bp)
flask_app.register_blueprint(gifti_bp)
flask_app.register_blueprint(common_bp)