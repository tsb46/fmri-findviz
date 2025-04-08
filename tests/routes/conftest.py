import pytest
from flask import Flask, make_response
import json
import copy
from unittest.mock import patch, MagicMock
import numpy as np
from functools import wraps

from findviz import create_app
from findviz.routes.shared import data_manager
from findviz.viz.viewer.data_manager import DataManager
from findviz.viz.viewer.context import VisualizationContext


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(testing=True, clear_cache=True)
    
    # Create a testing context for our app
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def reset_data_manager():
    """Reset the DataManager singleton between tests."""
    # Store original instance
    original_instance = DataManager._instance
    
    # Create a clean instance for testing
    DataManager._instance = None
    test_instance = DataManager()
    
    yield test_instance
    
    # Restore original instance after test
    DataManager._instance = original_instance


@pytest.fixture
def mock_data_manager_ctx():
    """Create a mock VisualizationContext that can be used for testing."""
    mock_ctx = MagicMock(spec=VisualizationContext)
    
    # Setup common attributes and methods that tests might need
    mock_ctx.context_id = "test_context"
    mock_ctx.file_type = "nifti"
    mock_ctx.anat_input = False
    mock_ctx.mask_input = False
    mock_ctx.fmri_preprocessed = False
    mock_ctx.ts_preprocessed = True
    mock_ctx.global_min = 0.0
    mock_ctx.global_max = 1.0
    mock_ctx.fmri_file_type = "nifti"
    mock_ctx.timepoint = 0
    mock_ctx.timepoints = [0, 1, 2, 3, 4]
    mock_ctx.tr = 2.0
    mock_ctx.view_state = "ortho"
    mock_ctx.montage_slice_dir = "x"
    mock_ctx.montage_slice_idx = {
        "x": {
            "slice_1": {"x": 0, "y": 0, "z": 0},
            "slice_2": {"x": 0, "y": 0, "z": 0},
            "slice_3": {"x": 0, "y": 0, "z": 0}
        },
        "y": {
            "slice_1": {"x": 0, "y": 0, "z": 0},
            "slice_2": {"x": 0, "y": 0, "z": 0},
            "slice_3": {"x": 0, "y": 0, "z": 0}
        },
        "z": {
            "slice_1": {"x": 0, "y": 0, "z": 0},
            "slice_2": {"x": 0, "y": 0, "z": 0},
            "slice_3": {"x": 0, "y": 0, "z": 0}
        }
    }
    mock_ctx.slice_len = {"x": 10, "y": 10, "z": 10}
    mock_ctx.color_options_original = {
        "threshold_min": 0.0,
        "threshold_max": 1.0
    }
    mock_ctx.coord_labels = ["x", "y", "z"]
    mock_ctx.selected_vertex = 0
    mock_ctx.selected_hemi = "left"
    mock_ctx.selected_slice = "slice_1"
    mock_ctx.click_coords = {"x": 5, "y": 5}
    mock_ctx.task_conditions = ["rest", "task"]
    mock_ctx.ts_labels = ["voxel_1", "voxel_2"]
    mock_ctx.ts_labels_preprocessed = ["voxel_1_preprocessed"]
    mock_ctx.timecourse_source = {
        "voxel_1": "timecourse", 
        "voxel_2": "timecourse",
        "rest": "task",
        "task": "task"
    }
    mock_ctx.annotation_markers = [10, 20, 30]
    mock_ctx.annotation_selection = 0
    mock_ctx.annotation_marker_plot_options = MagicMock()
    mock_ctx.annotation_marker_plot_options.to_dict.return_value = {"show": True}

    # Mock context methods
    def mock_set_tr(tr_value):
        mock_ctx.tr = tr_value
        return None
    mock_ctx.set_tr.side_effect = mock_set_tr

    def mock_update_timepoint(timepoint):
        mock_ctx.timepoint = timepoint
        return None
    mock_ctx.update_timepoint.side_effect = mock_update_timepoint

    def mock_convert_timepoints():
        mock_ctx.timepoints = [0.5, 1.5, 2.5, 3.5, 4.5]
        return None
    mock_ctx.convert_timepoints.side_effect = mock_convert_timepoints

    def mock_update_location(click_coords, slice_name):
        if mock_ctx.file_type == "nifti":
            mock_ctx.click_coords = click_coords
            mock_ctx.selected_slice = slice_name
        elif mock_ctx.file_type == "gifti":
            mock_ctx.selected_vertex = click_coords["selected_vertex"]
            mock_ctx.selected_hemi = click_coords["selected_hemi"]
        return None
    mock_ctx.update_location.side_effect = mock_update_location

    def mock_update_montage_slice_idx(slice_name, slice_idx):
        # Get the current montage slice direction
        montage_slice_dir = mock_ctx.montage_slice_dir
        # Update the specific index value while preserving structure
        mock_ctx.montage_slice_idx[montage_slice_dir][slice_name]["x"] = slice_idx
        return None

    mock_ctx.update_montage_slice_idx.side_effect = mock_update_montage_slice_idx

    # Mock the pop_annotation_marker method to actually remove the last marker
    def mock_pop_annotation_marker():
        if mock_ctx.annotation_markers:
            mock_ctx.annotation_markers.pop()
        return None
        
    mock_ctx.pop_annotation_marker.side_effect = mock_pop_annotation_marker
    
    # Instead of trying to patch the property itself, patch what the property returns
    # by patching where the DataManager is looking for the active context
    with patch.object(data_manager, '_active_context_id', "main"):
        with patch.dict(data_manager._contexts, {"main": mock_ctx}):
            yield mock_ctx
    
    return mock_ctx


@pytest.fixture
def json_content_type():
    """Return JSON content type header."""
    return {"Content-Type": "application/json"}


@pytest.fixture
def form_content_type():
    """Return form content type header."""
    return {"Content-Type": "application/x-www-form-urlencoded"}