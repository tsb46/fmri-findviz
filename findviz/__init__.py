"""Register routes"""

from flask import Flask

def create_app():
    """Application factory function."""
    app = Flask(__name__)

    # Import the blueprints
    from findviz.routes.nifti import nifti_bp
    from findviz.routes.gifti import gifti_bp
    from findviz.routes.common import common_bp

    # Register the blueprints
    app.register_blueprint(nifti_bp)
    app.register_blueprint(gifti_bp)
    app.register_blueprint(common_bp)

    return app