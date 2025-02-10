"""Flask routes"""
from findviz.routes import file
from findviz.routes.viewer import color, plot, preprocess, data
from findviz.routes import utils


__all__ = [
    'color',
    'file',
    'preprocess',
    'utils',
    'data',
    'plot'
]
