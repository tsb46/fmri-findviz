"""
Routes for display of color maps
"""
from enum import Enum

import plotly.colors as pc

from flask import Blueprint, make_response
 
from findviz.logger_config import setup_logger

# Set up a logger for the app
logger = setup_logger(__name__)

color_bp = Blueprint('color', __name__)

class ColorMaps(Enum):
    """
    Enum for color maps
    """
    GREYS = 'Greys'
    YLGNBU = 'YlGnBu'
    GREENS = 'Greens'
    YLORRD = 'YlOrRd'
    BLUERED = 'Bluered'
    RDBU = 'RdBu'
    REDS = 'Reds'
    BLUES = 'Blues'
    PICNIC = 'Picnic'
    RAINBOW = 'Rainbow'
    PORTLAND = 'Portland'
    JET = 'Jet'
    HOT = 'Hot'
    BLACKBODY = 'Blackbody'
    ELECTRIC = 'Electric'
    VIRIDIS = 'Viridis'
    CIVIDIS = 'Cividis'

# Route to provide colormap data
@color_bp.route('/get_colormaps', methods=['GET'])
def get_colormaps():
    try:
        colormap_data = generate_colormap_data(ColorMaps)
        return make_response(colormap_data, 200)
    except Exception as e:
        logger.critical(f"Error generating colormap data: {e}")
        error_message = f"Error generating colormap data"
        return make_response(error_message, 500)


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
