# tests/routes/viewer/test_data.py
import pytest
import json
import numpy as np
from unittest.mock import patch, MagicMock

from findviz.routes.utils import Routes


@pytest.mark.usefixtures("mock_data_manager_ctx")
class TestDataRoutes:
    """Test class for the data.py routes."""
    
    def test_convert_timepoints(self, client, mock_data_manager_ctx):
        """Test CONVERT_TIMEPOINTS route."""
        old_timepoints = mock_data_manager_ctx.timepoints
        new_timepoints = [0.5, 1.5, 2.5, 3.5, 4.5]

        # Setup
        mock_data_manager_ctx.convert_timepoints.return_value = {"status": "success"}
        
        # Make the request with context_id
        response = client.post(
            Routes.CONVERT_TIMEPOINTS.value + "?context_id=main"
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.convert_timepoints.assert_called_once_with()
        # Check that the timepoints were updated
        assert mock_data_manager_ctx.timepoints == new_timepoints
        # Check that the timepoints were not reset to the old value
        assert mock_data_manager_ctx.timepoints != old_timepoints
    
    def test_get_click_coords(self, client, mock_data_manager_ctx):
        """Test GET_CLICK_COORDS route."""
        # Setup the expected return value
        expected_data = {"selected_vertex": 0, "selected_hemi": "left"}
        mock_data_manager_ctx.get_click_coords.return_value = expected_data

        # Make the request with context_id
        response = client.get(Routes.GET_CLICK_COORDS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == expected_data
        mock_data_manager_ctx.get_click_coords.assert_called_once()
    
    def test_get_coord_labels_nifti(self, client, mock_data_manager_ctx):
        """Test GET_COORD_LABELS route with nifti file type."""
        # Setup for nifti file type
        mock_data_manager_ctx.fmri_file_type = "nifti"
        mock_data_manager_ctx.coord_labels = ["x", "y", "z"]
        
        # Make the request with context_id
        response = client.get(Routes.GET_COORD_LABELS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == ["x", "y", "z"]

    def test_get_coord_labels_gifti(self, client, mock_data_manager_ctx):
        """Test GET_COORD_LABELS route with gifti file type."""
        # Setup for gifti file type
        mock_data_manager_ctx.fmri_file_type = "gifti"
        mock_data_manager_ctx.coord_labels = [["left_x", "left_y", "left_z"], ["right_x", "right_y", "right_z"]]
        
        # Make the request with context_id
        response = client.get(Routes.GET_COORD_LABELS.value + "?context_id=main")

        # Check the response
        assert response.status_code == 200
        result = json.loads(response.data)
        assert "left_coord_labels" in result
        assert "right_coord_labels" in result
        assert result["left_coord_labels"] == ["left_x", "left_y", "left_z"]
        assert result["right_coord_labels"] == ["right_x", "right_y", "right_z"]
    
    def test_get_crosshair_coords(self, client, mock_data_manager_ctx):
        """Test GET_CROSSHAIR_COORDS route."""
        # Setup
        mock_data_manager_ctx.get_crosshair_coords.return_value = {"x": 10, "y": 20, "z": 30}
        
        # Make the request with context_id
        response = client.get(Routes.GET_CROSSHAIR_COORDS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"x": 10, "y": 20, "z": 30}
        mock_data_manager_ctx.get_crosshair_coords.assert_called_once()
    
    def test_get_direction_label_coords(self, client, mock_data_manager_ctx):
        """Test GET_DIRECTION_LABEL_COORDS route."""
        # Setup
        mock_data_manager_ctx.get_direction_label_coords.return_value = {"x": 10, "y": 20, "z": 30}
        
        # Make the request with context_id
        response = client.get(Routes.GET_DIRECTION_LABEL_COORDS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"x": 10, "y": 20, "z": 30}
        mock_data_manager_ctx.get_direction_label_coords.assert_called_once()
    
    def test_get_fmri_data(self, client, mock_data_manager_ctx):
        """Test GET_FMRI_DATA route."""
        # This is a more complex route requiring more mocking
        # Setup
        mock_data_manager_ctx.get_fmri_plot_options.return_value = {
            "threshold_min": 0.1,
            "threshold_max": 0.9
        }
        
        mock_viewer_data = {
            "func_img": MagicMock(),
            "anat_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = mock_viewer_data
        mock_data_manager_ctx.color_options_original = {
            "threshold_min": 0.0, 
            "threshold_max": 1.0
        }
        
        # Mock the get_nifti_data function
        with patch('findviz.routes.viewer.data.get_nifti_data') as mock_get_nifti_data:
            mock_get_nifti_data.return_value = {"slice_data": [[[0.5]]]}
            
            # Make the request with context_id
            response = client.get(Routes.GET_FMRI_DATA.value + "?context_id=main")
            
            # Check the response
            assert response.status_code == 200
            result = json.loads(response.data)
            assert "data" in result
            assert "plot_options" in result
            assert result["data"] == {"slice_data": [[[0.5]]]}
            mock_data_manager_ctx.get_viewer_data.assert_called_once()
            mock_get_nifti_data.assert_called_once()
    
    def test_get_last_timecourse(self, client, mock_data_manager_ctx):
        """Test GET_LAST_TIMECOURSE route."""
        # Setup
        mock_data_manager_ctx.get_last_timecourse.return_value = {"timecourse": [1, 2, 3]}
        
        # Make the request with context_id
        response = client.get(Routes.GET_LAST_TIMECOURSE.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"timecourse": [1, 2, 3]}
        mock_data_manager_ctx.get_last_timecourse.assert_called_once()
    
    def test_get_distance_data(self, client, mock_data_manager_ctx):
        """Test GET_DISTANCE_DATA route."""
        # Setup
        mock_data_manager_ctx.distance_data = np.array([0.1, 0.2, 0.3])
        expected_data = [0.1, 0.2, 0.3]
        
        # Make the request with context_id
        response = client.get(Routes.GET_DISTANCE_DATA.value + "?context_id=main")

        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == expected_data
    
    def test_get_montage_data(self, client, mock_data_manager_ctx):
        """Test GET_MONTAGE_DATA route."""
        # Make the request with context_id
        response = client.get(Routes.GET_MONTAGE_DATA.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["montage_slice_dir"] == mock_data_manager_ctx.montage_slice_dir
        assert result["montage_slice_idx"] == mock_data_manager_ctx.montage_slice_idx
        assert result["montage_slice_len"] == mock_data_manager_ctx.slice_len

    def test_get_task_conditions(self, client, mock_data_manager_ctx):
        """Test GET_TASK_CONDITIONS route."""
        # Setup
        mock_data_manager_ctx.task_conditions = ["rest", "task"]
        
        # Make the request with context_id
        response = client.get(Routes.GET_TASK_CONDITIONS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == ["rest", "task"]
    
    def test_get_timecourse_data(self, client, mock_data_manager_ctx):
        """Test GET_TIMECOURSE_DATA route."""
        # Setup mock data
        ts_data = {
            "voxel_1": [0.1, 0.2, 0.3, 0.4],
            "voxel_2": [0.5, 0.6, 0.7, 0.8]
        }
        task_data = {
            "rest": [1, 0, 0, 0],
            "task": [0, 1, 1, 0]
        }
        
        # Mock the viewer_data returned by get_viewer_data
        mock_data_manager_ctx.get_viewer_data.return_value = {
            "ts": ts_data,
            "task": task_data
        }
        
        # Test 1: Request with specific ts_labels
        requested_labels = ["voxel_1", "rest", "task"]
        response = client.get(
            f"{Routes.GET_TIMECOURSE_DATA.value}?context_id=main&ts_labels={json.dumps(requested_labels)}"
        )
        
        # Check the response contains only the requested label
        assert response.status_code == 200
        result = json.loads(response.data)
        assert "voxel_1" in result
        assert "voxel_2" not in result
        assert result["voxel_1"] == [0.1, 0.2, 0.3, 0.4]
        # Task data should also be included
        assert "rest" in result
        assert "task" in result
        
        # Test 2: Request without ts_labels (should return all)
        response = client.get(
            f"{Routes.GET_TIMECOURSE_DATA.value}?context_id=main&ts_labels=null"
        )
        
        # Check the response contains all timecourse data
        assert response.status_code == 200
        result = json.loads(response.data)
        assert "voxel_1" in result
        assert "voxel_2" in result
        assert "rest" in result
        assert "task" in result
        
        # Verify the get_viewer_data was called with correct parameters
        mock_data_manager_ctx.get_viewer_data.assert_called_with(
            fmri_data=False,
            time_course_data=True,
            task_data=True
        )
    
    def test_get_timecourse_labels(self, client, mock_data_manager_ctx):
        """Test GET_TIMECOURSE_LABELS route."""
        # Make the request with context_id
        response = client.get(Routes.GET_TIMECOURSE_LABELS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == ["voxel_1", "voxel_2"]
    
    def test_get_timecourse_labels_preprocessed(self, client, mock_data_manager_ctx):
        """Test GET_TIMECOURSE_LABELS_PREPROCESSED route."""
        # Make the request with context_id
        response = client.get(Routes.GET_TIMECOURSE_LABELS_PREPROCESSED.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == ["voxel_1_preprocessed"]
    
    def test_get_timecourse_source(self, client, mock_data_manager_ctx):
        """Test GET_TIMECOURSE_SOURCE route."""
        # Make the request with context_id
        response = client.get(Routes.GET_TIMECOURSE_SOURCE.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            'timecourse_source': {
                "voxel_1": "timecourse", 
                "voxel_2": "timecourse",
                "rest": "task", 
                "task": "task"
            }
        }

    def test_get_timepoint(self, client, mock_data_manager_ctx):
        """Test GET_TIMEPOINT route."""
        # Setup
        mock_data_manager_ctx.timepoint = 5
        expected_data = {"timepoint": 5}
        
        # Make the request with context_id
        response = client.get(Routes.GET_TIMEPOINT.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == expected_data

    def test_get_timepoints(self, client, mock_data_manager_ctx):
        """Test GET_TIMEPOINTS route."""
        # Setup
        expected_timepoints = [0, 1, 2, 3, 4]
        mock_data_manager_ctx.get_timepoints.return_value = expected_timepoints
        expected_data = {"timepoints": expected_timepoints}
        
        # Make the request with context_id
        response = client.get(Routes.GET_TIMEPOINTS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == expected_data
        mock_data_manager_ctx.get_timepoints.assert_called_once()

    def test_get_vertex_coords(self, client, mock_data_manager_ctx):
        """Test GET_VERTEX_COORDS route."""
        # Setup
        mock_data_manager_ctx.selected_vertex = 0
        mock_data_manager_ctx.selected_hemi = "left"
        
        # Make the request with context_id
        response = client.get(Routes.GET_VERTEX_COORDS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            'vertex_number': 0,
            'selected_hemisphere': 'left'
        }
    
    def test_get_viewer_metadata(self, client, mock_data_manager_ctx):
        """Test GET_VIEWER_METADATA route.""" 
        # Setup
        mock_data_manager_ctx.get_viewer_metadata.return_value = {
            "file_type": "nifti",
            "timepoint": 0,
            "anat_input": False,
            "mask_input": False,
            "tr": 2.0,
            "slicetime_ref": None,
            "view_state": "ortho",
            "montage_slice_dir": "x",
            "timepoints": [0, 1, 2, 3, 4],
            "fmri_preprocessed": False,
            "ts_preprocessed": True,
            "global_min": 0.0,
            "global_max": 1.0,
            "slice_len": {"x": 10, "y": 10, "z": 10},
            "ts_enabled": True,
            "task_enabled": True
        }
        response = client.get(Routes.GET_VIEWER_METADATA.value + "?context_id=main")

        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "file_type": "nifti",
            "timepoint": 0,
            "anat_input": False,
            "mask_input": False,
            "tr": 2.0,
            "slicetime_ref": None,
            "view_state": "ortho",
            "montage_slice_dir": "x",
            "timepoints": [0, 1, 2, 3, 4],
            "fmri_preprocessed": False,
            "ts_preprocessed": True,
            "global_min": 0.0,
            "global_max": 1.0,
            "slice_len": {"x": 10, "y": 10, "z": 10},
            "ts_enabled": True,
            "task_enabled": True
        }
        mock_data_manager_ctx.get_viewer_metadata.assert_called_once()
    
    def test_get_voxel_coords(self, client, mock_data_manager_ctx):
        """Test GET_VOXEL_COORDS route."""
        # Setup
        expected_data = [10, 20, 30]
        mock_data_manager_ctx.get_slice_idx.return_value = expected_data
        
        # Make the request with context_id
        response = client.get(Routes.GET_VOXEL_COORDS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == expected_data
        mock_data_manager_ctx.get_slice_idx.assert_called_once()
    
    def test_get_voxel_coords_montage(self, client, mock_data_manager_ctx):
        """Test GET_VOXEL_COORDS route with montage view state."""
        # Setup
        expected_data = {"slice_1": [10, 20, 30]}
        mock_data_manager_ctx.view_state = "montage"
        mock_data_manager_ctx.selected_slice = 'slice_1'
        mock_data_manager_ctx.get_slice_idx.return_value = expected_data
        
        # Make the request with context_id
        response = client.get(Routes.GET_VOXEL_COORDS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == [10, 20, 30]

    def test_get_world_coords(self, client, mock_data_manager_ctx):
        """Test GET_WORLD_COORDS route."""
        # Setup
        mock_data_manager_ctx.get_world_coords.return_value = [10, 20, 30]
        expected_data = {"x": 10, "y": 20, "z": 30}
        
        # Make the request with context_id
        response = client.get(Routes.GET_WORLD_COORDS.value + "?context_id=main")
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == expected_data
        mock_data_manager_ctx.get_world_coords.assert_called_once()
    
    def test_pop_fmri_timecourse(self, client, mock_data_manager_ctx, form_content_type):
        """Test POP_FMRI_TIMECOURSE route."""
        # Setup
        mock_data_manager_ctx.pop_fmri_timecourse.return_value = "voxel_1"
        
        # Make the request with context_id
        response = client.post(
            Routes.POP_FMRI_TIMECOURSE.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"label": "voxel_1"}
        mock_data_manager_ctx.pop_fmri_timecourse.assert_called_once()
    
    def test_remove_fmri_timecourses(self, client, mock_data_manager_ctx, form_content_type):
        """Test REMOVE_FMRI_TIMECOURSES route."""
        # Setup
        mock_data_manager_ctx.remove_fmri_timecourses.return_value = ["voxel_1", "voxel_2"]
        
        # Make the request with context_id
        response = client.post(
            Routes.REMOVE_FMRI_TIMECOURSES.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"labels": ["voxel_1", "voxel_2"]}
        mock_data_manager_ctx.remove_fmri_timecourses.assert_called_once()
    
    def test_update_location_nifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_LOCATION route for nifti data."""
        # Get the old values
        old_click_coords = mock_data_manager_ctx.click_coords
        old_selected_slice = mock_data_manager_ctx.selected_slice
        
        # Make the request with context_id - convert dictionary to JSON string
        response = client.post(
            Routes.UPDATE_LOCATION.value,
            data={
                "click_coords": json.dumps({"x": 20, "y": 10}),  # Convert to JSON string
                "slice_name": "slice_2", 
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_location.assert_called_once_with(
            {"x": 20, "y": 10}, "slice_2"
        )
        # Check that the click_coords and slice_name were updated
        assert mock_data_manager_ctx.click_coords == {"x": 20, "y": 10}
        assert mock_data_manager_ctx.selected_slice == "slice_2"
        # Check that the click_coords and slice_name were not reset to the old values
        assert mock_data_manager_ctx.click_coords != old_click_coords
        assert mock_data_manager_ctx.selected_slice != old_selected_slice
    
    def test_update_location_gifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_LOCATION route for gifti data."""
        # Setup
        mock_data_manager_ctx.file_type = "gifti"
        # Get the old values
        old_selected_vertex = mock_data_manager_ctx.selected_vertex
        old_selected_hemi = mock_data_manager_ctx.selected_hemi
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_LOCATION.value,
            data={
                "click_coords": json.dumps({"selected_vertex": 1, "selected_hemi": "right"}),
                "slice_name": '',
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_location.assert_called_once_with(
            {"selected_vertex": 1, "selected_hemi": "right"}, ''
        )
        # Check that the selected_vertex and selected_hemi were updated
        assert mock_data_manager_ctx.selected_vertex == 1
        assert mock_data_manager_ctx.selected_hemi == "right"
        # Check that the selected_vertex and selected_hemi were not reset to the old values
        assert mock_data_manager_ctx.selected_vertex != old_selected_vertex
        assert mock_data_manager_ctx.selected_hemi != old_selected_hemi

    def test_update_fmri_timecourse_nifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_FMRI_TIMECOURSE route for nifti data."""
        # Setup
        mock_viewer_data = {
            "func_img": MagicMock(),
            "anat_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = mock_viewer_data
        mock_data_manager_ctx.get_slice_idx.return_value = {'x': 0, 'y': 1, 'z': 2}

        # Mock the get_timecourse_nifti function
        with patch('findviz.routes.viewer.data.get_timecourse_nifti') as mock_get_timecourse_nifti:
            mock_get_timecourse_nifti.return_value = (
                [1, 2, 3], 
                "voxel_1"
            )

            # Make the request with context_id
            response = client.post(
                Routes.UPDATE_FMRI_TIMECOURSE.value,
                data={"context_id": "main"},
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            mock_data_manager_ctx.get_viewer_data.assert_called_once_with(
                fmri_data=True,
                time_course_data=False,
                task_data=False
            )
            mock_get_timecourse_nifti.assert_called_once_with(
                func_img=mock_viewer_data["func_img"],
                x=0, y=1, z=2
            )
            mock_data_manager_ctx.update_timecourse.assert_called_once_with(
                [1, 2, 3],
                "voxel_1"
            )
    
    def test_update_fmri_timecourse_gifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_FMRI_TIMECOURSE route for gifti data."""
        # Setup
        mock_data_manager_ctx.fmri_file_type = "gifti"
        mock_viewer_data = {
            "left_func_img": MagicMock(),
            "right_func_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = mock_viewer_data
        mock_data_manager_ctx.get_click_coords.return_value = {"selected_vertex": 0, "selected_hemi": "left"}

        # Mock the get_timecourse_gifti function
        with patch('findviz.routes.viewer.data.get_timecourse_gifti') as mock_get_timecourse_gifti:
            mock_get_timecourse_gifti.return_value = (
                [1, 2, 3],
                "vertex_1"
            )

            # Make the request with context_id
            response = client.post(
                Routes.UPDATE_FMRI_TIMECOURSE.value,
                data={"context_id": "main"},
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            mock_get_timecourse_gifti.assert_called_once_with(
                left_func_img=mock_viewer_data["left_func_img"],
                right_func_img=mock_viewer_data["right_func_img"],
                vertex_index=0,
                hemisphere="left"
            )
            mock_data_manager_ctx.update_timecourse.assert_called_once_with(
                [1, 2, 3],
                "vertex_1"
            )

    def test_update_montage_slice_dir(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_MONTAGE_SLICE_DIR route."""
        # Setup
        mock_data_manager_ctx.view_state = "montage"
        mock_data_manager_ctx.montage_slice_dir = "x"
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_MONTAGE_SLICE_DIR.value,
            data={"montage_slice_dir": "x", "slice_name": "slice_1", "context_id": "main"},
            headers=form_content_type
        )

        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_montage_slice_dir.assert_called_once_with("x")
    
    def test_update_montage_slice_idx(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_MONTAGE_SLICE_IDX route."""
        # Setup
        mock_data_manager_ctx.view_state = "montage"
        mock_data_manager_ctx.montage_slice_dir = "x"
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_MONTAGE_SLICE_IDX.value,
            data={"slice_idx": 1, "slice_name": "slice_1", "context_id": "main"},
            headers=form_content_type
        )

        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_montage_slice_idx.assert_called_once_with("slice_1", 1)
        # Verify update
        assert mock_data_manager_ctx.montage_slice_idx["x"]["slice_1"]["x"] == 1
        # Also verify the structure is preserved
        assert "y" in mock_data_manager_ctx.montage_slice_idx
        assert "z" in mock_data_manager_ctx.montage_slice_idx
    
    
    def test_update_timepoint(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_TIMEPOINT route."""
        # Setup
        old_timepoint = mock_data_manager_ctx.timepoint
        new_timepoint = 3
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_TIMEPOINT.value,
            data={"time_point": str(new_timepoint), "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.update_timepoint.assert_called_once_with(new_timepoint)
        # Check that the timepoint was updated
        assert mock_data_manager_ctx.timepoint == new_timepoint
        # Check that the timepoint was not reset to the old value
        assert mock_data_manager_ctx.timepoint != old_timepoint

    def test_update_tr(self, client, mock_data_manager_ctx, form_content_type):
        """Test UPDATE_TR route."""
        # Setup
        old_tr = mock_data_manager_ctx.tr
        new_tr = 1.0
        
        # Make the request with context_id
        response = client.post(
            Routes.UPDATE_TR.value,
            data={"tr": str(new_tr), "context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        mock_data_manager_ctx.set_tr.assert_called_once_with(new_tr)
        # Check that the tr was updated
        assert mock_data_manager_ctx.tr == new_tr
        # Check that the tr was not reset to the old value
        assert mock_data_manager_ctx.tr != old_tr       
        



