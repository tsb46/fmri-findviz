"""Flask routes"""
from findviz.routes import file
from findviz.routes.viewer import color, io, plot, preprocess, data
from findviz.routes import utils


__all__ = [
    'color',
    'data',
    'file',
    'io',
    'plot',
    'preprocess',
    'utils',
]
