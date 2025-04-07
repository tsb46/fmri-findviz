"""Tests for the DataManager singleton class."""

import pytest
from unittest.mock import Mock, patch

from findviz.viz.viewer.data_manager import DataManager
from findviz.viz.viewer.context import VisualizationContext
from findviz.viz.viewer.state.state_file import StateFile
from findviz.viz import exception

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    DataManager._instance = None
    yield

def test_singleton_pattern():
    """Test that DataManager implements singleton pattern correctly."""
    dm1 = DataManager()
    dm2 = DataManager()
    assert dm1 is dm2
    assert DataManager._instance is dm1

def test_initial_state():
    """Test initial state of DataManager."""
    dm = DataManager()
    # Should have a main context by default
    assert "main" in dm._contexts
    assert dm._active_context_id == "main"
    assert isinstance(dm.ctx, VisualizationContext)

def test_ctx_property():
    """Test the ctx property returns the active context."""
    dm = DataManager()
    assert dm.ctx is dm._contexts["main"]
    
    # Create a new context and switch to it
    dm._contexts["test"] = VisualizationContext("test")
    dm._active_context_id = "test"
    assert dm.ctx is dm._contexts["test"]

def test_create_analysis_context():
    """Test creating a new analysis context."""
    dm = DataManager()
    context_id = dm.create_analysis_context("test_analysis")
    
    assert context_id == "test_analysis"
    assert context_id in dm._contexts
    assert isinstance(dm._contexts[context_id], VisualizationContext)
    assert dm._contexts[context_id].context_id == context_id

def test_get_context():
    """Test getting a context by ID."""
    dm = DataManager()
    
    # Get the main context
    context = dm.get_context("main")
    assert context is dm._contexts["main"]
    
    # Try to get a non-existent context
    with pytest.raises(ValueError, match="Context nonexistent does not exist"):
        dm.get_context("nonexistent")

def test_get_context_ids():
    """Test getting all context IDs."""
    dm = DataManager()
    
    # Should have main context by default
    assert dm.get_context_ids() == ["main"]
    
    # Add a new context
    dm._contexts["test"] = VisualizationContext("test")
    assert set(dm.get_context_ids()) == {"main", "test"}

def test_get_active_context_id():
    """Test getting the active context ID."""
    dm = DataManager()
    assert dm.get_active_context_id() == "main"
    
    # Change the active context
    dm._active_context_id = "test"
    assert dm.get_active_context_id() == "test"

def test_switch_context():
    """Test switching between contexts."""
    dm = DataManager()
    
    # Create a new context
    dm._contexts["test"] = VisualizationContext("test")
    
    # Switch to the new context
    dm.switch_context("test")
    assert dm._active_context_id == "test"
    
    # Switch back to main
    dm.switch_context("main")
    assert dm._active_context_id == "main"
    
    # Try to switch to a non-existent context
    with pytest.raises(ValueError, match="Context nonexistent does not exist"):
        dm.switch_context("nonexistent")

@patch.object(StateFile, 'deserialize_from_bytes')
def test_load(mock_deserialize):
    """Test loading a state file."""
    dm = DataManager()
    
    # Create a mock context
    mock_context = Mock(spec=VisualizationContext)
    mock_context.context_id = "loaded_context"
    mock_deserialize.return_value = mock_context
    
    # Load the mock context
    dm.load(b"mock_data")
    
    # Verify the context was loaded
    mock_deserialize.assert_called_once_with(b"mock_data")
    assert dm._contexts["main"] is mock_context
    
    # Test error handling
    mock_deserialize.side_effect = ValueError("Test error")
    with pytest.raises(ValueError, match="Test error"):
        dm.load(b"mock_data")
    
    # Test version incompatibility error
    mock_deserialize.side_effect = exception.FVStateVersionIncompatibleError(
        "Test version error", "1.0", "2.0"
    )
    with pytest.raises(exception.FVStateVersionIncompatibleError):
        dm.load(b"mock_data")

@patch.object(StateFile, 'serialize_to_bytes')
def test_save(mock_serialize):
    """Test saving a state file."""
    dm = DataManager()
    mock_serialize.return_value = b"serialized_data"
    
    # Save the current context
    result = dm.save("test.fvstate")
    
    # Verify the context was serialized
    mock_serialize.assert_called_once()
    assert mock_serialize.call_args[0][0] is dm._contexts["main"]
    assert result == b"serialized_data"