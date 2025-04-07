"""
Tests for findviz.viz.analysis.validate module
"""

import pytest
from findviz.viz.analysis.validate import (
    validate_less_than_half_time_length,
    validate_less_than_or_equal_to_zero,
    validate_greater_than_or_equal_to_zero
)


class TestValidateLessThanHalfTimeLength:
    """Test cases for validate_less_than_half_time_length function"""
    
    def test_positive_value_within_range(self):
        """Test with positive value within allowed range"""
        assert validate_less_than_half_time_length(5, 20) is True
        
    def test_negative_value_within_range(self):
        """Test with negative value within allowed range"""
        assert validate_less_than_half_time_length(-5, 20) is True
        
    def test_value_exactly_half(self):
        """Test with value exactly at half time length"""
        assert validate_less_than_half_time_length(10, 20) is True
        assert validate_less_than_half_time_length(-10, 20) is True
        
    def test_value_exceeds_half(self):
        """Test with value exceeding half time length"""
        assert validate_less_than_half_time_length(11, 20) is False
        assert validate_less_than_half_time_length(-11, 20) is False
        
    def test_zero_value(self):
        """Test with zero value"""
        assert validate_less_than_half_time_length(0, 20) is True
        
    def test_edge_cases(self):
        """Test edge cases"""
        # Time length of 0
        assert validate_less_than_half_time_length(0, 0) is True
        # Time length of 1
        assert validate_less_than_half_time_length(0, 1) is True
        assert validate_less_than_half_time_length(1, 1) is False


class TestValidateLessThanOrEqualToZero:
    """Test cases for validate_less_than_or_equal_to_zero function"""
    
    def test_negative_values(self):
        """Test with negative values"""
        assert validate_less_than_or_equal_to_zero(-1) is True
        assert validate_less_than_or_equal_to_zero(-100) is True
        
    def test_zero_value(self):
        """Test with zero value"""
        assert validate_less_than_or_equal_to_zero(0) is True
        
    def test_positive_values(self):
        """Test with positive values"""
        assert validate_less_than_or_equal_to_zero(1) is False
        assert validate_less_than_or_equal_to_zero(100) is False


class TestValidateGreaterThanOrEqualToZero:
    """Test cases for validate_greater_than_or_equal_to_zero function"""
    
    def test_positive_values(self):
        """Test with positive values"""
        assert validate_greater_than_or_equal_to_zero(1) is True
        assert validate_greater_than_or_equal_to_zero(100) is True
        
    def test_zero_value(self):
        """Test with zero value"""
        assert validate_greater_than_or_equal_to_zero(0) is True
        
    def test_negative_values(self):
        """Test with negative values"""
        assert validate_greater_than_or_equal_to_zero(-1) is False
        assert validate_greater_than_or_equal_to_zero(-100) is False
