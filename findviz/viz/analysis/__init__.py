"""
Analysis tools for findviz viewer
"""

from findviz.viz.analysis.peak_finder import PeakFinder
from findviz.viz.analysis.distance import Distance
from findviz.viz.analysis.correlate import Correlate
from findviz.viz.analysis.average import WindowAverage

__all__ = [
    'PeakFinder',
    'Distance',
    'Correlate',
    'WindowAverage',
]