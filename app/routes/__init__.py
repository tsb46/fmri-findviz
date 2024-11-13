"""Flask routes"""
from app.routes import common
from app.routes import gifti
from app.routes import nifti
from app.routes import utils

__all__ = [
    'common',
    'gifti',
    'nifti',
    'utils'
]