import pytest
import json
import numpy as np
from unittest.mock import patch, MagicMock
from flask import request, make_response

from findviz.routes.utils import (
    Routes, 
    convert_value, 
    handle_context, 
    handle_route_errors,
    is_numeric,
    sanitize_array_for_json,
    str_to_float_list
)
from findviz.viz.exception import DataRequestError


class TestUtils:
    """Test suite for utility functions in routes/utils.py"""

    def test_routes_enum(self):
        """Test that Routes enum contains expected values"""
        assert Routes.CHECK_CACHE.value == '/check_cache'
        assert Routes.UPLOAD_FILES.value == '/upload'
        assert Routes.UPLOAD_SCENE.value == '/upload_scene'
        assert Routes.GET_HEADER.value == '/get_header'

    @pytest.mark.parametrize(
        "input_value,expected_output",
        [
            # Boolean conversions
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            (True, True),
            (False, False),
            
            # None/null conversions
            ('null', None),
            ('none', None),
            ('None', None),
            ('NONE', None),
            ('NULL', None),
            ('', None),
            
            # Integer conversions
            ('123', 123),
            ('-456', -456),
            ('0', 0),
            
            # Float conversions
            ('123.45', 123.45),
            ('-456.78', -456.78),
            ('0.0', 0.0),
            
            # Non-convertible strings
            ('hello', 'hello'),
            ('123abc', '123abc'),
            ('true_value', 'true_value'),
        ]
    )
    def test_convert_value(self, input_value, expected_output):
        """Test conversion of various input types"""
        assert convert_value(input_value) == expected_output
    
    def test_handle_context_success(self, app, mocker):
        """Test handle_context decorator with valid context ID"""
        # Create a mock for data_manager.switch_context
        mock_switch_context = mocker.patch('findviz.routes.utils.data_manager.switch_context')
        
        # Create a function decorated with handle_context
        @handle_context()
        def test_route():
            return {'success': True}
        
        # Create a test request context with a context_id query parameter
        with app.test_request_context('/?context_id=test_context'):
            # Call the decorated function
            result = test_route()
            
            # Check that switch_context was called with the correct context_id
            mock_switch_context.assert_called_once_with('test_context')
            
            # Check that the decorated function's return value is preserved
            assert result == {'success': True}
    
    def test_handle_context_form_data(self, app, mocker):
        """Test handle_context decorator with context ID in form data"""
        # Create a mock for data_manager.switch_context
        mock_switch_context = mocker.patch('findviz.routes.utils.data_manager.switch_context')
        
        # Create a function decorated with handle_context
        @handle_context()
        def test_route():
            return {'success': True}
        
        # Create a test request context with context_id in form data
        with app.test_request_context('/', method='POST', data={'context_id': 'test_context'}):
            # Call the decorated function
            result = test_route()
            
            # Check that switch_context was called with the correct context_id
            mock_switch_context.assert_called_once_with('test_context')
            
            # Check that the decorated function's return value is preserved
            assert result == {'success': True}
    
    def test_handle_context_error(self, app, mocker):
        """Test handle_context decorator with invalid context ID"""
        # Create a mock for data_manager.switch_context that raises ValueError
        mock_switch_context = mocker.patch(
            'findviz.routes.utils.data_manager.switch_context',
            side_effect=ValueError("Invalid context")
        )
        
        # Create a function decorated with handle_context
        @handle_context()
        def test_route():
            return {'success': True}
        
        # Create a test request context with an invalid context_id
        with app.test_request_context('/?context_id=invalid_context'):
            # Call the decorated function
            response = test_route()
            
            # Check that the response is an error response
            assert response.status_code == 400
            assert json.loads(response.data)['error'] == "Invalid context"
    
    def test_handle_route_errors_success(self, app, mocker):
        """Test handle_route_errors decorator with successful execution"""
        # Create a function decorated with handle_route_errors
        @handle_route_errors(
            error_msg="Test error",
            log_msg="Test success",
            fmri_file_type="nifti",
            route=Routes.GET_HEADER
        )
        def test_route():
            return {'success': True}
        
        # Create a test request context
        with app.test_request_context('/'):
            # Mock logger
            mock_logger = mocker.patch('findviz.routes.utils.logger')
            
            # Call the decorated function
            response = test_route()
            
            # Check that the response is successful
            assert response.status_code == 200
            assert json.loads(response.data) == {'success': True}
            
            # Check that success was logged
            mock_logger.info.assert_called_once_with("Test success")
    
    def test_handle_route_errors_missing_param(self, app, mocker):
        """Test handle_route_errors decorator with missing required parameter"""
        # Create a function decorated with handle_route_errors
        @handle_route_errors(
            error_msg="Missing parameter",
            fmri_file_type="nifti",
            route=Routes.GET_HEADER,
            route_parameters=['required_param']
        )
        def test_route():
            return {'success': True}
        
        # Create a test request context without the required parameter
        with app.test_request_context('/'):
            # Mock logger
            mock_logger = mocker.patch('findviz.routes.utils.logger')
            
            # Call the decorated function
            response = test_route()
            
            # Check that the response is an error response
            assert response.status_code == 400
            assert "Missing parameter" in response.data.decode()
    
    def test_handle_route_errors_custom_exception(self, app, mocker):
        """Test handle_route_errors decorator with custom exception handling"""
        # Create a function decorated with handle_route_errors that raises a custom exception
        @handle_route_errors(
            error_msg="Custom exception",
            fmri_file_type="nifti",
            route=Routes.GET_HEADER,
            custom_exceptions=[DataRequestError]
        )
        def test_route():
            raise DataRequestError(
                message="Test error message",
                fmri_file_type="nifti",
                route="/test",
                input_field="test_field"
            )
        
        # Create a test request context
        with app.test_request_context('/'):
            # Mock logger
            mock_logger = mocker.patch('findviz.routes.utils.logger')
            
            # Call the decorated function
            response = test_route()
            
            # Check that the response is a custom error response
            assert response.status_code == 400
            error_data = json.loads(response.data)
            assert error_data['error'] == "Test error message"
            assert error_data['type'] == "DataRequestError"
    
    def test_handle_route_errors_unexpected_exception(self, app, mocker):
        """Test handle_route_errors decorator with unexpected exception"""
        # Create a function decorated with handle_route_errors that raises an unexpected exception
        @handle_route_errors(
            error_msg="Unexpected error",
            fmri_file_type="nifti",
            route=Routes.GET_HEADER
        )
        def test_route():
            raise ValueError("Something went wrong")
        
        # Create a test request context
        with app.test_request_context('/'):
            # Mock logger
            mock_logger = mocker.patch('findviz.routes.utils.logger')
            
            # Call the decorated function
            response = test_route()
            
            # Check that the response is an error response
            assert response.status_code == 500
            error_data = json.loads(response.data)
            assert error_data['error'] == "Unexpected error"
            assert error_data['details'] == "Something went wrong"
            
            # Check that the error was logged as critical
            mock_logger.critical.assert_called_once()
    
    def test_handle_route_errors_callable_file_type(self, app, mocker):
        """Test handle_route_errors decorator with callable file_type"""
        # Create a callable that returns the file type
        def get_file_type():
            return "dynamic_file_type"
        
        # Create a function decorated with handle_route_errors using a callable file_type
        @handle_route_errors(
            error_msg="Error with dynamic file type",
            fmri_file_type=get_file_type,
            route=Routes.GET_HEADER
        )
        def test_route():
            raise ValueError("Test error")
        
        # Create a test request context
        with app.test_request_context('/'):
            # Mock logger
            mock_logger = mocker.patch('findviz.routes.utils.logger')
            
            # Call the decorated function
            response = test_route()
            
            # Check that the response includes the dynamically determined file type
            error_data = json.loads(response.data)
            assert error_data['context']['file_type'] == "dynamic_file_type"
    
    @pytest.mark.parametrize(
        "input_value,expected_output",
        [
            ('123', True),
            ('123.45', True),
            ('-456', True),
            ('-456.78', True),
            ('0', True),
            ('0.0', True),
            ('abc', False),
            ('123abc', False),
            ('', False),
            (None, False),
        ]
    )
    def test_is_numeric(self, input_value, expected_output):
        """Test is_numeric function with various inputs"""
        assert is_numeric(input_value) == expected_output
    
    def test_sanitize_array_for_json(self):
        """Test sanitize_array_for_json function with NaN values"""
        # Create a NumPy array with NaN values
        test_array = np.array([
            [1.0, 2.0, np.nan],
            [np.nan, 5.0, 6.0],
            [7.0, np.nan, 9.0]
        ])
        
        # Expected output with None instead of NaN
        expected_output = [
            [1.0, 2.0, None],
            [None, 5.0, 6.0],
            [7.0, None, 9.0]
        ]
        
        # Test the function
        result = sanitize_array_for_json(test_array)
        assert result == expected_output
    
    @pytest.mark.parametrize(
        "input_string,expected_output",
        [
            ('1,2,3', [1.0, 2.0, 3.0]),
            ('1.5,2.5,3.5', [1.5, 2.5, 3.5]),
            ('-1,-2,-3', [-1.0, -2.0, -3.0]),
            ('0', [0.0]),
            ('', []),
        ]
    )
    def test_str_to_float_list(self, input_string, expected_output):
        """Test str_to_float_list function with various inputs"""
        if input_string == '':
            # Special case for empty string, which will raise a ValueError
            with pytest.raises(ValueError):
                str_to_float_list(input_string)
        else:
            assert str_to_float_list(input_string) == expected_output
