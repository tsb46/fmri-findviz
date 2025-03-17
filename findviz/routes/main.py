"""
Main application routes.
"""
from flask import Blueprint, render_template

from findviz.routes.shared import data_manager

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

# display analysis view for a specific analysis route
@main_bp.route('/analysis_view/<analysis>')
def analysis_view(analysis):
    """Display the analysis view for a specific analysis."""
    if analysis == 'average':
        data_manager.switch_context('average')
    elif analysis == 'correlate':
        data_manager.switch_context('correlate')
    
    # get the plot type
    plot_type = data_manager.ctx.fmri_file_type

    return render_template(
        'analysis.html', 
        plot_type=plot_type,
        analysis=analysis
    )