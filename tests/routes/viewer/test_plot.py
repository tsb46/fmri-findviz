import pytest
import json
from unittest.mock import patch, MagicMock

from findviz.routes.utils import Routes


@pytest.mark.usefixtures("mock_data_manager_ctx")
class TestPlotRoutes:
    """Test class for the plot.py routes."""
    
    def test_add_annotation_marker(self, client, mock_data_manager_ctx, form_content_type):
        """Test ADD_ANNOTATION_MARKER route."""
        # Setup
        marker = 15
        
        # Make the request with context_id
        response = client.post(
            Routes.ADD_ANNOTATION_MARKER.value,
            data={"marker": str(marker), "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"marker": marker}
        mock_data_manager_ctx.add_annotation_markers.assert_called_once_with(marker)
    
    def test_change_task_convolution(self, client, mock_data_manager_ctx, form_content_type):
        """Test CHANGE_TASK_CONVOLUTION route."""
        # Setup
        convolution = True
        mock_data_manager_ctx.task_conditions = ["rest", "task_1", "task_2"]
        mock_data_manager_ctx.task_plot_options = {
            "rest": MagicMock(),
            "task_1": MagicMock(),
            "task_2": MagicMock()
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.CHANGE_TASK_CONVOLUTION.value,
            data={"convolution": str(convolution), "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_timecourse_global_plot_options.assert_called_once_with(
            {"global_convolution": convolution}
        )
        
        # Check that update_task_design_plot_options was called for each task condition
        assert mock_data_manager_ctx.update_task_design_plot_options.call_count == len(mock_data_manager_ctx.task_conditions)
        
        # Check that it was called with the correct arguments for each label
        for label in mock_data_manager_ctx.task_conditions:
            mock_data_manager_ctx.update_task_design_plot_options.assert_any_call(
                label, {"convolution": "hrf"}
            )
    
    def test_check_fmri_preprocessed(self, client, mock_data_manager_ctx, form_content_type):
        """Test CHECK_FMRI_PREPROCESSED route."""
        # Setup
        mock_data_manager_ctx.fmri_preprocessed = False
        
        # Make the request with context_id
        response = client.post(
            Routes.CHECK_FMRI_PREPROCESSED.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"is_preprocessed": False}
    
    def test_check_ts_preprocessed(self, client, mock_data_manager_ctx, form_content_type):
        """Test CHECK_TS_PREPROCESSED route for timecourse data."""
        # Setup for timecourse data
        mock_data_manager_ctx.check_ts_preprocessed.return_value = True
        
        # Make the request with context_id
        response = client.post(
            Routes.CHECK_TS_PREPROCESSED.value,
            data={"label": "voxel_1", "ts_type": "timecourse", "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"is_preprocessed": True}
        mock_data_manager_ctx.check_ts_preprocessed.assert_called_once_with("voxel_1")
    
    def test_check_ts_preprocessed_task(self, client, mock_data_manager_ctx, form_content_type):
        """Test CHECK_TS_PREPROCESSED route for task data."""
        # Setup for task data
        
        # Make the request with context_id
        response = client.post(
            Routes.CHECK_TS_PREPROCESSED.value,
            data={"label": "rest", "ts_type": "task", "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response - task data is never preprocessed
        assert response.status_code == 200
        assert json.loads(response.data) == {"is_preprocessed": False}
    
    def test_clear_annotation_markers(self, client, mock_data_manager_ctx, form_content_type):
        """Test CLEAR_ANNOTATION_MARKERS route."""
        # Make the request with context_id
        response = client.post(
            Routes.CLEAR_ANNOTATION_MARKERS.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.clear_annotation_markers.assert_called_once()
    
    def test_get_annotation_markers(self, client, mock_data_manager_ctx):
        """Test GET_ANNOTATION_MARKERS route."""
        # Setup
        mock_data_manager_ctx.annotation_markers = [10, 20, 30]
        mock_data_manager_ctx.annotation_selection = 0
        
        # Make the request with context_id
        response = client.get(Routes.GET_ANNOTATION_MARKERS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["markers"] == [10, 20, 30]
        assert result["selection"] == 0
        assert result["plot_options"] == {"show": True}
    
    def test_get_annotation_marker_plot_options(self, client, mock_data_manager_ctx):
        """Test GET_ANNOTATION_MARKER_PLOT_OPTIONS route."""
        # Setup
        mock_data_manager_ctx.get_annotation_marker_plot_options.return_value = {"show": True, "color": "red"}
        
        # Make the request with context_id
        response = client.get(Routes.GET_ANNOTATION_MARKER_PLOT_OPTIONS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"show": True, "color": "red"}
        mock_data_manager_ctx.get_annotation_marker_plot_options.assert_called_once()
    
    def test_get_distance_plot_options(self, client, mock_data_manager_ctx):
        """Test GET_DISTANCE_PLOT_OPTIONS route."""
        # Setup
        mock_data_manager_ctx.get_distance_plot_options.return_value = {"show": True, "color": "blue"}
        
        # Make the request with context_id
        response = client.get(Routes.GET_DISTANCE_PLOT_OPTIONS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"show": True, "color": "blue"}
        mock_data_manager_ctx.get_distance_plot_options.assert_called_once()
    
    def test_get_fmri_plot_options(self, client, mock_data_manager_ctx):
        """Test GET_FMRI_PLOT_OPTIONS route."""
        # Setup
        mock_data_manager_ctx.get_fmri_plot_options.return_value = {
            "threshold_min": 0.1,
            "threshold_max": 0.9,
            "colormap": "viridis"
        }
        
        # Make the request with context_id
        response = client.get(Routes.GET_FMRI_PLOT_OPTIONS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "threshold_min": 0.1,
            "threshold_max": 0.9,
            "colormap": "viridis"
        }
        mock_data_manager_ctx.get_fmri_plot_options.assert_called_once()
    
    def test_get_nifti_view_state(self, client, mock_data_manager_ctx):
        """Test GET_NIFTI_VIEW_STATE route."""
        # Setup
        mock_data_manager_ctx.view_state = "ortho"
        
        # Make the request with context_id
        response = client.get(Routes.GET_NIFTI_VIEW_STATE.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"view_state": "ortho"}
    
    def test_get_task_design_plot_options(self, client, mock_data_manager_ctx):
        """Test GET_TASK_DESIGN_PLOT_OPTIONS route."""
        # Setup
        mock_data_manager_ctx.get_task_design_plot_options.return_value = {
            "convolution": "hrf",
            "color": "green"
        }
        
        # Make the request with context_id
        response = client.get(Routes.GET_TASK_DESIGN_PLOT_OPTIONS.value + "?label=rest&context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "convolution": "hrf",
            "color": "green"
        }
        mock_data_manager_ctx.get_task_design_plot_options.assert_called_once_with("rest")
    
    def test_get_timecourse_global_plot_options(self, client, mock_data_manager_ctx):
        """Test GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS route."""
        # Setup
        mock_data_manager_ctx.get_timecourse_global_plot_options.return_value = {
            "global_convolution": True,
            "global_normalization": False
        }
        
        # Make the request with context_id
        response = client.get(Routes.GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "global_convolution": True,
            "global_normalization": False
        }
        mock_data_manager_ctx.get_timecourse_global_plot_options.assert_called_once()
    
    def test_get_timecourse_plot_options(self, client, mock_data_manager_ctx):
        """Test GET_TIMECOURSE_PLOT_OPTIONS route."""
        # Setup
        mock_data_manager_ctx.get_timecourse_plot_options.return_value = {
            "color": "red",
            "linewidth": 2,
            "visible": True
        }
        
        # Make the request with context_id
        response = client.get(Routes.GET_TIMECOURSE_PLOT_OPTIONS.value + "?label=voxel_1&context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "color": "red",
            "linewidth": 2,
            "visible": True
        }
        mock_data_manager_ctx.get_timecourse_plot_options.assert_called_once_with("voxel_1")
    
    def test_get_timecourse_shift_history(self, client, mock_data_manager_ctx):
        """Test GET_TIMECOURSE_SHIFT_HISTORY route."""
        # Setup
        mock_data_manager_ctx.get_timecourse_shift_history.return_value = {
            "scale": [1.0, 1.5, 2.0],
            "constant": [0, 0.5, 1.0]
        }
        
        # Make the request with context_id
        response = client.get(
            Routes.GET_TIMECOURSE_SHIFT_HISTORY.value + "?label=voxel_1&source=timecourse&context_id=main"
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "scale": [1.0, 1.5, 2.0],
            "constant": [0, 0.5, 1.0]
        }
        mock_data_manager_ctx.get_timecourse_shift_history.assert_called_once_with("voxel_1", "timecourse")
    
    def test_get_timemarker_plot_options(self, client, mock_data_manager_ctx):
        """Test GET_TIMEMARKER_PLOT_OPTIONS route."""
        # Setup
        mock_data_manager_ctx.get_time_marker_plot_options.return_value = {
            "color": "blue",
            "width": 1,
            "show": True
        }
        
        # Make the request with context_id
        response = client.get(Routes.GET_TIMEMARKER_PLOT_OPTIONS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "color": "blue",
            "width": 1,
            "show": True
        }
        mock_data_manager_ctx.get_time_marker_plot_options.assert_called_once()
    
    def test_get_ts_fmri_plotted(self, client, mock_data_manager_ctx):
        """Test GET_TS_FMRI_PLOTTED route."""
        # Setup
        mock_data_manager_ctx.ts_fmri_plotted = True
        
        # Make the request with context_id
        response = client.get(Routes.GET_TS_FMRI_PLOTTED.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"ts_fmri_plotted": True}
    
    def test_move_annotation_selection(self, client, mock_data_manager_ctx, form_content_type):
        """Test MOVE_ANNOTATION_SELECTION route."""
        # Setup
        mock_data_manager_ctx.move_annotation_selection.return_value = 1
        
        # Make the request with context_id
        response = client.post(
            Routes.MOVE_ANNOTATION_SELECTION.value,
            data={"direction": "next", "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"selected_marker": 1}
        mock_data_manager_ctx.move_annotation_selection.assert_called_once_with("next")
    
    def test_remove_distance_plot(self, client, mock_data_manager_ctx, form_content_type):
        """Test REMOVE_DISTANCE_PLOT route."""
        # Make the request with context_id
        response = client.post(
            Routes.REMOVE_DISTANCE_PLOT.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.clear_distance_plot_state.assert_called_once()
    
    def test_reset_fmri_color_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test RESET_FMRI_COLOR_OPTIONS route."""
        # Make the request with context_id
        response = client.post(
            Routes.RESET_FMRI_COLOR_OPTIONS.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.reset_fmri_color_options.assert_called_once()
    
    def test_reset_timecourse_shift(self, client, mock_data_manager_ctx, form_content_type):
        """Test RESET_TIMECOURSE_SHIFT route."""
        # Make the request with context_id
        response = client.post(
            Routes.RESET_TIMECOURSE_SHIFT.value,
            data={
                "label": "voxel_1", 
                "change_type": "scale", 
                "source": "timecourse", 
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.reset_timecourse_shift.assert_called_once_with(
            "voxel_1", "scale", "timecourse"
        )
    
    def test_undo_annotation_marker(self, client, mock_data_manager_ctx, form_content_type):
        """Test UNDO_ANNOTATION_MARKER route."""
        # Setup
        # Set up initial markers
        mock_data_manager_ctx.annotation_markers = [10, 20, 30]
        mock_data_manager_ctx.annotation_selection = 2
        # Make the request with context_id
        response = client.post(
            Routes.UNDO_ANNOTATION_MARKER.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"marker": 20}  # Returns the most recent marker after popping
        mock_data_manager_ctx.pop_annotation_marker.assert_called_once()
    
    def test_update_distance_plot_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_DISTANCE_PLOT_OPTIONS route."""
        # Setup
        distance_plot_options = {
            "show": True,
            "color": "red",
            "line_style": "solid"
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_DISTANCE_PLOT_OPTIONS.value,
            data={
                "distance_plot_options": json.dumps(distance_plot_options),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_distance_plot_options.assert_called_once_with(distance_plot_options)
    
    def test_update_fmri_plot_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_FMRI_PLOT_OPTIONS route."""
        # Setup
        fmri_plot_options = {
            "threshold_min": 0.2,
            "threshold_max": 0.8,
            "colormap": "hot"
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_FMRI_PLOT_OPTIONS.value,
            data={
                "fmri_plot_options": json.dumps(fmri_plot_options),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_fmri_plot_options.assert_called_once_with(fmri_plot_options)
    
    def test_update_annotation_marker_plot_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_ANNOTATION_MARKER_PLOT_OPTIONS route."""
        # Setup
        annotation_marker_plot_options = {
            "show": True,
            "color": "green",
            "style": "dashed"
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_ANNOTATION_MARKER_PLOT_OPTIONS.value,
            data={
                "annotation_marker_plot_options": json.dumps(annotation_marker_plot_options),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_annotation_marker_plot_options.assert_called_once_with(
            annotation_marker_plot_options
        )
    
    def test_update_nifti_view_state(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_NIFTI_VIEW_STATE route."""
        # Setup
        old_view_state = mock_data_manager_ctx.view_state
        new_view_state = "montage"
        
        # Set up mock behavior
        def mock_update_view_state(view_state):
            mock_data_manager_ctx.view_state = view_state
            return None
        mock_data_manager_ctx.update_view_state.side_effect = mock_update_view_state
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_NIFTI_VIEW_STATE.value,
            data={"view_state": new_view_state, "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_view_state.assert_called_once_with(new_view_state)
        # Check that view_state was updated
        assert mock_data_manager_ctx.view_state == new_view_state
        # Check that view_state was not reset to old value
        assert mock_data_manager_ctx.view_state != old_view_state
    
    def test_update_task_design_plot_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_TASK_DESIGN_PLOT_OPTIONS route."""
        # Setup
        task_design_plot_options = {
            "convolution": "hrf",
            "color": "blue",
            "line_style": "solid"
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_TASK_DESIGN_PLOT_OPTIONS.value,
            data={
                "label": "rest",
                "task_design_plot_options": json.dumps(task_design_plot_options),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_task_design_plot_options.assert_called_once_with(
            "rest", task_design_plot_options
        )
    
    def test_update_timecourse_global_plot_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS route."""
        # Setup
        timecourse_global_plot_options = {
            "global_convolution": True,
            "global_normalization": False
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS.value,
            data={
                "timecourse_global_plot_options": json.dumps(timecourse_global_plot_options),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_timecourse_global_plot_options.assert_called_once_with(
            timecourse_global_plot_options
        )
    
    def test_update_timecourse_plot_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_TIMECOURSE_PLOT_OPTIONS route."""
        # Setup
        timecourse_plot_options = {
            "color": "purple",
            "linewidth": "2",
            "visible": True
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_TIMECOURSE_PLOT_OPTIONS.value,
            data={
                "label": "voxel_1",
                "timecourse_plot_options": json.dumps(timecourse_plot_options),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        timecourse_plot_options["linewidth"] = 2
        mock_data_manager_ctx.update_timecourse_plot_options.assert_called_once_with(
            "voxel_1", timecourse_plot_options
        )
    
    def test_update_timecourse_shift(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_TIMECOURSE_SHIFT route."""
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_TIMECOURSE_SHIFT.value,
            data={
                "label": "voxel_1", 
                "source": "timecourse", 
                "change_type": "scale", 
                "change_direction": "increase",
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_timecourse_shift.assert_called_once_with(
            "voxel_1", "timecourse", "scale", "increase"
        )
    
    def test_update_timemarker_plot_options(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_TIMEMARKER_PLOT_OPTIONS route."""
        # Setup
        timemarker_plot_options = {
            "color": "red",
            "width": 2,
            "show": True
        }
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_TIMEMARKER_PLOT_OPTIONS.value,
            data={
                "timemarker_plot_options": json.dumps(timemarker_plot_options),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_time_marker_plot_options.assert_called_once_with(
            timemarker_plot_options
        )
