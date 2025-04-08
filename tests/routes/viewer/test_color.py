import pytest
import json
from unittest.mock import patch, MagicMock

from findviz.routes.utils import Routes
from findviz.viz.viewer.state.components import ColorMaps


@pytest.mark.usefixtures("mock_data_manager_ctx")
class TestColorRoutes:
    """Test class for the color.py routes."""
    
    def test_get_colormaps(self, client, mock_data_manager_ctx):
        """Test GET_COLORMAPS route."""
        # Define expected result with a mock colormap
        expected_data = {
            "Viridis": {
                "label": "Viridis",
                "gradient": "linear-gradient(to right, rgb(68,1,84), rgb(72,40,120), rgb(62,74,137), rgb(49,104,142), rgb(38,130,142), rgb(31,158,137), rgb(53,183,121), rgb(110,206,88), rgb(181,222,43), rgb(253,231,37))"
            }
        }
        
        # Mock the generate_colormap_data function
        with patch('findviz.routes.viewer.color.generate_colormap_data') as mock_generate:
            mock_generate.return_value = expected_data
            
            # Make the request with context_id
            response = client.get(Routes.GET_COLORMAPS.value + "?context_id=main")
            
            # Check the response
            assert response.status_code == 200
            assert json.loads(response.data) == expected_data
            # Verify the function was called with ColorMaps
            mock_generate.assert_called_once_with(ColorMaps)
    
    def test_generate_colormap_data(self):
        """Test generate_colormap_data function."""
        # Create a mock Enum for testing
        mock_colormaps = MagicMock()
        mock_colormaps.value = "Viridis"
        
        # Mock plotly.colors.get_colorscale to return known values
        with patch('plotly.colors.get_colorscale') as mock_get_colorscale:
            # Sample colorscale with position and color code
            mock_get_colorscale.return_value = [
                (0, 'rgb(68,1,84)'),
                (1, 'rgb(253,231,37)')
            ]
            
            # Import the function to test
            from findviz.routes.viewer.color import generate_colormap_data
            
            # Call the function
            result = generate_colormap_data([mock_colormaps])
            
            # Verify the result structure
            assert "Viridis" in result
            assert "label" in result["Viridis"]
            assert "gradient" in result["Viridis"]
            assert result["Viridis"]["label"] == "Viridis"
            assert "linear-gradient(to right, rgb(68,1,84), rgb(253,231,37))" == result["Viridis"]["gradient"]
            
            # Verify the plotly function was called with the right parameter
            mock_get_colorscale.assert_called_once_with("Viridis")
    
    def test_code_to_rgb_hex(self):
        """Test code_to_rgb function with hex color code."""
        # Import the function to test
        from findviz.routes.viewer.color import code_to_rgb
        
        # Mock plotly.colors.hex_to_rgb to return known values
        with patch('plotly.colors.hex_to_rgb') as mock_hex_to_rgb:
            mock_hex_to_rgb.return_value = (255, 0, 0)
            
            # Test with hex color code
            result = code_to_rgb('#FF0000')
            
            # Verify the result
            assert result == (255, 0, 0)
            mock_hex_to_rgb.assert_called_once_with('#FF0000')
    
    def test_code_to_rgb_rgb(self):
        """Test code_to_rgb function with rgb color code."""
        # Import the function to test
        from findviz.routes.viewer.color import code_to_rgb
        
        # Test with rgb color code
        result = code_to_rgb('rgb(255,0,0)')
        
        # Verify the result
        assert result == [255, 0, 0]
        
        # Test with additional spaces
        result = code_to_rgb('rgb(255, 0, 0)')
        
        # Verify the result
        assert result == [255, 0, 0]
