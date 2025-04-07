"""Tests for the components module."""

import pytest
import numpy as np
from findviz.viz.viewer.state.components import (
    ColorMaps,
    TimeCourseColor,
    AnnotationMarkerPlotOptions,
    DistancePlotOptions,
    FmriPlotOptions,
    TimeCoursePlotOptions,
    TimeCourseGlobalPlotOptions,
    TimeMarkerPlotOptions,
    TaskDesignPlotOptions
)
from findviz.viz.analysis.scaler import SignalScaler, SignalShifter

def test_color_maps_enum():
    """Test ColorMaps enum."""
    assert ColorMaps.GREYS.value == 'Greys'
    assert ColorMaps.VIRIDIS.value == 'Viridis'
    assert ColorMaps.RDBU.value == 'RdBu'
    assert len(ColorMaps) == 17 # Check total number of color maps

def test_time_course_color_enum():
    """Test TimeCourseColor enum."""
    assert TimeCourseColor.RED.value == 'red'
    assert TimeCourseColor.BLUE.value == 'blue'
    assert TimeCourseColor.GREEN.value == 'green'
    assert len(TimeCourseColor) == 30  # Check total number of colors

def test_annotation_marker_plot_options():
    """Test AnnotationMarkerPlotOptions class."""
    # Test default values
    options = AnnotationMarkerPlotOptions()
    assert options.opacity == 0.8
    assert options.width == 1.5
    assert options.shape == 'solid'
    assert options.color == TimeCourseColor.RED
    assert options.highlight is True
    
    # Test to_dict method
    options_dict = options.to_dict()
    assert options_dict['opacity'] == 0.8
    assert options_dict['width'] == 1.5
    assert options_dict['shape'] == 'solid'
    assert options_dict['color'] == 'red'
    assert options_dict['highlight'] is True
    
    # Test update_from_dict method
    new_options = {
        'opacity': 0.5,
        'width': 2.0,
        'shape': 'dash',
        'color': 'blue',
        'highlight': False
    }
    options.update_from_dict(new_options)
    assert options.opacity == 0.5
    assert options.width == 2.0
    assert options.shape == 'dash'
    assert options.color == TimeCourseColor.BLUE
    assert options.highlight is False

def test_distance_plot_options():
    """Test DistancePlotOptions class."""
    # Test default values
    options = DistancePlotOptions()
    assert options.color_min is None
    assert options.color_max is None
    assert options.color_range is None
    assert options.color_map == ColorMaps.RDBU
    assert options.precision == 6
    
    # Test to_dict method
    options.color_min = -1.0
    options.color_max = 1.0
    options.color_range = 2.0
    options_dict = options.to_dict()
    assert options_dict['color_min'] == -1.0
    assert options_dict['color_max'] == 1.0
    assert options_dict['color_range'] == 2.0
    assert options_dict['color_map'] == 'RdBu'
    
    # Test update_from_dict method
    new_options = {
        'color_min': -2.0,
        'color_max': 2.0,
        'color_map': 'Viridis',
        'precision': 4
    }
    options.update_from_dict(new_options)
    assert options.color_min == -2.0
    assert options.color_max == 2.0
    assert options.color_map == ColorMaps.VIRIDIS
    assert options.precision == 4

def test_fmri_plot_options():
    """Test FmriPlotOptions class."""
    # Test default values
    options = FmriPlotOptions()
    assert options.color_min is None
    assert options.color_max is None
    # VIRIDIS is the default color map
    assert options.color_map == ColorMaps.VIRIDIS

    # Test to_dict method
    options.color_min = -1.0
    options.color_max = 1.0
    options_dict = options.to_dict()
    assert options_dict['color_min'] == -1.0
    assert options_dict['color_max'] == 1.0
    assert options_dict['color_map'] == 'Viridis'
    
    # Test update_from_dict method
    new_options = {
        'color_min': -2.0,
        'color_max': 2.0,
        'color_map': 'RdBu'
    }
    options.update_from_dict(new_options)
    assert options.color_min == -2.0
    assert options.color_max == 2.0
    assert options.color_map == ColorMaps.RDBU

def test_time_course_global_plot_options():
    """Test TimeCourseGlobalPlotOptions class."""
    # Test default values
    options = TimeCourseGlobalPlotOptions()
    assert options.global_min is None
    assert options.global_max is None
    assert options.default_global_min == -1.0
    assert options.default_global_max == 1.0
    assert options.shift_unit == 1.0
    assert options.scale_unit == 0.1
    
    # Test to_dict method
    options.global_min = -2.0
    options.global_max = 2.0
    options_dict = options.to_dict()
    assert options_dict['global_min'] == -2.0
    assert options_dict['global_max'] == 2.0
    assert options_dict['shift_unit'] == 1.0
    assert options_dict['scale_unit'] == 0.1
    
    # Test update_from_dict method
    new_options = {
        'global_min': -3.0,
        'global_max': 3.0,
        'shift_unit': 0.2,
        'scale_unit': 0.2
    }
    options.update_from_dict(new_options)
    assert options.global_min == -3.0
    assert options.global_max == 3.0
    assert options.shift_unit == 0.2
    assert options.scale_unit == 0.2

def test_time_course_plot_options():
    """Test TimeCoursePlotOptions class."""
    # Test default values
    options = TimeCoursePlotOptions(label='test')
    assert options.label == 'test'
    assert options.color == TimeCourseColor.RED
    assert options.width == 2.0
    assert options.opacity == 1.0
    assert options.mode == 'lines'
    assert isinstance(options.scale, SignalScaler)
    assert isinstance(options.constant, SignalShifter)
    
    # Test with_color class method
    blue_options = TimeCoursePlotOptions.with_color(TimeCourseColor.BLUE, label='blue_test')
    assert blue_options.color == TimeCourseColor.BLUE
    assert blue_options.label == 'blue_test'
    
    # Test with_next_color class method
    used_colors = {TimeCourseColor.RED, TimeCourseColor.BLUE}
    next_color_options = TimeCoursePlotOptions.with_next_color(used_colors, label='next_color')
    assert next_color_options.color not in used_colors
    assert next_color_options.label == 'next_color'
    
    # Test to_dict method
    options_dict = options.to_dict()
    assert options_dict['label'] == 'test'
    assert options_dict['color'] == 'red'
    assert options_dict['width'] == 2.0
    
    # Test update_from_dict method
    new_options = {
        'color': 'blue',
        'width': 3.0,
        'opacity': 0.8,
        'mode': 'markers',
        'constant': [0.0, 1.0, 2.0],
        'scale': [1.0, 1.1, 1.2]
    }
    options.update_from_dict(new_options)
    assert options.color == TimeCourseColor.BLUE
    assert options.width == 3.0
    assert options.opacity == 0.8
    assert options.mode == 'markers'
    assert options.constant.shift_history == [0.0, 1.0, 2.0]
    assert options.scale.scale_history == [1.0, 1.1, 1.2]

def test_time_marker_plot_options():
    """Test TimeMarkerPlotOptions class."""
    # Test default values
    options = TimeMarkerPlotOptions()
    assert options.opacity == 0.5
    assert options.width == 1.0
    assert options.shape == 'solid'
    assert options.color == TimeCourseColor.GREY
    
    # Test to_dict method
    options_dict = options.to_dict()
    assert options_dict['opacity'] == 0.5
    assert options_dict['width'] == 1.0
    assert options_dict['shape'] == 'solid'
    assert options_dict['color'] == 'grey'
    
    # Test update_from_dict method
    new_options = {
        'opacity': 0.7,
        'width': 2.0,
        'shape': 'dash',
        'color': 'blue'
    }
    options.update_from_dict(new_options)
    assert options.opacity == 0.7
    assert options.width == 2.0
    assert options.shape == 'dash'
    assert options.color == TimeCourseColor.BLUE

def test_task_design_plot_options():
    """Test TaskDesignPlotOptions class."""
    # Test default values
    options = TaskDesignPlotOptions(label='task')
    assert options.label == 'task'
    assert options.convolution == 'hrf'
    assert options.color == TimeCourseColor.RED
    assert options.width == 2.0
    assert options.opacity == 1.0
    assert options.mode == 'lines'
    assert isinstance(options.scale, SignalScaler)
    assert isinstance(options.constant, SignalShifter)
    
    # Test with_color class method
    blue_options = TaskDesignPlotOptions.with_color(TimeCourseColor.BLUE, label='blue_task')
    assert blue_options.color == TimeCourseColor.BLUE
    assert blue_options.label == 'blue_task'
    
    # Test with_next_color class method
    used_colors = {TimeCourseColor.RED, TimeCourseColor.BLUE}
    next_color_options = TaskDesignPlotOptions.with_next_color(used_colors, label='next_color')
    assert next_color_options.color not in used_colors
    assert next_color_options.label == 'next_color'
    
    # Test to_dict method
    options_dict = options.to_dict()
    assert options_dict['label'] == 'task'
    assert options_dict['convolution'] == 'hrf'
    assert options_dict['color'] == 'red'
    
    # Test update_from_dict method
    new_options = {
        'convolution': 'block',
        'color': 'blue',
        'width': 3.0,
        'opacity': 0.8,
        'mode': 'markers',
        'constant': [0.0, 1.0, 2.0],
        'scale': [1.0, 1.1, 1.2]
    }
    options.update_from_dict(new_options)
    assert options.convolution == 'block'
    assert options.color == TimeCourseColor.BLUE
    assert options.width == 3.0
    assert options.opacity == 0.8
    assert options.mode == 'markers'
    assert options.constant.shift_history == [0.0, 1.0, 2.0]
    assert options.scale.scale_history == [1.0, 1.1, 1.2]
