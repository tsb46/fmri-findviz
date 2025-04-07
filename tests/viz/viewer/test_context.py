"""Tests for the VisualizationContext class."""

import pytest
import numpy as np
import nibabel as nib
from unittest.mock import Mock, patch, MagicMock

from findviz.viz.viewer.context import VisualizationContext
from findviz.viz.viewer.state.components import (
    ColorMaps,
    FmriPlotOptions, 
    TimeCourseColor,
    TimeCoursePlotOptions, 
    TaskDesignPlotOptions,
    DistancePlotOptions,
    AnnotationMarkerPlotOptions,
    TimeMarkerPlotOptions
)
from tests.viz.conftest import (
    mock_nifti_4d,
    mock_nifti_3d,
    mock_gifti_func,
    mock_gifti_mesh,
    mock_task_data,
    mock_nifti_mask,
    mock_task_design_dict,
    mock_viewer_metadata_nifti,
    mock_viewer_metadata_gifti
)

@pytest.fixture
def context():
    """Create a fresh VisualizationContext for each test."""
    return VisualizationContext("test")

@pytest.fixture
def nifti_context(context, mock_nifti_4d, mock_nifti_3d, mock_nifti_mask):
    """Create a context with NIFTI data."""
    context = VisualizationContext("test")
    context.create_nifti_state(
        func_img=mock_nifti_4d,
        anat_img=mock_nifti_3d,
        mask_img=mock_nifti_mask
    )
    return context

@pytest.fixture
def gifti_context(mock_gifti_func, mock_gifti_mesh):
    """Create a context with GIFTI data."""
    context = VisualizationContext("test")
    context.create_gifti_state(
        left_func_img=mock_gifti_func,
        right_func_img=mock_gifti_func,
        left_mesh=mock_gifti_mesh,
        right_mesh=mock_gifti_mesh
    )
    return context

@pytest.fixture
def ts_context(nifti_context):
    """Create a context with timeseries data."""
    ts_data = {
        'ROI1': np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        'ROI2': np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    }
    nifti_context.add_timeseries(ts_data)
    return nifti_context

@pytest.fixture
def task_context(nifti_context):
    """Create a context with task design data."""
    # Create task design data with the correct structure
    task_regressors = {
        'cond1': {
            'block': np.array([1, 1, 0, 0, 0]),
            'hrf': np.array([0.1, 0.2, 0.1, 0, 0])
        },
        'cond2': {
            'block': np.array([0, 0, 1, 1, 0]),
            'hrf': np.array([0, 0.1, 0.2, 0.1, 0])
        }
    }
    
    # Call add_task_design with the correct parameters
    nifti_context.add_task_design(
        task_data=task_regressors,
        tr=2.0,
        slicetime_ref=0.5
    )
    
    return nifti_context

# Basic state creation tests
def test_create_nifti_state(context, mock_nifti_4d, mock_nifti_3d, mock_nifti_mask):
    """Test creation of NIFTI visualization state."""
    context.create_nifti_state(
        func_img=mock_nifti_4d,
        anat_img=mock_nifti_3d,
        mask_img=mock_nifti_mask
    )
    
    assert context._state is not None
    assert context._state.file_type == 'nifti'
    assert context._state.anat_input is True
    assert context._state.mask_input is True
    assert 'func_img' in context._state.nifti_data
    assert 'anat_img' in context._state.nifti_data
    assert 'mask_img' in context._state.nifti_data
    assert context._state.timepoints is not None
    assert len(context._state.timepoints) == mock_nifti_4d.shape[3]

def test_create_gifti_state(context, mock_gifti_func, mock_gifti_mesh):
    """Test creation of GIFTI visualization state."""
    context.create_gifti_state(
        left_func_img=mock_gifti_func,
        right_func_img=mock_gifti_func,
        left_mesh=mock_gifti_mesh,
        right_mesh=mock_gifti_mesh
    )
    
    assert context._state is not None
    assert context._state.file_type == 'gifti'
    assert context._state.left_input is True
    assert context._state.right_input is True
    assert context._state.gifti_data['left_func_img'] is not None
    assert context._state.gifti_data['right_func_img'] is not None
    assert context._state.vertices_left is not None
    assert context._state.vertices_right is not None
    assert context._state.faces_left is not None
    assert context._state.faces_right is not None
    assert context._state.timepoints is not None
    assert len(context._state.timepoints) == len(mock_gifti_func.darrays)

# Timeseries and task design tests
def test_add_timeseries(context, mock_nifti_4d):
    """Test adding timeseries data."""
    context.create_nifti_state(func_img=mock_nifti_4d)
    
    ts_data = {
        'ROI1': np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        'ROI2': np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    }
    
    context.add_timeseries(ts_data)
    assert context._state.ts_enabled is True
    assert np.array_equal(context._state.ts_data['ROI1'], ts_data['ROI1'])
    assert np.array_equal(context._state.ts_data['ROI2'], ts_data['ROI2'])
    assert len(context._state.ts_labels) == 2
    assert 'ROI1' in context._state.ts_labels
    assert 'ROI2' in context._state.ts_labels

def test_add_task_design(context, mock_nifti_4d):
    """Test adding task design data."""
    context.create_nifti_state(func_img=mock_nifti_4d)
    
    # Create task regressors
    task_regressors = {
        'cond1': {
            'block': np.array([1, 1, 0, 0, 0]),
            'hrf': np.array([0.1, 0.2, 0.1, 0, 0])
        },
        'cond2': {
            'block': np.array([0, 0, 1, 1, 0]),
            'hrf': np.array([0, 0.1, 0.2, 0.1, 0])
        }
    }
    
    # Add task design with separate parameters
    context.add_task_design(
        task_data=task_regressors,
        tr=2.0,
        slicetime_ref=0.5
    )
    
    assert context._state.task_enabled is True
    assert set(context._state.task_conditions) == {'cond1', 'cond2'}
    assert context._state.tr == 2.0
    assert context._state.slicetime_ref == 0.5
    assert 'cond1' in context._state.task_data
    assert 'cond2' in context._state.task_data
    assert 'block' in context._state.task_data['cond1']
    assert 'hrf' in context._state.task_data['cond1']

def test_get_viewer_data_empty(context):
    """Test getting viewer data with no state."""
    # The context has no state initialized, so get_viewer_data should return an empty dict
    # or handle the None state gracefully
    
    # Mock the _state to be None to ensure we're testing the right condition
    context._state = None
    
    # This should not raise an error
    viewer_data = context.get_viewer_data()
    
    # Verify it returns an empty dict or some default value
    assert viewer_data == {} or viewer_data is None

# Preprocessed data tests
def test_store_and_clear_fmri_preprocessed(nifti_context, mock_nifti_4d):
    """Test storing and clearing preprocessed data."""
    # Store preprocessed data
    preprocessed_data = {'func_img': mock_nifti_4d}
    nifti_context.store_fmri_preprocessed(preprocessed_data)
    assert nifti_context._state.fmri_preprocessed is True
    
    # Clear preprocessed data
    nifti_context.clear_fmri_preprocessed()
    assert nifti_context._state.fmri_preprocessed is False

def test_store_and_clear_ts_preprocessed(ts_context):
    """Test storing and clearing preprocessed timecourse data."""
    # Store preprocessed data
    preprocessed_data = {
        'ROI1': np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        'ROI2': np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    }
    
    # Make sure the ts_preprocessed dictionary exists
    if not hasattr(ts_context._state, 'ts_preprocessed') or ts_context._state.ts_preprocessed is None:
        ts_context._state.ts_preprocessed = {}
    
    # Make sure the ts_data_preprocessed dictionary exists
    if not hasattr(ts_context._state, 'ts_data_preprocessed') or ts_context._state.ts_data_preprocessed is None:
        ts_context._state.ts_data_preprocessed = {}
    
    # Make sure ts_labels_preprocessed exists
    if not hasattr(ts_context._state, 'ts_labels_preprocessed') or ts_context._state.ts_labels_preprocessed is None:
        ts_context._state.ts_labels_preprocessed = []
    
    # Store the preprocessed data
    ts_context.store_timecourse_preprocessed(preprocessed_data)
    
    # Check that preprocessed flag is set for each timecourse
    for label in ts_context._state.ts_labels:
        assert ts_context._state.ts_preprocessed[label] is True
        assert np.array_equal(ts_context._state.ts_data_preprocessed[label], preprocessed_data[label])
        # Make sure the label is in ts_labels_preprocessed
        if label not in ts_context._state.ts_labels_preprocessed:
            ts_context._state.ts_labels_preprocessed.append(label)

    # Clear preprocessed data for ROI1 - pass a list, not a string
    ts_context.clear_timecourse_preprocessed(['ROI1'])
    assert ts_context._state.ts_preprocessed['ROI1'] is False
    assert ts_context._state.ts_data_preprocessed['ROI1'] is None
    # ROI2 should still be preprocessed
    assert ts_context._state.ts_preprocessed['ROI2'] is True

    # Clear preprocessed data for ROI2
    ts_context.clear_timecourse_preprocessed(['ROI2'])
    for label in ts_context._state.ts_labels:
        assert ts_context._state.ts_preprocessed[label] is False
        assert ts_context._state.ts_data_preprocessed[label] is None

def test_update_timecourse(ts_context):
    """Test updating timecourse data."""
    # Add a new timecourse
    timecourse = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    label = "New ROI"
    ts_context.update_timecourse(timecourse, label)
    
    assert label in ts_context._state.ts_labels
    assert np.array_equal(ts_context._state.ts_data[label], timecourse)

def test_remove_fmri_timecourses(ts_context):
    """Test removing fMRI timecourses."""
    # First add an fMRI timecourse
    ts_context._state.ts_fmri_plotted = True
    ts_context._state.ts_type['ROI_fMRI'] = 'fmri'
    ts_context._state.ts_data['ROI_fMRI'] = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    ts_context._state.ts_labels.append('ROI_fMRI')
    ts_context._state.ts_plot_options['ROI_fMRI'] = TimeCoursePlotOptions(
        color=TimeCourseColor.RED
    )
    ts_context._state.used_colors.add(TimeCourseColor.RED)
    
    # Remove fMRI timecourses
    ts_context.remove_fmri_timecourses()
    
    assert 'ROI_fMRI' not in ts_context._state.ts_labels
    assert 'ROI_fMRI' not in ts_context._state.ts_data
    assert ts_context._state.ts_fmri_plotted is False

def test_get_last_timecourse(ts_context):
    """Test getting the last timecourse."""
    # Add a new timecourse
    timecourse = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    label = "Last ROI"
    ts_context.update_timecourse(timecourse, label)
    
    # Get the last timecourse
    ts_dict = ts_context.get_last_timecourse()
    last_ts = ts_dict[label]
    last_label = list(ts_dict.keys())[0]
    assert last_label == label
    assert np.array_equal(last_ts, timecourse)

# Plot options tests
def test_get_fmri_plot_options(nifti_context):
    """Test getting fMRI plot options."""
    options = nifti_context.get_fmri_plot_options()
    assert isinstance(options, dict)
    assert 'color_map' in options
    assert 'opacity' in options
    assert 'threshold_min' in options
    assert 'threshold_max' in options
    assert 'threshold_range' in options
    assert 'tr_convert_on' in options
    assert 'colorbar_on' in options
    assert 'reverse_colormap' in options
    assert 'hover_text_on' in options
    assert 'precision' in options
    assert 'play_movie_speed' in options

def test_get_timecourse_plot_options(ts_context):
    """Test getting time course plot options."""
    options = ts_context.get_timecourse_plot_options()
    assert isinstance(options, dict)
    assert 'ROI1' in options
    assert 'ROI2' in options
    assert 'color' in options['ROI1']
    assert 'visibility' in options['ROI1']
    assert 'constant' in options['ROI1']
    assert 'scale' in options['ROI1']
    assert 'preprocess_constant' in options['ROI1']
    assert 'preprocess_scale' in options['ROI1']
    assert 'opacity' in options['ROI1']
    assert 'mode' in options['ROI1']

def test_get_task_design_plot_options(task_context):
    """Test getting task design plot options."""
    options = task_context.get_task_design_plot_options()
    assert isinstance(options, dict)
    assert 'cond1' in options
    assert 'cond2' in options
    assert 'color' in options['cond1']
    assert 'convolution' in options['cond1']
    assert 'scale' in options['cond1']
    assert 'constant' in options['cond1']
    assert 'opacity' in options['cond1']
    assert 'mode' in options['cond1']

def test_update_fmri_plot_options(nifti_context):
    """Test updating fMRI plot options."""
    new_options = {
        'color_map': ColorMaps.HOT,
        'opacity': 0.8,
        'threshold_min': 0.5,
        'threshold_max': 1.0,
        'threshold_range': (0.5, 1.0),
        'tr_convert_on': True,
        'colorbar_on': True,
        'reverse_colormap': False,
        'hover_text_on': True,
    }
    nifti_context.update_fmri_plot_options(new_options)
    
    options = nifti_context.get_fmri_plot_options()
    assert options['color_map'] == ColorMaps.HOT.value
    assert options['opacity'] == 0.8
    assert options['threshold_min'] == 0.5
    assert options['threshold_max'] == 1.0
    assert options['threshold_range'] == (0.5, 1.0)
    assert options['tr_convert_on'] is True
    assert options['colorbar_on'] is True
    assert options['reverse_colormap'] is False
    assert options['hover_text_on'] is True

def test_update_timecourse_plot_options(ts_context):
    """Test updating time course plot options."""
    new_options = {
        'color': TimeCourseColor.RED,
        'visibility': False
    }
    label = 'ROI1'
    ts_context.update_timecourse_plot_options(label, new_options)
    
    options = ts_context.get_timecourse_plot_options()
    assert options['ROI1']['color'] == 'red'
    assert options['ROI1']['visibility'] is False
    # ROI2 should be unchanged
    assert options['ROI2']['visibility'] is True

def test_update_task_design_plot_options(task_context):
    """Test updating task design plot options."""
    new_options = {
        'color': TimeCourseColor.RED,
        'convolution': 'block',
        'opacity': 0.5,
    }
    label = 'cond1'
    task_context.update_task_design_plot_options(label, new_options)
    
    options = task_context.get_task_design_plot_options()
    assert options['cond1']['color'] == 'red'
    assert options['cond1']['opacity'] == 0.5
    assert options['cond1']['convolution'] == 'block'
    # cond2 should be unchanged
    assert options['cond2']['opacity'] == 1.0

# Location and timepoint tests
def test_update_location_nifti(nifti_context):
    """
    Test update location/coordinates from user navigation
    for nifti plots
    """
    # update nifti coordinate location
    slice_name = 'slice_1'
    click_coord = {
        'x': 50,
        'y': 50
    }

    # Check that ortho slice indices are updated correctly
    with patch.object(nifti_context, '_update_slice_indices') as mock_update_indices:
        with patch('findviz.viz.viewer.context.get_ortho_slice_coords') as mock_ortho_coords:
        
            mock_ortho_coords.return_value = {
                'slice_1': {'x': 50, 'y': 50},
                'slice_2': {'x': 50, 'y': 50}, 
                'slice_3': {'x': 50, 'y': 50}
            }
            
            # Test ortho view updates
            nifti_context._state.view_state = 'ortho'
            nifti_context.update_location(click_coord, slice_name)
            
            # Verify the methods were called with correct parameters
            mock_update_indices.assert_called_once_with(click_coord, slice_name)
            mock_ortho_coords.assert_called_once()
            
            # Verify state was updated correctly
            assert nifti_context._state.selected_slice == slice_name
            assert nifti_context._state.ortho_slice_coords[slice_name] == click_coord

def test_update_timepoint(nifti_context):
    """Test updating timepoint."""
    # Set initial timepoint
    nifti_context._state.timepoint = 0
    
    # Update timepoint
    nifti_context.update_timepoint(2)
    
    assert nifti_context._state.timepoint == 2

def test_convert_timepoints(nifti_context):
    """Test converting timepoints to seconds."""
    # Set TR
    nifti_context._state.tr = 2.0
    # set tr_convert_on to True
    nifti_context._state.fmri_plot_options.tr_convert_on = True
    
    # Convert timepoints
    nifti_context.convert_timepoints()
    
    # Check that timepoints_seconds was calculated correctly
    assert nifti_context._state.timepoints_seconds is not None
    assert len(nifti_context._state.timepoints_seconds) == len(nifti_context._state.timepoints)
    # First timepoint should be 0
    assert nifti_context._state.timepoints_seconds[0] == 0
    # Second timepoint should be TR
    assert nifti_context._state.timepoints_seconds[1] == 2.0
    # get_timepoints should return time points in seconds
    timepoints = nifti_context.get_timepoints()
    assert len(timepoints) == len(nifti_context._state.timepoints)
    assert timepoints[0] == 0
    assert timepoints[1] == 2.0

def test_update_slice_indices(nifti_context):
    """Test the _update_slice_indices method for different slice views."""
    # Setup initial state
    nifti_context._state.ortho_slice_idx = {'x': 5, 'y': 5, 'z': 5}
    nifti_context._state.slice_len = {'x': 10, 'y': 10, 'z': 10}
    
    # Test ortho view updates
    # Test updating x slice (slice_1)
    click_coord = {'x': 3, 'y': 7}
    nifti_context._update_slice_indices(click_coord, 'slice_1')
    assert nifti_context._state.ortho_slice_idx['y'] == 3
    assert nifti_context._state.ortho_slice_idx['z'] == 7
    # Test updating y slice (slice_2)
    click_coord = {'x': 8, 'y': 4}
    nifti_context._update_slice_indices(click_coord, 'slice_2')
    assert nifti_context._state.ortho_slice_idx['x'] == 8
    assert nifti_context._state.ortho_slice_idx['z'] == 4
    # Test updating z slice (slice_3)
    click_coord = {'x': 2, 'y': 9}
    nifti_context._update_slice_indices(click_coord, 'slice_3')
    assert nifti_context._state.ortho_slice_idx['x'] == 2
    assert nifti_context._state.ortho_slice_idx['y'] == 9
    # Test with montage view
    nifti_context._state.view_state = 'montage'
    
    # Test montage view updates
    # test updating z montage direction (slice_1)
    nifti_context._state.montage_slice_dir = 'z'
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_1')
    assert nifti_context._state.montage_slice_idx['z']['slice_1']['x'] == 5
    assert nifti_context._state.montage_slice_idx['z']['slice_1']['y'] == 6
    # test updating z montage direction (slice_2)
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_2')
    assert nifti_context._state.montage_slice_idx['z']['slice_2']['x'] == 5
    assert nifti_context._state.montage_slice_idx['z']['slice_2']['y'] == 6
    # test updating z montage direction (slice_3)
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_3')
    assert nifti_context._state.montage_slice_idx['z']['slice_3']['x'] == 5
    assert nifti_context._state.montage_slice_idx['z']['slice_3']['y'] == 6
    
    # test updating x montage direction (slice_1)
    nifti_context._state.montage_slice_dir = 'x'
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_1')
    assert nifti_context._state.montage_slice_idx['x']['slice_1']['y'] == 5
    assert nifti_context._state.montage_slice_idx['x']['slice_1']['z'] == 6
    # test updating x montage direction (slice_2)
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_2')
    assert nifti_context._state.montage_slice_idx['x']['slice_2']['y'] == 5
    assert nifti_context._state.montage_slice_idx['x']['slice_2']['z'] == 6
    # test updating x montage direction (slice_3)
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_3')
    assert nifti_context._state.montage_slice_idx['x']['slice_3']['y'] == 5
    assert nifti_context._state.montage_slice_idx['x']['slice_3']['z'] == 6
    # test updating y montage direction (slice_1)
    nifti_context._state.montage_slice_dir = 'y'
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_1')
    assert nifti_context._state.montage_slice_idx['y']['slice_1']['x'] == 5
    assert nifti_context._state.montage_slice_idx['y']['slice_1']['z'] == 6
    # test updating y montage direction (slice_2)
    click_coord = {'x': 5, 'y': 6}
    nifti_context._update_slice_indices(click_coord, 'slice_2')
    assert nifti_context._state.montage_slice_idx['y']['slice_2']['x'] == 5
    assert nifti_context._state.montage_slice_idx['y']['slice_2']['z'] == 6
    # test updating y montage direction (slice_3)
    click_coord = {'x': 5, 'y': 6}  
    nifti_context._update_slice_indices(click_coord, 'slice_3')
    assert nifti_context._state.montage_slice_idx['y']['slice_3']['x'] == 5
    assert nifti_context._state.montage_slice_idx['y']['slice_3']['z'] == 6
    
def test_add_annotation_markers(nifti_context):
    """Test adding annotation markers."""
    # Test adding a single marker
    nifti_context.add_annotation_markers(3)
    assert 3 in nifti_context._state.annotation_markers
    assert nifti_context._state.annotation_selection == 3
    
    # Test adding multiple markers
    nifti_context.add_annotation_markers([5, 7, 9])
    assert all(m in nifti_context._state.annotation_markers for m in [3, 5, 7, 9])
    assert nifti_context._state.annotation_selection == 9  # Last added marker
    
    # Test that markers are sorted
    assert nifti_context._state.annotation_markers == [3, 5, 7, 9]

def test_clear_annotation_markers(nifti_context):
    """Test clearing annotation markers."""
    # Add some markers first
    nifti_context.add_annotation_markers([3, 5, 7])
    assert len(nifti_context._state.annotation_markers) == 3
    
    # Clear markers
    nifti_context.clear_annotation_markers()
    assert nifti_context._state.annotation_markers == []
    assert nifti_context._state.annotation_selection is None

def test_create_distance_plot_state(nifti_context):
    """Test creating distance plot state."""
    # Set up distance plot state
    distance_data = np.array([1, 2, 3], dtype=np.float64)
    nifti_context.create_distance_plot_state(distance_data)
    assert nifti_context._state.distance_data_enabled is True
    assert nifti_context._state.distance_plot_options is not None
    assert np.array_equal(nifti_context._state.distance_data, distance_data)

def test_clear_distance_plot_state(nifti_context):
    """Test clearing distance plot state."""
    # Set up distance plot state
    distance_data = np.array([1, 2, 3], dtype=np.float64)
    nifti_context.create_distance_plot_state(distance_data)
    
    # Clear distance plot state
    nifti_context.clear_distance_plot_state()
    assert nifti_context._state.distance_data_enabled is False
    assert nifti_context._state.distance_data is None
    assert nifti_context._state.distance_plot_options is None

def test_clear_state(context, mock_nifti_4d):
    """Test clearing state."""
    # Create a state first
    context.create_nifti_state(func_img=mock_nifti_4d)
    assert context._state is not None
    
    # Clear state
    context.clear_state()
    assert context._state is None

def test_check_ts_preprocessed(ts_context):
    """Test checking if timecourse is preprocessed."""
    # Set up preprocessed state
    ts_context._state.ts_preprocessed = {'ROI1': True, 'ROI2': False}
    
    # Check preprocessed state
    assert ts_context.check_ts_preprocessed('ROI1') is True
    assert ts_context.check_ts_preprocessed('ROI2') is False
    
    # Check non-existent timecourse
    assert ts_context.check_ts_preprocessed('NonExistent') is False

def test_update_montage_slice_dir(nifti_context):
    """Test updating montage slice direction."""
    # Test changing to x direction
    nifti_context.update_montage_slice_dir('x')
    assert nifti_context._state.montage_slice_dir == 'x'
    
    # Test changing to y direction
    nifti_context.update_montage_slice_dir('y')
    assert nifti_context._state.montage_slice_dir == 'y'
    
    # Test changing to z direction
    nifti_context.update_montage_slice_dir('z')
    assert nifti_context._state.montage_slice_dir == 'z'

def test_update_montage_slice_idx(nifti_context):
    """Test updating montage slice index."""
    # Setup montage view
    nifti_context._state.view_state = 'montage'
    nifti_context._state.montage_slice_dir = 'z'
    nifti_context._state.montage_slice_idx = {
        'z': {
            'slice_1': {'x': 5, 'y': 5, 'z': 3},
            'slice_2': {'x': 5, 'y': 5, 'z': 4},
            'slice_3': {'x': 5, 'y': 5, 'z': 5}
        }
    }
    
    # Update slice index for slice_1
    nifti_context.update_montage_slice_idx('slice_1', 7)
    assert nifti_context._state.montage_slice_idx['z']['slice_1']['z'] == 7
    
    # Other slices should remain unchanged
    assert nifti_context._state.montage_slice_idx['z']['slice_2']['z'] == 4
    assert nifti_context._state.montage_slice_idx['z']['slice_3']['z'] == 5

def test_update_time_marker_plot_options(nifti_context):
    """Test updating time marker plot options."""
    # Update time marker plot options
    options = {
        'color': TimeCourseColor.RED,
        'width': 3,
        'dash': 'dash'
    }
    nifti_context.update_time_marker_plot_options(options)
    
    # Check that options were updated
    assert nifti_context._state.time_marker_plot_options.color == TimeCourseColor.RED
    assert nifti_context._state.time_marker_plot_options.width == 3
    assert nifti_context._state.time_marker_plot_options.dash == 'dash'

def test_update_view_state(nifti_context, gifti_context):
    """Test updating view state."""
    # Test changing to montage view
    nifti_context.update_view_state('montage')
    assert nifti_context._state.view_state == 'montage'
    
    # Test changing back to ortho view
    nifti_context.update_view_state('ortho')
    assert nifti_context._state.view_state == 'ortho'

    # For GIFTI data (there should no attribute view_state)
    assert not hasattr(gifti_context._state, 'view_state')
    

def test_ts_preprocessed_property(ts_context):
    """Test ts_preprocessed property."""
    # Set up preprocessed state
    ts_context._state.ts_preprocessed = {'ROI1': True, 'ROI2': False}
    
    # Check property
    assert ts_context.ts_preprocessed == {'ROI1': True, 'ROI2': False}

def test_get_time_course_labels(ts_context):
    """Test getting time course labels."""
    labels = ts_context.ts_labels
    assert labels is not None
    assert 'ROI1' in labels
    assert 'ROI2' in labels

def test_get_time_course_labels_preprocessed(ts_context):
    """Test getting preprocessed time course labels."""
    # Setup preprocessed data
    ts_context._state.ts_preprocessed = {'ROI1': True, 'ROI2': False}
    ts_context._state.ts_labels_preprocessed = ['ROI1']
    ts_context._state.ts_preprocessed_data = {
        'ROI1': np.array([1, 2, 3, 4, 5]),
        'ROI2': np.array([6, 7, 8, 9, 10])
    }
    # ts labels should remain the same
    labels = ts_context.ts_labels
    assert labels is not None
    assert 'ROI1' in labels
    assert 'ROI2' in labels

def test_get_task_conditions(task_context):
    """Test getting task conditions."""
    conditions = task_context.task_conditions
    assert conditions is not None
    assert 'cond1' in conditions
    assert 'cond2' in conditions

def test_get_time_points(nifti_context):
    """Test getting time points."""
    timepoints = nifti_context.get_timepoints()
    assert timepoints is not None
    assert len(timepoints) == nifti_context._state.nifti_data['func_img'].shape[3]

def test_get_time_point(nifti_context):
    """Test getting current time point."""
    # Set a specific timepoint
    nifti_context._state.timepoint = 2
    assert nifti_context.timepoint == 2

def test_get_crosshair_coords(nifti_context):
    """Test getting crosshair coordinates."""
    # Set up the state for ortho view
    nifti_context._state.file_type = 'nifti'
    nifti_context._state.view_state = 'ortho'
    nifti_context._state.slice_len = {'x': 10, 'y': 12, 'z': 14}
    nifti_context._state.ortho_slice_coords = {
        'slice_1': {'x': 5, 'y': 6},
        'slice_2': {'x': 7, 'y': 8},
        'slice_3': {'x': 9, 'y': 10}
    }
    
    # Get crosshair coordinates
    coords = nifti_context.get_crosshair_coords()
    
    # Check that the coordinates are correct
    assert coords is not None
    assert 'slice_1' in coords
    assert 'slice_2' in coords
    assert 'slice_3' in coords
    
    # Check slice_1 (sagittal view)
    assert coords['slice_1']['len_x'] == 11  # slice_len['y'] - 1
    assert coords['slice_1']['len_y'] == 13  # slice_len['z'] - 1
    assert coords['slice_1']['x'] == 5
    assert coords['slice_1']['y'] == 6
    
    # Check slice_2 (coronal view)
    assert coords['slice_2']['len_x'] == 9   # slice_len['x'] - 1
    assert coords['slice_2']['len_y'] == 13  # slice_len['z'] - 1
    assert coords['slice_2']['x'] == 7
    assert coords['slice_2']['y'] == 8
    
    # Check slice_3 (axial view)
    assert coords['slice_3']['len_x'] == 9   # slice_len['x'] - 1
    assert coords['slice_3']['len_y'] == 11  # slice_len['y'] - 1
    assert coords['slice_3']['x'] == 9
    assert coords['slice_3']['y'] == 10
    
    # Test montage view
    nifti_context._state.view_state = 'montage'
    nifti_context._state.montage_slice_dir = 'z'
    nifti_context._state.montage_slice_coords = {
        'z': {
            'slice_1': {'x': 1, 'y': 2},
            'slice_2': {'x': 3, 'y': 4},
            'slice_3': {'x': 5, 'y': 6}
        }
    }
    
    # Get crosshair coordinates for montage view
    coords = nifti_context.get_crosshair_coords()
    
    # Check that the coordinates are correct
    assert coords is not None
    assert 'slice_1' in coords
    assert 'slice_2' in coords
    assert 'slice_3' in coords
    
    # For z direction, len_x = slice_len['x'] - 1, len_y = slice_len['y'] - 1
    assert coords['slice_1']['len_x'] == 9
    assert coords['slice_1']['len_y'] == 11
    assert coords['slice_1']['x'] == 1
    assert coords['slice_1']['y'] == 2
    
    # Test with GIFTI data (should return empty dict)
    nifti_context._state.file_type = 'gifti'
    coords = nifti_context.get_crosshair_coords()
    assert coords == {}

def test_get_direction_label_coords(nifti_context):
    """Test getting direction label coordinates."""
    # Set slice lengths
    nifti_context._state.file_type = 'nifti'
    nifti_context._state.slice_len = {'x': 10, 'y': 12, 'z': 14}
    
    # Get direction label coordinates
    coords = nifti_context.get_direction_label_coords()
    
    # Check that coordinates are returned for each slice
    assert coords is not None
    assert 'slice_1' in coords  # Sagittal view
    assert 'slice_2' in coords  # Coronal view
    assert 'slice_3' in coords  # Axial view
    
    # Check slice_1 (sagittal) - should have A(nterior) and P(osterior) labels
    assert 'A' in coords['slice_1']
    assert 'P' in coords['slice_1']
    # A should be at the back of the y axis
    assert coords['slice_1']['A']['x'] == 12 - 2
    assert coords['slice_1']['A']['y'] == 14 // 2
    # P should be at the front of the y axis
    assert coords['slice_1']['P']['x'] == 1
    assert coords['slice_1']['P']['y'] == 14 // 2
    
    # Check slice_2 (coronal) - should have L(eft) and R(ight) labels
    assert 'L' in coords['slice_2']
    assert 'R' in coords['slice_2']
    # L should be at the left of the x axis
    assert coords['slice_2']['L']['x'] == 1
    assert coords['slice_2']['L']['y'] == 14 // 2
    # R should be at the right of the x axis
    assert coords['slice_2']['R']['x'] == 10 - 2
    assert coords['slice_2']['R']['y'] == 14 // 2
    
    # Check slice_3 (axial) - should have A, P, L, R labels
    assert 'A' in coords['slice_3']
    assert 'P' in coords['slice_3']
    assert 'L' in coords['slice_3']
    assert 'R' in coords['slice_3']
    # A should be at the top of the y axis
    assert coords['slice_3']['A']['x'] == 10 // 2
    assert coords['slice_3']['A']['y'] == 12 - 2
    # P should be at the bottom of the y axis
    assert coords['slice_3']['P']['x'] == 10 // 2
    assert coords['slice_3']['P']['y'] == 1
    # L should be at the left of the x axis
    assert coords['slice_3']['L']['x'] == 1
    assert coords['slice_3']['L']['y'] == 12 // 2
    # R should be at the right of the x axis
    assert coords['slice_3']['R']['x'] == 10 - 2
    assert coords['slice_3']['R']['y'] == 12 // 2
    
    # Test with GIFTI data (should return empty dict)
    nifti_context._state.file_type = 'gifti'
    coords = nifti_context.get_direction_label_coords()
    assert coords == {}

def test_get_world_coords(nifti_context):
    """Test getting world coordinates."""
    # Set up affine matrix
    nifti_context._state.func_affine = np.eye(4)
    nifti_context._state.ortho_slice_idx = {'x': 5, 'y': 6, 'z': 7}
    
    coords = nifti_context.get_world_coords()
    assert coords is not None
    assert len(coords) == 3  # x, y, z coordinates
    # With identity affine, world coords should match voxel coords
    assert coords[0] == 5
    assert coords[1] == 6
    assert coords[2] == 7

def test_get_viewer_metadata_nifti(nifti_context):
    """Test getting viewer metadata for NIFTI data."""
    metadata = nifti_context.get_viewer_metadata()
    assert metadata is not None
    assert metadata['file_type'] == 'nifti'
    assert 'anat_input' in metadata
    assert 'mask_input' in metadata
    assert 'slice_len' in metadata
    assert 'timepoints' in metadata

def test_get_viewer_metadata_gifti(gifti_context):
    """Test getting viewer metadata for GIFTI data."""
    metadata = gifti_context.get_viewer_metadata()
    assert metadata is not None
    assert metadata['file_type'] == 'gifti'
    assert 'left_input' in metadata
    assert 'right_input' in metadata
    assert 'timepoints' in metadata

def test_get_viewer_data_nifti(nifti_context):
    """Test getting viewer data for NIFTI data."""
    data = nifti_context.get_viewer_data(
        time_course_data=False,
        task_data=False,
        coord_labels=False
    )
    assert data is not None
    assert 'func_img' in data
    assert 'anat_img' in data
    assert 'mask_img' in data
    # no ts_data in nifti data
    assert 'ts' not in data
    # no task_data in nifti data
    assert 'task' not in data

def test_get_viewer_data_gifti(gifti_context):
    """Test getting viewer data for GIFTI data."""
    data = gifti_context.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
        coord_labels=False
    )
    assert data is not None
    assert 'left_func_img' in data
    assert 'right_func_img' in data
    # no ts_data in gifti data
    assert 'ts' not in data
    # no task_data in gifti data
    assert 'task' not in data

def test_get_viewer_data_timecourse(ts_context):
    """Test getting viewer data for timecourse."""
    data = ts_context.get_viewer_data(
        fmri_data=False,
        time_course_data=True,
        task_data=False,
        coord_labels=False
    )
    assert data is not None
    assert 'ts' in data
    assert 'ROI1' in data['ts']
    assert 'ROI2' in data['ts']
    assert np.array_equal(data['ts']['ROI1'], ts_context._state.ts_data['ROI1'])
    assert np.array_equal(data['ts']['ROI2'], ts_context._state.ts_data['ROI2'])

    # no func_data in timecourse data
    assert 'func_data' not in data

def test_get_viewer_data_task(task_context):
    """Test getting viewer data for task."""
    data = task_context.get_viewer_data(
        fmri_data=False,
        time_course_data=False,
        task_data=True,
        coord_labels=False
    )
    assert data is not None
    assert 'task' in data
    assert 'cond1' in data['task']
    # default convolution is hrf
    assert np.array_equal(data['task']['cond1'], task_context._state.task_data['cond1']['hrf'])
    # no ts_data in task data
    assert 'ts' not in data
    # no func_data in task data
    assert 'func_img' not in data

def test_get_viewer_data_coord_labels(nifti_context):
    """Test getting viewer data for coordinate labels."""
    # set coord_labels
    nifti_context._state.coord_labels = [
        (1, 2, 3), (4, 5, 6), (7, 8, 9)
    ]
    data = nifti_context.get_viewer_data(
        fmri_data=True,
        time_course_data=False,
        task_data=False,
        coord_labels=True
    )

    assert data is not None
    assert 'coord_labels' in data
    assert np.array_equal(data['coord_labels'], nifti_context._state.coord_labels)


def test_reset_fmri_color_options(nifti_context):
    """Test resetting fMRI color options."""
    # Set up original color options
    nifti_context._state.color_options_original = {
        'color_min': -1.0,
        'color_max': 1.0,
        'threshold_min': -0.5,
        'threshold_max': 0.5,
        'opacity': 0.5
    }
    
    # Change current color options
    nifti_context._state.fmri_plot_options.color_min = -2.0
    nifti_context._state.fmri_plot_options.color_max = 2.0
    nifti_context._state.fmri_plot_options.threshold_min = -1.0
    nifti_context._state.fmri_plot_options.threshold_max = 1.0
    nifti_context._state.fmri_plot_options.opacity = 0.7
    
    # Reset color options
    nifti_context.reset_fmri_color_options()
    
    # Check that options were reset to original
    assert nifti_context._state.fmri_plot_options.color_min == -1.0
    assert nifti_context._state.fmri_plot_options.color_max == 1.0
    assert nifti_context._state.fmri_plot_options.threshold_min == -0.5
    assert nifti_context._state.fmri_plot_options.threshold_max == 0.5
    assert nifti_context._state.fmri_plot_options.opacity == 0.5

def test_reset_timecourse_shift(ts_context):
    """Test resetting time course shift."""
    # Set up time course with shift
    ts_context._state.ts_plot_options['ROI1'].constant.shift_history = [1.0, 2.0]
    ts_context._state.ts_plot_options['ROI1'].scale.scale_history = [1.5, 0.8]
    
    # Reset constant shift
    ts_context.reset_timecourse_shift('ROI1', 'constant', 'timecourse')
    
    # Check that shift was reset
    assert len(ts_context._state.ts_plot_options['ROI1'].constant.shift_history) == 0

    # Reset scale
    ts_context.reset_timecourse_shift('ROI1', 'scale', 'timecourse')
    assert len(ts_context._state.ts_plot_options['ROI1'].scale.scale_history) == 0

def test_set_timepoints(nifti_context):
    """Test setting timepoints."""
    # Set timepoints
    timepoints = [0, 1, 2, 3, 4]
    nifti_context.set_timepoints(timepoints)
    
    # Check that timepoints were set
    assert nifti_context._state.timepoints == timepoints

def test_set_tr(nifti_context):
    """Test setting TR."""
    # Set TR
    nifti_context.set_tr(2.0)
    
    # Check that TR was set
    assert nifti_context.get_viewer_metadata()['tr'] == 2.0

def test_store_fmri_preprocessed_nifti(nifti_context, mock_nifti_4d):
    """Test storing preprocessed fMRI data for NIFTI."""
    # Create preprocessed data
    preprocessed_data = {
        'func_img': mock_nifti_4d
    }
    
    # Store preprocessed data
    nifti_context.store_fmri_preprocessed(preprocessed_data)
    
    # Check that data was stored
    assert nifti_context._state.fmri_preprocessed is True
    assert 'func_img' in nifti_context._state.nifti_data_preprocessed

def test_store_fmri_preprocessed_gifti(gifti_context, mock_gifti_func):
    """Test storing preprocessed fMRI data for GIFTI."""
    # Create preprocessed data
    preprocessed_data = {
        'left_func_img': mock_gifti_func,
        'right_func_img': mock_gifti_func
    }
    
    # Store preprocessed data
    gifti_context.store_fmri_preprocessed(preprocessed_data)
    
    # Check that data was stored
    assert gifti_context._state.fmri_preprocessed is True
    assert 'left_func_img' in gifti_context._state.gifti_data_preprocessed
    assert 'right_func_img' in gifti_context._state.gifti_data_preprocessed

def test_store_timecourse_preprocessed(ts_context):
    """Test storing preprocessed timecourse data."""
    # Create preprocessed data
    preprocessed_data = {
        'ROI1': np.array([2.0, 3.0, 4.0, 5.0, 6.0]),
        'ROI2': np.array([6.0, 5.0, 4.0, 3.0, 2.0])
    }
    
    # Store preprocessed data
    ts_context.store_timecourse_preprocessed(preprocessed_data)
    
    # Check that data was stored
    assert ts_context._state.ts_preprocessed['ROI1'] is True
    assert ts_context._state.ts_preprocessed['ROI2'] is True
    assert np.array_equal(ts_context._state.ts_data_preprocessed['ROI1'], preprocessed_data['ROI1'])
    assert np.array_equal(ts_context._state.ts_data_preprocessed['ROI2'], preprocessed_data['ROI2'])
    assert 'ROI1' in ts_context._state.ts_labels_preprocessed
    assert 'ROI2' in ts_context._state.ts_labels_preprocessed

def test_update_annotation_marker_plot_options(nifti_context):
    """Test updating annotation marker plot options."""
    # Update annotation marker plot options
    options = {
        'color': TimeCourseColor.RED,
        'width': 3,
        'opacity': 0.7
    }
    nifti_context.update_annotation_marker_plot_options(options)
    
    # Check that options were updated
    assert nifti_context._state.annotation_marker_plot_options.color == TimeCourseColor.RED
    assert nifti_context._state.annotation_marker_plot_options.width == 3
    assert nifti_context._state.annotation_marker_plot_options.opacity == 0.7

def test_update_distance_plot_options(nifti_context):
    """Test updating distance plot options."""
    # Create distance plot first
    distance_data = np.array([1, 2, 3], dtype=np.float64)
    nifti_context.create_distance_plot_state(distance_data)
    
    # Update distance plot options
    options = {
        'color_min': -2.0,
        'color_max': 2.0,
        'color_map': ColorMaps.JET
    }
    nifti_context.update_distance_plot_options(options)
    
    # Check that options were updated
    assert nifti_context._state.distance_plot_options.color_min == -2.0
    assert nifti_context._state.distance_plot_options.color_max == 2.0
    assert nifti_context._state.distance_plot_options.color_map == ColorMaps.JET

def test_update_timecourse_shift(ts_context):
    """Test updating time course shift."""
    # set time course shift unit
    ts_context._state.time_course_global_plot_options.shift_unit = 1.0
    ts_context._state.ts_plot_options['ROI1'].constant.shift_unit = 0.1
    # Update time course shift
    ts_context.update_timecourse_shift('ROI1', 'timecourse', 'constant', 'increase')
    
    # Check that shift was updated
    assert ts_context._state.ts_plot_options['ROI1'].constant.shift_history[-1] == 1.0
    
    # Update time course scale
    ts_context.update_timecourse_shift('ROI1', 'timecourse', 'scale', 'increase')
    
    # Check that scale was updated (scale shift starts at 1)
    assert ts_context._state.ts_plot_options['ROI1'].scale.scale_history[-1] == 1.1

def test_move_annotation_selection(nifti_context):
    """Test moving annotation selection."""
    # Add some markers first
    nifti_context.add_annotation_markers([3, 5, 7, 9])
    assert nifti_context._state.annotation_selection == 9
    
    # Move selection to previous marker
    nifti_context.move_annotation_selection('left')
    assert nifti_context._state.annotation_selection == 7
    
    # Move selection to next marker
    nifti_context.move_annotation_selection('right')
    assert nifti_context._state.annotation_selection == 9
    
    # Test wrapping around at the ends
    nifti_context._state.annotation_selection = 3  # First marker
    nifti_context.move_annotation_selection('left')
    assert nifti_context._state.annotation_selection == 9  # Should wrap to last
    
    nifti_context._state.annotation_selection = 9  # Last marker
    nifti_context.move_annotation_selection('right')
    assert nifti_context._state.annotation_selection == 3  # Should wrap to first

def test_pop_annotation_marker(nifti_context):
    """Test popping annotation markers."""
    # Add some markers first
    nifti_context.add_annotation_markers([3, 5, 7, 9])
    
    # Pop the most recent marker
    popped = nifti_context.pop_annotation_marker()
    assert popped == 9
    assert nifti_context._state.annotation_markers == [3, 5, 7]
    assert nifti_context._state.annotation_selection == 7  # Selection should move to previous
    
    # Pop another marker
    popped = nifti_context.pop_annotation_marker()
    assert popped == 7
    assert nifti_context._state.annotation_markers == [3, 5]
    assert nifti_context._state.annotation_selection == 5
    
    # Pop another marker 
    popped = nifti_context.pop_annotation_marker()
    assert popped == 5
    assert nifti_context._state.annotation_markers == [3]
    assert nifti_context._state.annotation_selection == 3
    
    # Pop last marker
    popped = nifti_context.pop_annotation_marker()
    assert popped == 3
    assert nifti_context._state.annotation_markers == []
    # annotation selection should equal the last marker that was added
    assert nifti_context._state.annotation_selection is None

    # Pop when no markers remain
    popped = nifti_context.pop_annotation_marker()
    assert popped is None
    assert nifti_context._state.annotation_markers == []
    assert nifti_context._state.annotation_selection is None

def test_get_click_coords(nifti_context):
    """Test getting click coordinates."""
    # Set up the state
    nifti_context._state.file_type = 'nifti'
    nifti_context._state.view_state = 'ortho'
    nifti_context._state.ortho_slice_coords = {
        'slice_1': {'x': 3, 'y': 4},
        'slice_2': {'x': 5, 'y': 6},
        'slice_3': {'x': 7, 'y': 8}
    }
    nifti_context._state.montage_slice_coords = {
        'x': {
            'slice_1': {'x': 3, 'y': 4},
            'slice_2': {'x': 5, 'y': 6},
            'slice_3': {'x': 7, 'y': 8}
        },
        'y': {
            'slice_1': {'x': 3, 'y': 4},
            'slice_2': {'x': 5, 'y': 6},
            'slice_3': {'x': 7, 'y': 8}
        },
        'z': {
            'slice_1': {'x': 3, 'y': 4},
            'slice_2': {'x': 5, 'y': 6},
            'slice_3': {'x': 7, 'y': 8}
        }
    }
    
    coords = nifti_context.get_click_coords()
    assert coords is not None
    assert 'slice_1' in coords
    assert 'slice_2' in coords
    assert 'slice_3' in coords
    assert coords['slice_1'] == {'x': 3, 'y': 4}
    assert coords['slice_2'] == {'x': 5, 'y': 6}
    assert coords['slice_3'] == {'x': 7, 'y': 8}
    
    # Test with montage view
    nifti_context._state.view_state = 'montage'
    nifti_context._state.montage_slice_dir = 'z'
    
    coords = nifti_context.get_click_coords()
    assert coords is not None
    assert 'slice_1' in coords
    assert 'slice_2' in coords
    assert 'slice_3' in coords
    assert coords['slice_1'] == {'x': 3, 'y': 4}
    assert coords['slice_2'] == {'x': 5, 'y': 6}
    assert coords['slice_3'] == {'x': 7, 'y': 8}

def test_update_annotation_selection(nifti_context):
    """Test updating annotation selection."""
    # Add some markers first
    nifti_context.add_annotation_markers([3, 5, 7, 9])
    
    # Update selection (position should be 1)
    nifti_context.update_annotation_selection(5)
    assert nifti_context._state.annotation_selection == 1
    
    # Test with invalid selection (not in markers)
    nifti_context.update_annotation_selection(10)
    # Should not change selection
    assert nifti_context._state.annotation_selection == 1


    
