"""Flask routes"""
from findviz.routes import common
from findviz.routes import gifti
from findviz.routes import nifti
from findviz.routes import utils

__all__ = [
    'common',
    'gifti',
    'nifti',
    'utils'
]