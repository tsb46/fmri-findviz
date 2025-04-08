import pytest
import json
import numpy as np
from unittest.mock import patch, MagicMock

from findviz.routes.utils import Routes
from findviz.viz.preprocess.fmri import PreprocessFMRIInputs
from findviz.viz.preprocess.timecourse import PreprocessTimecourseInputs
from findviz.viz.exception import PreprocessInputError, NiftiMaskError


@pytest.mark.usefixtures("mock_data_manager_ctx")
class TestPreprocessRoutes:
    """Test class for the preprocess.py routes."""
    
    def test_get_preprocessed_fmri_nifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test GET_PREPROCESSED_FMRI route with nifti file type."""
        # Setup
        mock_data_manager_ctx.fmri_file_type = "nifti"
        mock_data_manager_ctx.fmri_preprocessed = False
        
        # Mock viewer data that will be returned by get_viewer_data
        mock_viewer_data = {
            "func_img": MagicMock(),
            "mask_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = mock_viewer_data
        
        # Mock the preprocess_fmri function
        with patch('findviz.routes.viewer.preprocess.preprocess_fmri') as mock_preprocess_fmri:
            mock_preprocess_fmri.return_value = MagicMock()
            
            # Create input parameters
            params = {
                "standardize": "True",
                "detrend": "False",
                "high_pass": "0.01",
                "low_pass": "0.1",
                "smooth": "5.0",
                "fwhm": "5",
                "normalize": "False",
                "mean_center": "False",
                "zscore": "False",
                "filter": "True",
                "high_cut": "0.1",
                "low_cut": "0.01",
                "context_id": "main",
                "tr": "2"
            }
            
            # Make the request
            response = client.post(
                Routes.GET_PREPROCESSED_FMRI.value,
                data=params,
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify the mock calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once_with(
                fmri_data=True,
                time_course_data=False,
                task_data=False
            )
            
            # Verify preprocess_fmri was called with correct parameters
            mock_preprocess_fmri.assert_called_once()
            call_args = mock_preprocess_fmri.call_args[1]
            assert call_args["file_type"] == "nifti"
            assert call_args["func_img"] == mock_viewer_data["func_img"]
            assert call_args["mask_img"] == mock_viewer_data["mask_img"]
            
            # Verify the preprocessed data was stored
            mock_data_manager_ctx.store_fmri_preprocessed.assert_called_once()
    
    def test_get_preprocessed_fmri_gifti(self, client, mock_data_manager_ctx, form_content_type):
        """Test GET_PREPROCESSED_FMRI route with gifti file type."""
        # Setup
        mock_data_manager_ctx.fmri_file_type = "gifti"
        mock_data_manager_ctx.fmri_preprocessed = False
        
        # Mock viewer data that will be returned by get_viewer_data
        mock_viewer_data = {
            "left_func_img": MagicMock(),
            "right_func_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = mock_viewer_data
        
        # Mock the preprocess_fmri function
        with patch('findviz.routes.viewer.preprocess.preprocess_fmri') as mock_preprocess_fmri:
            # For gifti, preprocess_fmri returns a tuple of two processed images
            mock_preprocess_fmri.return_value = (MagicMock(), MagicMock())
            
            # Create input parameters
            params = {
                "standardize": "True",
                "detrend": "False",
                "high_pass": "0.01",
                "low_pass": "0.1",
                "smooth": "5.0",
                "fwhm": "5",
                "normalize": "False",
                "mean_center": "False",
                "zscore": "False",
                "filter": "True",
                "high_cut": "0.1",
                "low_cut": "0.01",
                "context_id": "main",
                "tr": "2"
            }
            
            # Make the request
            response = client.post(
                Routes.GET_PREPROCESSED_FMRI.value,
                data=params,
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify the mock calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once_with(
                fmri_data=True,
                time_course_data=False,
                task_data=False
            )
            
            # Verify preprocess_fmri was called with correct parameters
            mock_preprocess_fmri.assert_called_once()
            call_args = mock_preprocess_fmri.call_args[1]
            assert call_args["file_type"] == "gifti"
            assert call_args["left_func_img"] == mock_viewer_data["left_func_img"]
            assert call_args["right_func_img"] == mock_viewer_data["right_func_img"]
            
            # Verify the preprocessed data was stored
            mock_data_manager_ctx.store_fmri_preprocessed.assert_called_once()
    
    def test_get_preprocessed_fmri_already_preprocessed(self, client, mock_data_manager_ctx, form_content_type):
        """Test GET_PREPROCESSED_FMRI route when data is already preprocessed."""
        # Setup
        mock_data_manager_ctx.fmri_file_type = "nifti"
        mock_data_manager_ctx.fmri_preprocessed = True
        
        # We need to mock both get_viewer_data and preprocess_fmri since the route calls them after clearing
        # Mock viewer data that will be returned by get_viewer_data
        mock_viewer_data = {
            "func_img": MagicMock(),
            "mask_img": MagicMock()
        }
        mock_data_manager_ctx.get_viewer_data.return_value = mock_viewer_data
        
        # Mock the preprocess_fmri function
        with patch('findviz.routes.viewer.preprocess.preprocess_fmri') as mock_preprocess_fmri:
            mock_preprocess_fmri.return_value = MagicMock()
            
            # Create input parameters
            params = {
                "standardize": "True",
                "detrend": "False",
                "smooth": "5.0",
                "fwhm": "5",
                "normalize": "False",
                "mean_center": "False",
                "zscore": "False",
                "filter": "True",
                "high_cut": "0.1",
                "low_cut": "0.01",
                "context_id": "main",
                "tr": "2"
            }
            
            # Make the request
            response = client.post(
                Routes.GET_PREPROCESSED_FMRI.value,
                data=params,
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify clear_fmri_preprocessed was called
            mock_data_manager_ctx.clear_fmri_preprocessed.assert_called_once()
            
            # Also verify that get_viewer_data and preprocess_fmri were called after clearing
            mock_data_manager_ctx.get_viewer_data.assert_called_once_with(
                fmri_data=True,
                time_course_data=False,
                task_data=False
            )
            mock_preprocess_fmri.assert_called_once()
    
    def test_get_preprocessed_fmri_validation_error(self, client, mock_data_manager_ctx, form_content_type):
        """Test GET_PREPROCESSED_FMRI route with validation error."""
        # Setup
        mock_data_manager_ctx.fmri_file_type = "nifti"
        mock_data_manager_ctx.fmri_preprocessed = False
        
        # Mock FMRIPreprocessInputValidator to raise PreprocessInputError
        with patch('findviz.routes.viewer.preprocess.FMRIPreprocessInputValidator') as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator.validate_preprocess_input.side_effect = PreprocessInputError("Invalid input")
            mock_validator_class.return_value = mock_validator
            
            # Create input parameters
            params = {
                "standardize": "True",
                "detrend": "False",
                "normalize": "False",
                "mean_center": "False",
                "zscore": "False",
                "filter": "True",
                "high_cut": "0.01",
                "low_cut": "0.1",
                "smooth": "invalid",  # Invalid value,
                "fwhm": "5",
                "context_id": "main",
                "tr": "2"
            }
            
            # Make the request
            response = client.post(
                Routes.GET_PREPROCESSED_FMRI.value,
                data=params,
                headers=form_content_type
            )
            
            # Check the response - should be an error
            assert response.status_code == 400
            # Check that the response contains the expected error message as a string
            assert b"Invalid input" in response.data
            
            # Verify validator was called
            mock_validator.validate_preprocess_input.assert_called_once()
    
    def test_get_preprocessed_timecourse(self, client, mock_data_manager_ctx, form_content_type):
        """Test GET_PREPROCESSED_TIMECOURSE route."""
        # Setup
        # Mock viewer data that will be returned by get_viewer_data
        mock_viewer_data = {
            "ts": {
                "voxel_1": np.array([0.1, 0.2, 0.3]),
                "voxel_2": np.array([0.4, 0.5, 0.6])
            }
        }
        mock_data_manager_ctx.get_viewer_data.return_value = mock_viewer_data
        
        # Mock the preprocess_timecourse function
        with patch('findviz.routes.viewer.preprocess.preprocess_timecourse') as mock_preprocess_timecourse:
            mock_preprocess_timecourse.return_value = np.array([0.2, 0.3, 0.4])
            
            # Create input parameters
            params = {
                "standardize": "True",
                "detrend": "False",
                "normalize": "False",
                "mean_center": "False",
                "zscore": "False",
                "filter": "True",
                "high_cut": "0.1",
                "low_cut": "0.01",
                "ts_labels": json.dumps(["voxel_1"]),
                "context_id": "main",
                "tr": "2"
            }
            
            # Make the request
            response = client.post(
                Routes.GET_PREPROCESSED_TIMECOURSE.value,
                data=params,
                headers=form_content_type
            )
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == {"status": "success"}
            
            # Verify the mock calls
            mock_data_manager_ctx.get_viewer_data.assert_called_once_with(
                fmri_data=False,
                time_course_data=True,
                task_data=False
            )
            
            # Verify preprocess_timecourse was called with correct parameters
            mock_preprocess_timecourse.assert_called_once()
            call_args = mock_preprocess_timecourse.call_args[1]
            assert np.array_equal(call_args["timecourse_data"], mock_viewer_data["ts"]["voxel_1"])
            
            # Verify the preprocessed data was stored
            mock_data_manager_ctx.store_timecourse_preprocessed.assert_called_once()
    
    def test_get_preprocessed_timecourse_validation_error(self, client, mock_data_manager_ctx, form_content_type):
        """Test GET_PREPROCESSED_TIMECOURSE route with validation error."""
        # Mock TimecoursePreprocessInputValidator to raise PreprocessInputError
        with patch('findviz.routes.viewer.preprocess.TimecoursePreprocessInputValidator') as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator.validate_preprocess_input.side_effect = PreprocessInputError("Invalid timecourse input")
            mock_validator_class.return_value = mock_validator
            
            # Create input parameters - adding the missing 'filter' parameter
            params = {
                "standardize": "True",
                "detrend": "False",
                "normalize": "False",
                "mean_center": "False",
                "zscore": "False",
                "filter": "True",  # Add the missing filter parameter
                "high_cut": "invalid",  # Invalid value
                "low_cut": "0.1",
                "ts_labels": json.dumps(["voxel_1"]),
                "context_id": "main",
                "tr": "2"
            }
            
            # Make the request
            response = client.post(
                Routes.GET_PREPROCESSED_TIMECOURSE.value,
                data=params,
                headers=form_content_type
            )
            
            # Check the response - should be an error
            assert response.status_code == 400
            
            # Check that the response contains the expected error message as a string
            assert b'Invalid timecourse input' in response.data
            
            # Verify validator was called
            mock_validator.validate_preprocess_input.assert_called_once()
    
    def test_reset_fmri_preprocess(self, client, mock_data_manager_ctx, form_content_type):
        """Test RESET_FMRI_PREPROCESS route."""
        # Setup
        mock_data_manager_ctx.fmri_preprocessed = True
        
        # Make the request
        response = client.post(
            Routes.RESET_FMRI_PREPROCESS.value,
            data={"context_id": "main"},
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        
        # Verify clear_fmri_preprocessed was called
        mock_data_manager_ctx.clear_fmri_preprocessed.assert_called_once()
    
    def test_reset_timecourse_preprocess(self, client, mock_data_manager_ctx, form_content_type):
        """Test RESET_TIMECOURSE_PREPROCESS route."""
        # Setup
        mock_data_manager_ctx.ts_labels_preprocessed = ["voxel_1_preprocessed", "voxel_2_preprocessed"]
        
        # Create input parameters
        params = {
            "ts_labels": json.dumps(["voxel_1_preprocessed"]),
            "context_id": "main"
        }
        
        # Make the request
        response = client.post(
            Routes.RESET_TIMECOURSE_PREPROCESS.value,
            data=params,
            headers=form_content_type
        )
        
        # Check the response
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success"}
        
        # Verify clear_timecourse_preprocessed was called with the right labels
        mock_data_manager_ctx.clear_timecourse_preprocessed.assert_called_once_with(["voxel_1_preprocessed"])
    
    def test_reset_timecourse_preprocess_no_labels(self, client, mock_data_manager_ctx, form_content_type):
        """Test RESET_TIMECOURSE_PREPROCESS route with no timecourse labels."""
        # Setup
        mock_data_manager_ctx.ts_labels_preprocessed = ["voxel_1_preprocessed", "voxel_2_preprocessed"]
        
        # Create input parameters with empty labels list
        params = {
            "ts_labels": json.dumps([]),
            "context_id": "main"
        }
        
        # Make the request
        response = client.post(
            Routes.RESET_TIMECOURSE_PREPROCESS.value,
            data=params,
            headers=form_content_type
        )
        
        # Check the response - should be an error
        assert response.status_code == 400
        # Check the response contains the expected error message
        assert b"No timecourses selected" in response.data
    
    def test_reset_timecourse_preprocess_invalid_label(self, client, mock_data_manager_ctx, form_content_type):
        """Test RESET_TIMECOURSE_PREPROCESS route with invalid timecourse label."""
        # Setup
        mock_data_manager_ctx.ts_labels_preprocessed = ["voxel_1_preprocessed"]
        
        # Create input parameters with a label that doesn't exist in preprocessed data
        params = {
            "ts_labels": json.dumps(["voxel_2_preprocessed"]),  # This label isn't in ts_labels_preprocessed
            "context_id": "main"
        }
        
        # Make the request
        response = client.post(
            Routes.RESET_TIMECOURSE_PREPROCESS.value,
            data=params,
            headers=form_content_type
        )
        
        # Check the response - should be an error
        assert response.status_code == 400
        # Check that the response contains the expected error message as a string
        assert b"Timecourse voxel_2_preprocessed is not preprocessed" in response.data
