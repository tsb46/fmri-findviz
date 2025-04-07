"""Tests for the visualization state module."""

import pytest
import numpy as np
from dataclasses import asdict

from findviz.viz.viewer.state.viz_state import (
    VisualizationState,
    NiftiVisualizationState,
    GiftiVisualizationState
)
from findviz.viz.viewer.state.components import (
    FmriPlotOptions,
    TimeCoursePlotOptions,
    TimeCourseGlobalPlotOptions,
    ColorMaps,
    AnnotationMarkerPlotOptions,
    TimeMarkerPlotOptions,
    DistancePlotOptions
)

def test_visualization_state_init():
    """Test initialization of base VisualizationState."""
    state = VisualizationState()
    
    # Check default values
    assert state.tr is None
    assert state.slicetime_ref is None
    assert state.timepoints is None
    assert state.timepoints_seconds is None
    assert state.global_min is None
    assert state.global_max is None
    assert state.file_type is None
    assert state.timepoint == 0
    assert isinstance(state.fmri_plot_options, FmriPlotOptions)
    assert isinstance(state.preprocessed_fmri_plot_options, FmriPlotOptions)
    assert state.ts_enabled is False
    assert state.task_enabled is False
    assert state.fmri_preprocessed is False
    assert state.ts_preprocessed == {}
    assert state.used_colors == set()
    assert isinstance(state.time_course_global_plot_options, TimeCourseGlobalPlotOptions)
    assert state.ts_data == {}
    assert state.ts_data_preprocessed == {}
    assert state.ts_labels == []
    assert state.ts_type == {}
    assert state.ts_labels_preprocessed == []
    assert state.ts_fmri_plotted is False
    assert state.ts_plot_options == {}
    assert state.task_data == {}
    assert state.task_plot_options == {}
    assert state.annotation_markers == []
    assert state.annotation_selection is None
    assert isinstance(state.annotation_marker_plot_options, AnnotationMarkerPlotOptions)
    assert isinstance(state.time_marker_plot_options, TimeMarkerPlotOptions)
    assert state.distance_data is None
    assert state.distance_data_enabled is False
    assert state.distance_plot_options is None

def test_nifti_visualization_state_init():
    """Test initialization of NiftiVisualizationState."""
    state = NiftiVisualizationState()
    
    # Check that it inherits from VisualizationState
    assert isinstance(state, VisualizationState)
    
    # Check NIFTI-specific default values
    assert state.file_type == 'nifti'
    assert state.anat_input is False
    assert state.mask_input is False
    assert state.nifti_data == {}
    assert state.nifti_data_preprocessed == {}
    assert state.func_header is None
    assert state.func_affine is None
    assert state.view_state == 'ortho'
    assert state.slice_len is None
    assert state.coord_labels is None
    assert state.ortho_slice_idx == {}
    assert state.montage_slice_idx == {}
    assert state.ortho_slice_coords == {}
    assert state.montage_slice_coords == {}
    assert state.montage_slice_dir == 'z'
    assert state.selected_slice == 'slice_1'
    assert state.distance_data is None
    assert state.distance_data_enabled is False
    assert state.distance_plot_options is None

def test_gifti_visualization_state_init():
    """Test initialization of GiftiVisualizationState."""
    state = GiftiVisualizationState()
    
    # Check that it inherits from VisualizationState
    assert isinstance(state, VisualizationState)
    
    # Check GIFTI-specific default values
    assert state.file_type == 'gifti'
    assert state.left_input is False
    assert state.right_input is False
    assert state.vertices_left is None
    assert state.faces_left is None
    assert state.vertices_right is None
    assert state.faces_right is None
    assert state.both_hemispheres is False
    assert state.gifti_data == {}
    assert state.gifti_data_preprocessed == {}
    assert state.selected_vertex is None
    assert state.selected_hemi is None
    assert state.left_coord_labels is None
    assert state.right_coord_labels is None

def test_nifti_state_with_custom_values():
    """Test NiftiVisualizationState with custom values."""
    # Create state with custom values
    state = NiftiVisualizationState(
        tr=2.0,
        slicetime_ref=0.5,
        timepoints=[0, 1, 2, 3],
        timepoints_seconds=[0.0, 2.0, 4.0, 6.0],
        global_min=-1.0,
        global_max=1.0,
        timepoint=2,
        anat_input=True,
        mask_input=True,
        slice_len={'x': 64, 'y': 64, 'z': 32},
        view_state='montage',
        montage_slice_dir='x',
        selected_slice='slice_2'
    )
    
    # Check custom values
    assert state.tr == 2.0
    assert state.slicetime_ref == 0.5
    assert state.timepoints == [0, 1, 2, 3]
    assert state.timepoints_seconds == [0.0, 2.0, 4.0, 6.0]
    assert state.global_min == -1.0
    assert state.global_max == 1.0
    assert state.timepoint == 2
    assert state.anat_input is True
    assert state.mask_input is True
    assert state.slice_len == {'x': 64, 'y': 64, 'z': 32}
    assert state.view_state == 'montage'
    assert state.montage_slice_dir == 'x'
    assert state.selected_slice == 'slice_2'

def test_gifti_state_with_custom_values():
    """Test GiftiVisualizationState with custom values."""
    # Create state with custom values
    state = GiftiVisualizationState(
        tr=2.0,
        timepoints=[0, 1, 2, 3],
        global_min=-1.0,
        global_max=1.0,
        timepoint=2,
        left_input=True,
        right_input=True,
        vertices_left=np.array([[0, 0, 0], [1, 1, 1]]),
        faces_left=np.array([[0, 1, 2]]),
        vertices_right=np.array([[3, 3, 3], [4, 4, 4]]),
        faces_right=np.array([[0, 1, 2]])
    )
    
    # Check custom values
    assert state.tr == 2.0
    assert state.timepoints == [0, 1, 2, 3]
    assert state.global_min == -1.0
    assert state.global_max == 1.0
    assert state.timepoint == 2
    assert state.left_input is True
    assert state.right_input is True
    assert np.array_equal(state.vertices_left, np.array([[0, 0, 0], [1, 1, 1]]))
    assert np.array_equal(state.faces_left, np.array([[0, 1, 2]]))
    assert np.array_equal(state.vertices_right, np.array([[3, 3, 3], [4, 4, 4]]))
    assert np.array_equal(state.faces_right, np.array([[0, 1, 2]]))
    assert state.both_hemispheres is True  # Should be set in post_init

def test_nifti_state_post_init():
    """Test NiftiVisualizationState post-initialization logic."""
    # Test with func_data
    func_data = np.zeros((64, 64, 32, 10))
    state = NiftiVisualizationState()
    state.func_data = func_data
    
    # Test with both hemispheres
    state = GiftiVisualizationState(left_input=True, right_input=True)
    assert state.both_hemispheres is True
    
    # Test with only left hemisphere
    state = GiftiVisualizationState(left_input=True, right_input=False)
    assert state.both_hemispheres is False
    
    # Test with only right hemisphere
    state = GiftiVisualizationState(left_input=False, right_input=True)
    assert state.both_hemispheres is False

def test_state_with_timecourse_data():
    """Test state with time course data."""
    state = NiftiVisualizationState()
    
    # Add time course data
    state.ts_enabled = True
    state.ts_data = {
        'ROI1': np.array([1.0, 2.0, 3.0]),
        'ROI2': np.array([3.0, 2.0, 1.0])
    }
    state.ts_labels = ['ROI1', 'ROI2']
    state.ts_type = {'ROI1': 'user', 'ROI2': 'user'}
    state.ts_plot_options = {
        'ROI1': TimeCoursePlotOptions(label='ROI1'),
        'ROI2': TimeCoursePlotOptions(label='ROI2')
    }
    
    # Check that data was added correctly
    assert state.ts_enabled is True
    assert 'ROI1' in state.ts_data
    assert 'ROI2' in state.ts_data
    assert np.array_equal(state.ts_data['ROI1'], np.array([1.0, 2.0, 3.0]))
    assert np.array_equal(state.ts_data['ROI2'], np.array([3.0, 2.0, 1.0]))
    assert state.ts_labels == ['ROI1', 'ROI2']
    assert state.ts_type['ROI1'] == 'user'
    assert state.ts_type['ROI2'] == 'user'
    assert state.ts_plot_options['ROI1'].label == 'ROI1'
    assert state.ts_plot_options['ROI2'].label == 'ROI2'

def test_state_with_task_data():
    """Test state with task design data."""
    state = NiftiVisualizationState()
    
    # Add task design data
    state.task_enabled = True
    state.task_data = {
        'cond1': {
            'block': [1.0, 0.0, 1.0],
            'hrf': [0.8, 0.2, 0.8]
        },
        'cond2': {
            'block': [0.0, 1.0, 0.0],
            'hrf': [0.2, 0.8, 0.2]
        }
    }
    
    # Check that data was added correctly
    assert state.task_enabled is True
    assert 'cond1' in state.task_data
    assert 'cond2' in state.task_data
    assert 'block' in state.task_data['cond1']
    assert 'hrf' in state.task_data['cond1']
    assert state.task_data['cond1']['block'] == [1.0, 0.0, 1.0]
    assert state.task_data['cond1']['hrf'] == [0.8, 0.2, 0.8]
    assert state.task_data['cond2']['block'] == [0.0, 1.0, 0.0]
    assert state.task_data['cond2']['hrf'] == [0.2, 0.8, 0.2]

def test_state_with_annotation_markers():
    """Test state with annotation markers."""
    state = NiftiVisualizationState()
    
    # Add annotation markers
    state.annotation_markers = [10, 20, 30]
    state.annotation_selection = 20
    
    # Check that markers were added correctly
    assert state.annotation_markers == [10, 20, 30]
    assert state.annotation_selection == 20
