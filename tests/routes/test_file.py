import json
import io
import zipfile
import pytest
from unittest.mock import patch, MagicMock, mock_open

from findviz.viz.io.cache import Cache
from findviz.viz.io.timecourse import get_ts_header
from findviz.viz.io.upload import FileUpload
from findviz.viz import exception
from findviz.routes.utils import Routes


class TestFileRoutes:
    """Test suite for file.py routes"""

    def test_check_cache_no_cache(self, client, mocker):
        """Test check_cache route when no cache exists"""
        # Mock Cache.exists to return False
        mocker.patch.object(Cache, 'exists', return_value=False)
        
        # Make the request
        response = client.get(Routes.CHECK_CACHE.value)
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['has_cache'] is False

    def test_check_cache_with_cache(self, client, mocker):
        """Test check_cache route when cache exists"""
        # Mock cache data
        mock_cache_data = {
            'file_type': 'nifti',
            'some_key': 'some_value'
        }
        
        # Mock Cache methods
        mocker.patch.object(Cache, 'exists', return_value=True)
        mocker.patch.object(Cache, 'load', return_value=mock_cache_data)
        
        # Make the request
        response = client.get(Routes.CHECK_CACHE.value)
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['has_cache'] is True
        assert data['cache_data'] == mock_cache_data
        assert data['plot_type'] == 'nifti'

    def test_check_cache_with_error(self, client, mocker):
        """Test check_cache route when loading cache raises an error"""
        # Mock Cache methods
        mocker.patch.object(Cache, 'exists', return_value=True)
        mocker.patch.object(Cache, 'load', side_effect=Exception("Cache load error"))
        
        # Make the request
        response = client.get(Routes.CHECK_CACHE.value)
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['has_cache'] is False
        assert data['error'] == "Cache load error"

    def test_clear_cache_success(self, client, mocker):
        """Test clear_cache route with successful cache clearing"""
        # Mock Cache.clear
        mock_clear = mocker.patch.object(Cache, 'clear')
        
        # Make the request
        response = client.post(Routes.CLEAR_CACHE.value)
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        mock_clear.assert_called_once()

    def test_clear_cache_error(self, client, mocker):
        """Test clear_cache route when clearing cache raises an error"""
        # Mock Cache.clear to raise an exception
        mocker.patch.object(Cache, 'clear', side_effect=Exception("Clear cache error"))
        
        # Make the request
        response = client.post(Routes.CLEAR_CACHE.value)
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error'] == "Clear cache error"

    def test_get_header_success(self, client, mocker):
        """Test get_header route with successful header extraction"""
        # Mock file and header data
        mock_file = MagicMock()
        mock_file.filename = "test_file.csv"
        mock_header = 'column1'
        
        # Mock get_ts_header function
        mocker.patch('findviz.routes.file.get_ts_header', return_value=mock_header)
        
        # Create form data with file
        data = {
            'file_index': '0',
            'ts_file': (io.BytesIO(b"test data"), mock_file.filename, 'text/csv')
        }
        
        # Make the request
        response = client.post(Routes.GET_HEADER.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['header'] == mock_header

    def test_get_header_file_input_error(self, client, mocker):
        """Test get_header route with FileInputError"""
        # Mock file
        mock_file = MagicMock()
        mock_file.filename = "test_file.csv"
        
        # Create a FileInputError to be raised
        error = exception.FileInputError(
            "Invalid file input",
            exception.ExceptionFileTypes.TIMECOURSE.value,
            "cli",
            "ts_file",
            [0]
        )
        
        # Mock get_ts_header to raise the error
        mocker.patch('findviz.routes.file.get_ts_header', side_effect=error)
         
        # Create form data with file
        data = {
            'file_index': '0',
            'ts_file': (io.BytesIO(b"test data"), mock_file.filename, 'text/csv')
        }
        
        # Make the request
        response = client.post(Routes.GET_HEADER.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == "Invalid file input"
        assert response_data['file_type'] == exception.ExceptionFileTypes.TIMECOURSE.value
        assert response_data['fields'] == "ts_file"
        assert response_data['index'] == [0]

    def test_get_header_unexpected_error(self, client, mocker):
        """Test get_header route with unexpected error"""
        # Mock file
        mock_file = MagicMock()
        mock_file.filename = "test_file.csv"
        
        # Mock get_ts_header to raise an unexpected error
        mocker.patch('findviz.routes.file.get_ts_header', side_effect=Exception("Unexpected error"))
        
        # Create form data with file
        data = {
            'file_index': '0',
            'ts_file': (io.BytesIO(b"test data"), mock_file.filename, 'text/csv')
        }
        
        # Make the request
        response = client.post(Routes.GET_HEADER.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "unexpected error" in response_data['error'].lower()
        assert response_data['file_type'] is None
        assert response_data['fields'] is None
        assert response_data['index'] is None

    @pytest.mark.parametrize(
        "file_type,ts_input,task_input",
        [
            ("nifti", "true", "true"),
            ("gifti", "true", "false"),
            ("nifti", "false", "false"),
            ("gifti", "false", "true"),
        ],
    )
    def test_upload_success(self, client, mocker, mock_data_manager_ctx, file_type, ts_input, task_input):
        """Test upload route with successful file upload"""
        # Mock FileUpload.upload method
        mock_upload_result = {
            'nifti': MagicMock() if file_type == 'nifti' else None,
            'gifti': MagicMock() if file_type == 'gifti' else None,
            'ts': MagicMock(),
            'task': MagicMock() if task_input == 'true' else None
        }
        
        # Create form data
        data = {
            'fmri_file_type': file_type,
            'ts_input': ts_input,
            'task_input': task_input
        }
        
        # Mock upload method
        mocker.patch.object(FileUpload, 'upload', return_value=mock_upload_result)
        
        # Mock context methods
        if file_type == 'nifti':
            mock_data_manager_ctx.create_nifti_state.return_value = None
        else:
            mock_data_manager_ctx.create_gifti_state.return_value = None
            
        mock_data_manager_ctx.add_timeseries.return_value = None
        mock_data_manager_ctx.add_task_design.return_value = None
        
        # Mock get_viewer_metadata to return test data
        mock_viewer_metadata = {'key': 'value'}
        mock_data_manager_ctx.get_viewer_metadata.return_value = mock_viewer_metadata
        
        # Make the request
        response = client.post(Routes.UPLOAD_FILES.value, data=data)
        
        # Check response
        assert response.status_code == 201
        assert response.json == mock_viewer_metadata
        
        # Verify context methods were called
        if file_type == 'nifti':
            mock_data_manager_ctx.create_nifti_state.assert_called_once()
        else:
            mock_data_manager_ctx.create_gifti_state.assert_called_once()
        
        mock_data_manager_ctx.add_timeseries.assert_called_once()
        
        if task_input == 'true':
            mock_data_manager_ctx.add_task_design.assert_called_once()
        else:
            mock_data_manager_ctx.add_task_design.assert_not_called()

    def test_upload_file_input_error(self, client, mocker):
        """Test upload route with FileInputError"""
        # Create a FileInputError to be raised
        error = exception.FileInputError(
            "Missing required files",
            exception.ExceptionFileTypes.NIFTI.value,
            'cli',
            "func_nii",
            None
        )
        
        # Mock FileUpload.upload to raise the error
        mocker.patch.object(FileUpload, 'upload', side_effect=error)
        
        # Create form data
        data = {
            'fmri_file_type': 'nifti',
            'ts_input': 'false',
            'task_input': 'false'
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_FILES.value, data=data)
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == "Missing required files"
        assert response_data['file_type'] == exception.ExceptionFileTypes.NIFTI.value
        assert response_data['fields'] == "func_nii"
        assert response_data['index'] is None

    def test_upload_timecourse_error(self, client, mocker):
        """Test upload route with timecourse error"""
        # Create a FileValidationError for timecourse to be raised
        error = exception.FileValidationError(
            "Timecourse validation failed",
            'validate_timecourse',
            exception.ExceptionFileTypes.TIMECOURSE.value,
            "timecourse",
            [2]  # Index of the problematic timecourse file
        )
        
        # Mock FileUpload.upload to raise the error
        mocker.patch.object(FileUpload, 'upload', side_effect=error)
        
        # Create form data
        data = {
            'fmri_file_type': 'nifti',
            'ts_input': 'true',
            'task_input': 'false'
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_FILES.value, data=data)
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == "Timecourse validation failed"
        assert response_data['file_type'] == exception.ExceptionFileTypes.TIMECOURSE.value
        assert response_data['fields'] == "timecourse"
        assert response_data['index'] == [2]

    def test_upload_unexpected_error(self, client, mocker):
        """Test upload route with unexpected error"""
        # Mock FileUpload.upload to raise an unexpected error
        mocker.patch.object(FileUpload, 'upload', side_effect=Exception("Unexpected upload error"))
        
        # Create form data
        data = {
            'fmri_file_type': 'nifti',
            'ts_input': 'false',
            'task_input': 'false'
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_FILES.value, data=data)
        
        # Check response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "unexpected error" in response_data['error'].lower()
        assert response_data['file_type'] is None
        assert response_data['fields'] is None
        assert response_data['index'] is None

    def create_simple_zip(self):
        """Create a simple zip file for testing error cases"""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add some dummy content
            zipf.writestr('dummy.txt', 'This is just a dummy file for testing')
        zip_buffer.seek(0)
        return zip_buffer

    def test_upload_scene_success(self, client, mocker, mock_data_manager_ctx):
        """Test upload_scene route with successful scene upload"""
        # Create a simple dummy file - we'll mock the loading process
        dummy_data = io.BytesIO(b"dummy fvstate data")
        
        # Set up mock for data_manager.load
        # Instead of testing the whole deserialization process, we'll just mock it
        # This way we can test the route's behavior without needing real image data
        mocker.patch('findviz.routes.shared.data_manager.load')
        
        # Mock viewer metadata
        mock_viewer_metadata = {'key': 'value'}
        mock_data_manager_ctx.get_viewer_metadata.return_value = mock_viewer_metadata
        
        # Create data with file included
        data = {
            'scene_file': (dummy_data, 'scene.fvstate', 'application/octet-stream')
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_SCENE.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 200
        assert response.json == mock_viewer_metadata

    def test_upload_scene_no_file(self, client):
        """Test upload_scene route with no file provided"""
        # Make the request without a file
        response = client.post(Routes.UPLOAD_SCENE.value)
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "no scene file provided" in response_data['error'].lower()

    def test_upload_scene_empty_file(self, client):
        """Test upload_scene route with empty file"""
        # Create empty file data
        data = {
            'scene_file': (io.BytesIO(b""), '', 'application/octet-stream')
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_SCENE.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "empty file provided" in response_data['error'].lower()

    def test_upload_scene_invalid_extension(self, client):
        """Test upload_scene route with invalid file extension"""
        # Create a simple zip file with wrong extension
        zip_buffer = self.create_simple_zip()
        
        # Create file with invalid extension
        data = {
            'scene_file': (zip_buffer, 'scene.txt', 'application/zip')
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_SCENE.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "invalid file format" in response_data['error'].lower()

    def test_upload_scene_version_error(self, client, mocker):
        """Test upload_scene route with version incompatibility error"""
        # Create a simple zip file
        dummy_data = io.BytesIO(b"dummy fvstate data")
        
        # Mock data_manager.load to raise version error
        error = exception.FVStateVersionIncompatibleError(
            "Version incompatible", 
            '1.0', 
            '2.0'
        )
        mocker.patch('findviz.routes.shared.data_manager.load', side_effect=error)
        
        # Create file data
        data = {
            'scene_file': (dummy_data, 'scene.fvstate', 'application/octet-stream')
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_SCENE.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "version incompatible" in response_data['error'].lower()

    def test_upload_scene_general_error(self, client, mocker):
        """Test upload_scene route with general error"""
        # Create a simple dummy file
        dummy_data = io.BytesIO(b"dummy fvstate data")
        
        # Mock data_manager.load to raise generic error
        mocker.patch('findviz.routes.shared.data_manager.load', side_effect=Exception("General error"))
        
        # Create file data
        data = {
            'scene_file': (dummy_data, 'scene.fvstate', 'application/octet-stream')
        }
        
        # Make the request
        response = client.post(Routes.UPLOAD_SCENE.value, data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "general error" in response_data['error'].lower()
