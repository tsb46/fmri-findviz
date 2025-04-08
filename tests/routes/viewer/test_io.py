import pytest
import io
from unittest.mock import patch, MagicMock

from findviz.routes.utils import Routes


@pytest.mark.usefixtures("mock_data_manager_ctx")
class TestIORoutes:
    """Test class for the io.py routes."""
    
    def test_save_scene(self, client, mock_data_manager_ctx):
        """Test SAVE_SCENE route."""
        # Create mock serialized data
        mock_serialized_data = b'mock_serialized_scene_data'
        
        # Mock the data_manager.save() method
        with patch('findviz.routes.shared.data_manager.save') as mock_save:
            mock_save.return_value = mock_serialized_data
            
            # Make the request
            response = client.post(Routes.SAVE_SCENE.value)
            
            # Check the response status code
            assert response.status_code == 200
            
            # Verify the content type
            assert response.content_type == 'application/octet-stream'
            
            # Check that the response data matches our mock data
            assert response.data == mock_serialized_data
            
            # Verify headers to prevent caching
            assert response.headers["Cache-Control"] == "no-cache, no-store, must-revalidate"
            assert response.headers["Pragma"] == "no-cache"
            assert response.headers["Expires"] == "0"
            
            # Verify the attachment filename
            assert response.headers["Content-Disposition"] == "attachment; filename=scene"
            
            # Verify the data_manager.save() method was called
            mock_save.assert_called_once()
    
    def test_save_scene_error(self, client, mock_data_manager_ctx):
        """Test SAVE_SCENE route when an error occurs."""
        # Mock the data_manager.save() method to raise an exception
        with patch('findviz.routes.shared.data_manager.save') as mock_save:
            mock_save.side_effect = Exception("Error saving scene")
            
            # Make the request and expect an error response
            with pytest.raises(Exception, match="Error saving scene"):
                client.post(Routes.SAVE_SCENE.value)
            
            # Verify the data_manager.save() method was called
            mock_save.assert_called_once()
