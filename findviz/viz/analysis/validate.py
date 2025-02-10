"""
Validate parameters to analysis classes
"""

from typing import List

def validate_less_than_half_time_length(
    value: int, 
    time_length: int
) -> bool:
    """
    Validate value is less than half the time length
    """
    return abs(value) <= time_length / 2


def validate_less_than_or_equal_to_zero(value: int) -> bool:
    """
    Validate value is less than or equal to zero
    """
    return value <= 0

def validate_greater_than_or_equal_to_zero(value: int) -> bool:
    """
    Validate value is greater than or equal to zero
    """
    return value >= 0

