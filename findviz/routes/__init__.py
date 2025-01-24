"""Flask routes"""
from findviz.routes import file
from findviz.routes.viewer import color, preprocess, data, plot_options
from findviz.routes import utils


__all__ = [
    'color',
    'file',
    'preprocess',
    'utils',
    'data',
    'plot_options'
]
