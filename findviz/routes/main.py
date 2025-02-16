"""
Main application routes.
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')