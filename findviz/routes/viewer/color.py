"""
Routes for display of color maps
"""
from enum import Enum

import plotly.colors as pc

from flask import Blueprint
 
from findviz.logger_config import setup_logger
from findviz.routes.utils import (
    handle_route_errors, 
    Routes
)
from findviz.viz.viewer.state.components import ColorMaps
from findviz.routes.shared import data_manager

# Set up a logger for the app
logger = setup_logger(__name__)

color_bp = Blueprint('color', __name__)

# Route to provide colormap data
@color_bp.route(Routes.GET_COLORMAPS.value, methods=['GET'])
@handle_route_errors(
    error_msg='Error generating colormap data',
    log_msg='Generated colormap data successfully',
    fmri_file_type=lambda: data_manager.ctx.fmri_file_type,
    route=Routes.GET_COLORMAPS
)
def get_colormaps() -> dict:
    """Get colormap data"""
    return generate_colormap_data(ColorMaps)


def generate_colormap_data(
    colormaps: list[ColorMaps]
) -> dict[str, dict[str, str]]:
    """
    Generate colormap data

    Arguments
    ---------
    colormaps : list[ColorMaps]
        List of color maps

    Returns
    -------
    dict[str, dict[str, str]]
        Colormap data
    """
    colormap_data = {}
    for cmap in colormaps:
        # Get the colorscale for each colormap
        colormap_colors = pc.get_colorscale(cmap.value)
        # Convert Plotly color codes to rgb
        rgb_colors = [
            (pos, code_to_rgb(color_code))
            for pos, color_code in colormap_colors
        ]
        # Put into html
        gradient = "linear-gradient(to right, " + ", ".join(
            [f"rgb({r},{g},{b})" for pos, (r, g, b) in rgb_colors]
        ) + ")"
        # package output
        colormap_data[cmap.value] = {
            'label': cmap.value,
            'gradient': gradient
        }
    return colormap_data


def code_to_rgb(color_code: str) -> list[int]:
    """
    Convert color code to rgb

    Arguments
    ---------
    color_code : str
        Color code

    Returns
    -------
    list[int]
        RGB values
    """
    # if hex format
    if color_code.startswith('#'):
        color_rgb = pc.hex_to_rgb(color_code)
    # otherwise, assume rgb
    else:
        # clean string
        color_clean = color_code.replace('rgb(','').replace(')','')
        color_rgb = [int(c) for c in color_clean.split(',')]
    return color_rgb
