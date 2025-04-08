import pytest
import json
import numpy as np
from unittest.mock import patch, MagicMock
from nibabel import GiftiImage, Nifti1Image
from findviz.routes.utils import Routes
from findviz.viz.exception import (
    ParameterInputError, 
    PeakFinderNoPeaksFoundError,
    NiftiMaskError
)


@pytest.mark.usefixtures("mock_data_manager_ctx")
class TestAnalysisRoutes:
    """Test class for the analysis.py routes."""
    
    def test_correlate(self, client, mock_data_manager_ctx, form_content_type):
        """Test CORRELATE route."""
        # Setup
        viewer_data = {
            "func_img": MagicMock(spec=Nifti1Image),
            "anat_img": MagicMock(spec=Nifti1Image),
            "mask_img": MagicMock(spec=Nifti1Image),
            "ts": {"test_label": [1, 2, 3]},
            "task": {"test_task": [0, 1, 0]}
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.fmri_file_type = "nifti"
        
        # Mock transforms
        with patch('findviz.routes.viewer.analysis.transforms.nifti_to_array_masked') as mock_nifti_to_array, \
        patch('findviz.routes.viewer.analysis.transforms.array_to_nifti_masked') as mock_array_to_nifti, \
        patch('findviz.routes.viewer.analysis.Correlate') as mock_correlate_class, \
        patch('findviz.viz.viewer.data_manager.DataManager.create_analysis_context') as mock_create_analysis_context, \
        patch('findviz.viz.viewer.data_manager.DataManager.switch_context') as mock_switch_context:
            # Setup mocks
            mock_nifti_to_array.return_value = np.array([[1, 2], [3, 4]])
            mock_correlate_instance = MagicMock()
            mock_correlate_instance.correlate.return_value = np.array([0.5, 0.6])
            mock_correlate_instance.lags = np.array([-1, 0, 1])
            mock_correlate_class.return_value = mock_correlate_instance
            mock_array_to_nifti.return_value = MagicMock(spec=Nifti1Image)
            
            # Make the request
            response = client.post(
                Routes.CORRELATE.value,
                data={
                    "label": "test_label",
                    "time_course_type": "timecourse",
                    "negative_lag": "-1",
                    "positive_lag": "1",
                    "context_id": "main"
                },
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once()
            mock_nifti_to_array.assert_called_once_with(viewer_data["func_img"], viewer_data["mask_img"])
            mock_correlate_class.assert_called_once_with(negative_lag=-1, positive_lag=1, time_length=2)
            mock_correlate_instance.correlate.assert_called_once()
            mock_array_to_nifti.assert_called_once()
            mock_create_analysis_context.assert_called_once_with("correlate")
            mock_switch_context.assert_called_once_with("correlate")
            mock_data_manager_ctx.create_nifti_state.assert_called_once()
            mock_data_manager_ctx.set_timepoints.assert_called_once_with([-1, 0, 1])
    
    def test_correlate_gifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test CORRELATE route with gifti file type."""
        # Setup
        # Create a more elaborate mock for GiftiImage
        mock_left_img = MagicMock(spec=GiftiImage)
        mock_right_img = MagicMock(spec=GiftiImage)
        mock_data_manager_ctx.n_timepoints = 3
        
        # Set up the darrays attribute with the expected structure
        mock_darr1 = MagicMock()
        mock_darr1.data = np.array([0.1, 0.2, 0.3])
        mock_darr2 = MagicMock()
        mock_darr2.data = np.array([0.2, 0.3, 0.4])
        
        mock_left_img.darrays = [mock_darr1, mock_darr2]
        mock_right_img.darrays = [mock_darr1, mock_darr2]
        
        viewer_data = {
            "left_func_img": mock_left_img,
            "right_func_img": mock_right_img,
            "ts": {"test_label": [1, 2, 3]},
            "task": {"test_task": [0, 1, 0]}
        }
        
        viewer_metadata = {
            "faces_left": [[0, 1, 2]],
            "faces_right": [[0, 1, 2]],
            "vertices_left": [[0, 0, 0]],
            "vertices_right": [[0, 0, 0]]
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.get_viewer_metadata.return_value = viewer_metadata
        mock_data_manager_ctx.fmri_file_type = "gifti"
        mock_data_manager_ctx.both_hemispheres = True
        mock_data_manager_ctx.left_surface_input = True
        mock_data_manager_ctx.right_surface_input = True
        
        # Mock transforms
        with patch('findviz.routes.viewer.analysis.transforms.gifti_to_array') as mock_gifti_to_array, \
        patch('findviz.routes.viewer.analysis.transforms.array_to_gifti') as mock_array_to_gifti, \
        patch('findviz.routes.viewer.analysis.Correlate') as mock_correlate_class, \
        patch('findviz.viz.viewer.utils.get_fmri_minmax') as mock_get_fmri_minmax, \
        patch('findviz.viz.viewer.data_manager.DataManager.create_analysis_context') as mock_create_analysis_context, \
        patch('findviz.viz.viewer.data_manager.DataManager.switch_context') as mock_switch_context:
            
            # Setup mocks
            mock_gifti_to_array.return_value = (np.array([[1, 2, 3], [4, 5, 6]]), 1)
            mock_correlate_instance = MagicMock()
            mock_correlate_instance.correlate.return_value = np.array([0.5, 0.6])
            mock_correlate_instance.lags = np.array([-1, 0, 1])
            mock_correlate_class.return_value = mock_correlate_instance
            
            # Configure the mock GiftiImage objects for the return value
            mock_left_result = MagicMock(spec=GiftiImage)
            mock_left_result.darrays = [mock_darr1, mock_darr1, mock_darr1]
            mock_right_result = MagicMock(spec=GiftiImage)
            mock_right_result.darrays = [mock_darr2, mock_darr2, mock_darr2]
            mock_array_to_gifti.return_value = [mock_left_result, mock_right_result]
            
            # Mock get_fmri_minmax to avoid the deep attribute access
            mock_get_fmri_minmax.return_value = (0.0, 1.0)
            
            # Make the request
            response = client.post(
                Routes.CORRELATE.value,
                data={
                    "label": "test_label",
                    "time_course_type": "timecourse",
                    "negative_lag": "1",
                    "positive_lag": "1",
                    "context_id": "main"
                },
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once()
            mock_gifti_to_array.assert_called_once_with(viewer_data["left_func_img"], viewer_data["right_func_img"])
            mock_correlate_class.assert_called_once_with(negative_lag=1, positive_lag=1, time_length=2)
            mock_correlate_instance.correlate.assert_called_once()
            mock_array_to_gifti.assert_called_once()
            mock_create_analysis_context.assert_called_once_with("correlate")
            mock_switch_context.assert_called_once_with("correlate")
            mock_data_manager_ctx.create_gifti_state.assert_called_once()
            mock_data_manager_ctx.set_timepoints.assert_called_once_with([-1, 0, 1])

    
    def test_correlate_nifti_mask_error(self, client, mock_data_manager_ctx, form_content_type):
        """Test CORRELATE route with nifti mask error."""
        # Setup
        viewer_data = {
            "func_img": MagicMock(),
            "anat_img": MagicMock(),
            "mask_img": None,
            "ts": {"test_label": [1, 2, 3]},
            "task": {"test_task": [0, 1, 0]}
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.fmri_file_type = "nifti"
        
        # Make the request
        response = client.post(
            Routes.CORRELATE.value,
            data={
                "label": "test_label",
                "time_course_type": "timecourse",
                "negative_lag": "1",
                "positive_lag": "1",
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 400
        assert b"A brain mask is required for nifti preprocessing" in response.data
    
    def test_distance(self, client, mock_data_manager_ctx, form_content_type):
        """Test DISTANCE route."""
        # Setup
        viewer_data = {
            "func_img": MagicMock(),
            "mask_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.fmri_file_type = "nifti"
        mock_data_manager_ctx.timepoint = 5
        
        # Mock transforms and Distance class
        with patch('findviz.routes.viewer.analysis.transforms.nifti_to_array_masked') as mock_nifti_to_array:
            with patch('findviz.routes.viewer.analysis.Distance') as mock_distance_class:
                # Setup mocks
                mock_nifti_to_array.return_value = np.array([[1, 2], [3, 4]])
                mock_distance_instance = MagicMock()
                mock_distance_instance.calculate_distance.return_value = np.array([0.1, 0.2])
                mock_distance_class.return_value = mock_distance_instance
                
                # Make the request
                response = client.post(
                    Routes.DISTANCE.value,
                    data={
                        "distance_metric": "euclidean",
                        "context_id": "main"
                    },
                    headers=form_content_type
                )
                
                # Check the response
                assert response.status_code == 200
                assert json.loads(response.data) == {"status": "success"}
                
                # Verify calls
                mock_data_manager_ctx.get_viewer_data.assert_called_once()
                mock_nifti_to_array.assert_called_once_with(viewer_data["func_img"], viewer_data["mask_img"])
                mock_distance_class.assert_called_once_with(distance_metric="euclidean")
                mock_distance_instance.calculate_distance.assert_called_once_with(5, mock_nifti_to_array.return_value)
                args, kwargs = mock_data_manager_ctx.create_distance_plot_state.call_args
                assert np.array_equal(args[0], np.array([0.1, 0.2]))
    
    def test_distance_gifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test DISTANCE route with gifti file type."""
        # Setup
        viewer_data = {
            "left_func_img": MagicMock(),
            "right_func_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.fmri_file_type = "gifti"
        mock_data_manager_ctx.timepoint = 5
        
        # Mock transforms and Distance class
        with patch('findviz.routes.viewer.analysis.transforms.gifti_to_array') as mock_gifti_to_array:
            with patch('findviz.routes.viewer.analysis.Distance') as mock_distance_class:
                # Setup mocks
                mock_gifti_to_array.return_value = (np.array([[1, 2], [3, 4]]), 1)
                mock_distance_instance = MagicMock()
                mock_distance_instance.calculate_distance.return_value = np.array([0.1, 0.2])
                mock_distance_class.return_value = mock_distance_instance
                
                # Make the request
                response = client.post(
                    Routes.DISTANCE.value,
                    data={
                        "distance_metric": "correlation",
                        "context_id": "main"
                    },
                    headers=form_content_type
                )
                
                # Check the response
                assert response.status_code == 200
                assert json.loads(response.data) == {"status": "success"}
                
                # Verify calls
                mock_data_manager_ctx.get_viewer_data.assert_called_once()
                mock_gifti_to_array.assert_called_once_with(viewer_data["left_func_img"], viewer_data["right_func_img"])
                mock_distance_class.assert_called_once_with(distance_metric="correlation")
                mock_distance_instance.calculate_distance.assert_called_once_with(5, mock_gifti_to_array.return_value[0])
                args, kwargs = mock_data_manager_ctx.create_distance_plot_state.call_args
                assert np.array_equal(args[0], np.array([0.1, 0.2]))
    
    def test_distance_nifti_mask_error(self, client, mock_data_manager_ctx, form_content_type):
        """Test DISTANCE route with nifti mask error."""
        # Setup
        viewer_data = {
            "func_img": MagicMock(),
            "mask_img": None
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.fmri_file_type = "nifti"
        
        # Make the request
        response = client.post(
            Routes.DISTANCE.value,
            data={
                "distance_metric": "euclidean",
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 400
        assert b"A brain mask is required for time point distance calculation" in response.data
    
    def test_find_peaks(self, client, mock_data_manager_ctx, form_content_type):
        """Test FIND_PEAKS route."""
        # Setup
        viewer_data = {
            "ts": {"test_label": [1, 2, 3, 2, 1, 4, 3, 2]},
            "task": {"test_task": [0, 1, 1, 0, 0, 1, 1, 0]}
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        
        # Mock PeakFinder class
        with patch('findviz.routes.viewer.analysis.PeakFinder') as mock_peak_finder_class:
            # Setup mocks
            mock_peak_finder_instance = MagicMock()
            mock_peak_finder_instance.find_peaks.return_value = np.array([2, 5])
            mock_peak_finder_class.return_value = mock_peak_finder_instance
            
            # Make the request
            response = client.post(
                Routes.FIND_PEAKS.value,
                data={
                    "label": "test_label",
                    "time_course_type": "timecourse",
                    "peak_finder_params": json.dumps({
                        "zscore": "True",
                        "peak_distance": "1",
                        "peak_height": "0.5",
                        "peak_prominence": "0.1",
                        "peak_width": "1",
                        "peak_threshold": "0.0"
                    }),
                    "context_id": "main"
                },
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once()
            mock_peak_finder_class.assert_called_once_with(
                zscore=True,
                peak_distance=1,
                peak_height=0.5,
                peak_prominence=0.1,
                peak_width=1,
                peak_threshold=0.0
            )
            mock_peak_finder_instance.find_peaks.assert_called_once_with(viewer_data["ts"]["test_label"])
            mock_data_manager_ctx.add_annotation_markers.assert_called_once_with([2, 5])
    
    def test_find_peaks_task(self, client, mock_data_manager_ctx, form_content_type):
        """Test FIND_PEAKS route with task time course type."""
        # Setup
        viewer_data = {
            "ts": {"test_label": [1, 2, 3, 2, 1, 4, 3, 2]},
            "task": {"test_task": [0, 1, 1, 0, 0, 1, 1, 0]}
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        
        # Mock PeakFinder class
        with patch('findviz.routes.viewer.analysis.PeakFinder') as mock_peak_finder_class:
            # Setup mocks
            mock_peak_finder_instance = MagicMock()
            mock_peak_finder_instance.find_peaks.return_value = np.array([1, 5])
            mock_peak_finder_class.return_value = mock_peak_finder_instance
            
            # Make the request
            response = client.post(
                Routes.FIND_PEAKS.value,
                data={
                    "label": "test_task",
                    "time_course_type": "task",
                    "peak_finder_params": json.dumps({
                        "zscore": "False",
                        "peak_distance": "1",
                        "peak_height": "0.5",
                        "peak_prominence": "0.1",
                        "peak_width": "1",
                        "peak_threshold": "0.0"
                    }),
                    "context_id": "main"
                },
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once()
            mock_peak_finder_instance.find_peaks.assert_called_once_with(viewer_data["task"]["test_task"])
            mock_data_manager_ctx.add_annotation_markers.assert_called_once_with([1, 5])
    
    def test_windowed_average(self, client, mock_data_manager_ctx, form_content_type):
        """Test WINDOWED_AVERAGE route."""
        # Setup
        viewer_data = {
            "func_img": MagicMock(),
            "anat_img": MagicMock(),
            "mask_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.fmri_file_type = "nifti"
        mock_data_manager_ctx.annotation_markers = [2, 5]
        mock_data_manager_ctx.n_timepoints = 8
        
        # Mock transforms and WindowAverage class
        with patch('findviz.routes.viewer.analysis.transforms.nifti_to_array_masked') as mock_nifti_to_array, \
             patch('findviz.routes.viewer.analysis.transforms.array_to_nifti_masked') as mock_array_to_nifti, \
             patch('findviz.routes.viewer.analysis.WindowAverage') as mock_window_average_class, \
             patch('findviz.viz.viewer.data_manager.DataManager.create_analysis_context') as mock_create_analysis_context, \
             patch('findviz.viz.viewer.data_manager.DataManager.switch_context') as mock_switch_context:
            
            # Setup mocks
            mock_nifti_to_array.return_value = np.array([[1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1]])
            mock_window_average_instance = MagicMock()
            mock_window_average_instance.average.return_value = np.array([3, 4])
            mock_window_average_instance.get_timepoints.return_value = [0]
            mock_window_average_class.return_value = mock_window_average_instance
            mock_array_to_nifti.return_value = MagicMock()
            
            # Make the request
            response = client.post(
                Routes.WINDOWED_AVERAGE.value,
                data={
                    "window_average_params": json.dumps({
                        "left_edge": "1",
                        "right_edge": "1"
                    }),
                    "context_id": "main"
                },
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once()
            mock_nifti_to_array.assert_called_once_with(viewer_data["func_img"], viewer_data["mask_img"])
            mock_window_average_class.assert_called_once_with(left_edge=1, right_edge=1, n_timepoints=8)
            mock_window_average_instance.average.assert_called_once_with(
                mock_nifti_to_array.return_value, 
                mock_data_manager_ctx.annotation_markers
            )
            mock_array_to_nifti.assert_called_once()
            
            # Verify DataManager method calls
            mock_create_analysis_context.assert_called_once_with("average")
            mock_switch_context.assert_called_once_with("average")
    
    def test_windowed_average_gifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test WINDOWED_AVERAGE route with gifti file type."""
        # Setup
        viewer_data = {
            "left_func_img": MagicMock(),
            "right_func_img": MagicMock()
        }
        viewer_metadata = {
            "faces_left": [[0, 1, 2]],
            "faces_right": [[0, 1, 2]],
            "vertices_left": [[0, 0, 0]],
            "vertices_right": [[0, 0, 0]]
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.get_viewer_metadata.return_value = viewer_metadata
        mock_data_manager_ctx.fmri_file_type = "gifti"
        mock_data_manager_ctx.both_hemispheres = True
        mock_data_manager_ctx.left_surface_input = True
        mock_data_manager_ctx.right_surface_input = True
        mock_data_manager_ctx.annotation_markers = [2, 5]
        mock_data_manager_ctx.n_timepoints = 4
        
        # Mock transforms and WindowAverage class
        with patch('findviz.routes.viewer.analysis.transforms.gifti_to_array') as mock_gifti_to_array, \
             patch('findviz.routes.viewer.analysis.transforms.array_to_gifti') as mock_array_to_gifti, \
             patch('findviz.routes.viewer.analysis.WindowAverage') as mock_window_average_class, \
             patch('findviz.viz.viewer.utils.get_fmri_minmax') as mock_get_fmri_minmax, \
             patch('findviz.viz.viewer.data_manager.DataManager.create_analysis_context') as mock_create_analysis_context, \
             patch('findviz.viz.viewer.data_manager.DataManager.switch_context') as mock_switch_context:
            
            # Setup mocks
            mock_gifti_to_array.return_value = (np.array([[1, 2, 3, 4], [8, 7, 6, 5]]), 1)
            mock_window_average_instance = MagicMock()
            mock_window_average_instance.average.return_value = np.array([1, 2, 3, 4])
            mock_window_average_instance.get_timepoints.return_value = [0, 1, 2, 3]
            mock_window_average_class.return_value = mock_window_average_instance
            mock_array_to_gifti.return_value = [MagicMock(), MagicMock()]
            
            # Mock the get_fmri_minmax function to avoid type checking
            mock_get_fmri_minmax.return_value = (0.0, 1.0)
            
            # Make the request
            response = client.post(
                Routes.WINDOWED_AVERAGE.value,
                data={
                    "window_average_params": json.dumps({
                        "left_edge": "1",
                        "right_edge": "1"
                    }),
                    "context_id": "main"
                },
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once()
            mock_gifti_to_array.assert_called_once_with(viewer_data["left_func_img"], viewer_data["right_func_img"])
            mock_window_average_class.assert_called_once_with(left_edge=1, right_edge=1, n_timepoints=4)
            mock_window_average_instance.average.assert_called_once_with(
                mock_gifti_to_array.return_value[0], 
                mock_data_manager_ctx.annotation_markers
            )
            mock_array_to_gifti.assert_called_once()
            
            # Verify DataManager method calls
            mock_create_analysis_context.assert_called_once_with("average")
            mock_switch_context.assert_called_once_with("average")
    
    def test_windowed_average_nifti_mask_error(self, client, mock_data_manager_ctx, form_content_type):
        """Test WINDOWED_AVERAGE route with nifti mask error."""
        # Setup
        viewer_data = {
            "func_img": MagicMock(),
            "anat_img": MagicMock(),
            "mask_img": None
        }
        mock_data_manager_ctx.get_viewer_data.return_value = viewer_data
        mock_data_manager_ctx.fmri_file_type = "nifti"
        
        # Make the request
        response = client.post(
            Routes.WINDOWED_AVERAGE.value,
            data={
                "window_average_params": json.dumps({
                    "left_edge": "1",
                    "right_edge": "1"
                }),
                "context_id": "main"
            },
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 400
        assert b"A brain mask is required for nifti preprocessing" in response.data
