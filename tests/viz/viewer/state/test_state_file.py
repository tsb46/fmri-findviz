"""Tests for the state file module."""

import io
import json
import zipfile
import datetime
import tempfile
import os
from pathlib import Path

import pytest
import numpy as np
import nibabel as nib
from unittest.mock import patch, MagicMock, mock_open

from findviz.viz.viewer.state.state_file import StateFile
from findviz.viz.viewer.context import VisualizationContext
from findviz.viz.viewer.state.viz_state import NiftiVisualizationState, GiftiVisualizationState
from findviz.viz.viewer.state.components import (
    ColorMaps,
    FmriPlotOptions, 
    TimeCoursePlotOptions,
    TimeCourseColor,
    TaskDesignPlotOptions
)
from findviz.viz.exception import FVStateVersionIncompatibleError

@pytest.fixture
def mock_nifti_context():
    """Create a mock NIFTI context with basic state."""
    context = VisualizationContext('test_nifti')
    context._state = NiftiVisualizationState(
        tr=2.0,
        timepoints=[0, 1, 2, 3],
        timepoints_seconds=[0.0, 2.0, 4.0, 6.0],
        global_min=-1.0,
        global_max=1.0,
        timepoint=2
    )
    return context

@pytest.fixture
def mock_gifti_context():
    """Create a mock GIFTI context with basic state."""
    context = VisualizationContext('test_gifti')
    context._state = GiftiVisualizationState(
        tr=2.0,
        timepoints=[0, 1, 2, 3],
        global_min=-1.0,
        global_max=1.0,
        timepoint=2,
        left_input=True,
        right_input=True
    )
    return context

@pytest.fixture
def mock_nifti_image():
    """Create a properly mocked Nifti1Image for testing."""
    mock_img = MagicMock(spec=nib.Nifti1Image)
    # Make get_fdata return a numpy array with proper dimensions (3D+time)
    mock_img.get_fdata.return_value = np.zeros((10, 10, 10, 4))
    # Set header and affine properties
    mock_img.header = MagicMock(spec=nib.Nifti1Header)
    mock_img.affine = np.eye(4)
    # Mock to_bytes for serialization
    mock_img.to_bytes.return_value = b'mock_nifti_bytes'
    return mock_img

@pytest.fixture
def mock_gifti_image():
    """Create a properly mocked GiftiImage for testing."""
    mock_img = MagicMock(spec=nib.gifti.GiftiImage)
    # Create mock darrays
    mock_darray1 = MagicMock()
    mock_darray1.data = np.zeros(100)
    mock_darray2 = MagicMock()
    mock_darray2.data = np.ones(100)
    # Set darrays
    mock_img.darrays = [mock_darray1, mock_darray2]
    # Mock to_bytes for serialization
    mock_img.to_bytes.return_value = b'mock_gifti_bytes'
    return mock_img

def test_serialize_state_basic(mock_nifti_context):
    """Test basic state serialization."""
    # Serialize the state
    state_dict = StateFile._serialize_state(mock_nifti_context._state)
    
    # Check that basic properties were serialized correctly
    assert state_dict['tr'] == 2.0
    assert state_dict['timepoints']['__type__'] == 'list'
    assert state_dict['timepoints']['values'] == [0, 1, 2, 3]
    assert state_dict['timepoints_seconds']['__type__'] == 'list'
    assert state_dict['timepoints_seconds']['values'] == [0.0, 2.0, 4.0, 6.0]
    assert state_dict['global_min'] == -1.0
    assert state_dict['global_max'] == 1.0
    assert state_dict['timepoint'] == 2
    assert state_dict['file_type'] == 'nifti'

def test_serialize_state_with_numpy_arrays(mock_nifti_context):
    """Test serialization of state with numpy arrays."""
    # Add numpy arrays to the state
    mock_nifti_context._state.numpy_data = np.array([1.0, 2.0, 3.0])
    
    # Serialize the state
    state_dict = StateFile._serialize_state(mock_nifti_context._state)
    
    # Check that numpy arrays were serialized correctly
    assert state_dict['numpy_data']['__type__'] == 'numpy_array'
    assert state_dict['numpy_data']['values'] == [1.0, 2.0, 3.0]

def test_serialize_state_with_sets(mock_nifti_context):
    """Test serialization of state with sets."""
    # Add a set to the state
    mock_nifti_context._state.used_colors = {TimeCourseColor.RED, TimeCourseColor.BLUE}
    
    # Serialize the state
    state_dict = StateFile._serialize_state(mock_nifti_context._state)
    
    # Check that sets were serialized correctly
    assert state_dict['used_colors']['__type__'] == 'set'
    assert state_dict['used_colors']['__item_type__'] == 'TimeCourseColor'
    assert set(state_dict['used_colors']['values']) == {'red', 'blue'}

def test_serialize_state_with_nested_structures(mock_nifti_context):
    """Test serialization of state with nested structures."""
    # Add nested structures to the state
    mock_nifti_context._state.ts_data = {
        'ROI1': np.array([1.0, 2.0, 3.0]),
        'ROI2': np.array([3.0, 2.0, 1.0])
    }
    
    # Serialize the state
    state_dict = StateFile._serialize_state(mock_nifti_context._state)
    
    # Check that nested structures were serialized correctly
    assert state_dict['ts_data']['__type__'] == 'dict'
    assert 'ROI1' in state_dict['ts_data']['values']
    assert 'ROI2' in state_dict['ts_data']['values']

def test_serialize_list():
    """Test serialization of lists."""
    # Create a list with various types
    test_list = [
        1, 
        "string", 
        np.array([1.0, 2.0, 3.0]), 
        [4, 5, 6], 
        {'key': 'value'}
    ]
    
    # Serialize the list
    serialized = StateFile._serialize_list(test_list)
    
    # Check that the list was serialized correctly
    assert serialized[0] == 1
    assert serialized[1] == "string"
    assert serialized[2]['__type__'] == 'numpy_array'
    assert serialized[2]['values'] == [1.0, 2.0, 3.0]
    assert serialized[3]['__type__'] == 'list'
    assert serialized[3]['values'] == [4, 5, 6]
    assert serialized[4]['__type__'] == 'dict'
    assert serialized[4]['values'] == {'key': 'value'}

def test_serialize_dict():
    """Test serialization of dictionaries."""
    # Create a dictionary with various types
    test_dict = {
        'int': 1,
        'string': "string",
        'array': np.array([1.0, 2.0, 3.0]),
        'list': [4, 5, 6],
        'dict': {'nested': 'value'}
    }
    
    # Serialize the dictionary
    serialized = StateFile._serialize_dict(test_dict)
    
    # Check that the dictionary was serialized correctly
    assert serialized['int'] == 1
    assert serialized['string'] == "string"
    assert serialized['array'] == [1.0, 2.0, 3.0]  # Arrays in dicts are converted to lists
    assert serialized['list'] == [4, 5, 6]
    assert serialized['dict'] == {'nested': 'value'}

def test_deserialize_list():
    """Test deserialization of lists."""
    # Create a serialized list
    serialized = [
        1,
        "string",
        {'__type__': 'numpy_array', 'values': [1.0, 2.0, 3.0]},
        {'__type__': 'list', 'values': [4, 5, 6]},
        {'__type__': 'dict', 'values': {'key': 'value'}}
    ]
    
    # Deserialize the list
    deserialized = StateFile._deserialize_list(serialized)
    
    # Check that the list was deserialized correctly
    assert deserialized[0] == 1
    assert deserialized[1] == "string"
    assert isinstance(deserialized[2], np.ndarray)
    assert np.array_equal(deserialized[2], np.array([1.0, 2.0, 3.0]))
    assert deserialized[3] == [4, 5, 6]
    assert deserialized[4] == {'key': 'value'}

def test_deserialize_dict():
    """Test deserialization of dictionaries."""
    # Create a serialized dictionary
    serialized = {
        'int': 1,
        'string': "string",
        'array': {'__type__': 'numpy_array', 'values': [1.0, 2.0, 3.0]},
        'list': {'__type__': 'list', 'values': [4, 5, 6]},
        'dict': {'__type__': 'dict', 'values': {'nested': 'value'}}
    }
    
    # Deserialize the dictionary
    deserialized = StateFile._deserialize_dict(serialized)
    
    # Check that the dictionary was deserialized correctly
    assert deserialized['int'] == 1
    assert deserialized['string'] == "string"
    assert isinstance(deserialized['array'], np.ndarray)
    assert np.array_equal(deserialized['array'], np.array([1.0, 2.0, 3.0]))
    assert deserialized['list'] == [4, 5, 6]
    assert deserialized['dict'] == {'nested': 'value'}


def test_apply_state_dict():
    """Test applying a state dictionary to a state object."""
    # Create a state object
    state = NiftiVisualizationState()
    
    # Create a state dictionary
    state_dict = {
        'tr': 2.0,
        'timepoints': [0, 1, 2, 3],
        'global_min': -1.0,
        'global_max': 1.0,
        'timepoint': 2,
        'fmri_plot_options': {
            'color_min': -2.0,
            'color_max': 2.0,
            'color_map': 'Viridis'
        },
        'ts_plot_options': {
            'ROI1': {
                'label': 'ROI1',
                'color': 'red',
                'width': 2.0,
                'opacity': 1.0,
                'mode': 'lines',
                'constant': [0.0, 1.0, 2.0],
                'scale': [1.0, 1.1, 1.2]
            }
        },
        'task_plot_options': {
            'cond1': {
                'label': 'cond1',
                'convolution': 'hrf',
                'color': 'blue',
                'width': 2.0,
                'opacity': 1.0,
                'mode': 'lines',
                'constant': [0.0],
                'scale': [1.0]
            }
        },
        'distance_data': {'__type__': 'numpy_array', 'values': [1.0, 2.0, 3.0]},
        'used_colors': {'__type__': 'set', '__item_type__': 'TimeCourseColor', 'values': ['red', 'blue']}
    }
    
    # Apply the state dictionary
    StateFile._apply_state_dict(state, state_dict)
    
    # Check that the state was updated correctly
    assert state.tr == 2.0
    assert state.timepoints == [0, 1, 2, 3]
    assert state.global_min == -1.0
    assert state.global_max == 1.0
    assert state.timepoint == 2
    
    # Check plot options
    assert state.fmri_plot_options.color_min == -2.0
    assert state.fmri_plot_options.color_max == 2.0
    assert state.fmri_plot_options.color_map.value == 'Viridis'
    
    # Check time course options
    assert 'ROI1' in state.ts_plot_options
    assert state.ts_plot_options['ROI1'].label == 'ROI1'
    assert state.ts_plot_options['ROI1'].color.value == 'red'
    assert state.ts_plot_options['ROI1'].width == 2.0
    assert state.ts_plot_options['ROI1'].constant.shift_history == [0.0, 1.0, 2.0]
    assert state.ts_plot_options['ROI1'].scale.scale_history == [1.0, 1.1, 1.2]
    
    # Check task options
    assert 'cond1' in state.task_plot_options
    assert state.task_plot_options['cond1'].label == 'cond1'
    assert state.task_plot_options['cond1'].convolution == 'hrf'
    assert state.task_plot_options['cond1'].color.value == 'blue'
    
    # Check sets
    assert isinstance(state.used_colors, set)
    assert TimeCourseColor.RED in state.used_colors
    assert TimeCourseColor.BLUE in state.used_colors

def test_integration_serialize_deserialize(mock_nifti_image):
    """Integration test for serializing and deserializing state."""
    # Create a context with state
    context = VisualizationContext('test_nifti')
    context._state = NiftiVisualizationState(
        tr=2.0,
        timepoints=[0, 1, 2, 3],
        global_min=-1.0,
        global_max=1.0,
        timepoint=2
    )
    
    # Add some plot options
    context._state.fmri_plot_options.color_min = -2.0
    context._state.fmri_plot_options.color_max = 2.0
    context._state.fmri_plot_options.color_map = ColorMaps.VIRIDIS
    
    # Add some time course data
    context._state.ts_enabled = True
    context._state.ts_data = {
        'ROI1': np.array([1.0, 2.0, 3.0])
    }
    context._state.ts_labels = ['ROI1']
    context._state.ts_type = {'ROI1': 'user'}
    context._state.ts_plot_options = {
        'ROI1': TimeCoursePlotOptions(label='ROI1')
    }
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.fvstate', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Serialize the state
        with patch.object(nib.Nifti1Image, 'to_bytes', return_value=b'mock_bytes'):
            # Mock the nifti data
            context._state.nifti_data = {
                'func_img': mock_nifti_image
            }
            
            # Serialize to bytes
            state_bytes = StateFile.serialize_to_bytes(context)
            
            # Write bytes to file
            with open(temp_path, 'wb') as f:
                f.write(state_bytes)
        
        # Deserialize from file
        with open(temp_path, 'rb') as f:
            loaded_bytes = f.read()
            
            with patch.object(nib.Nifti1Image, 'from_bytes', return_value=mock_nifti_image):
                loaded_context = StateFile.deserialize_from_bytes(loaded_bytes)
        
        # Check that the loaded state matches the original
        assert loaded_context._state.tr == 2.0
        assert loaded_context._state.timepoints == [0, 1, 2, 3]
        assert loaded_context._state.global_min == -1.0
        assert loaded_context._state.global_max == 1.0
        assert loaded_context._state.timepoint == 2
        assert loaded_context._state.file_type == 'nifti'
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_serialize_to_bytes_nifti(mock_nifti_context):
    """Test serializing NIFTI state to bytes."""
    # Add some data to the context
    mock_nifti_context._state.nifti_data = {
        'func_img': MagicMock(spec=nib.Nifti1Image)
    }
    mock_nifti_context._state.nifti_data['func_img'].to_bytes = MagicMock(return_value=b'mock_bytes')
    
    # Serialize the state
    with patch.object(nib.Nifti1Image, 'to_bytes', return_value=b'mock_bytes'):
        state_bytes = StateFile.serialize_to_bytes(mock_nifti_context)
    
    # Check that we got bytes back
    assert isinstance(state_bytes, bytes)
    
    # Check that the bytes contain a valid ZIP file
    buffer = io.BytesIO(state_bytes)
    with zipfile.ZipFile(buffer, 'r') as zipf:
        # Check that the expected files are in the ZIP
        file_list = zipf.namelist()
        assert 'manifest.json' in file_list
        assert 'state.json' in file_list
        
        # Check the manifest
        manifest = json.loads(zipf.read('manifest.json').decode('utf-8'))
        assert manifest['format_version'] == StateFile.FORMAT_VERSION
        assert 'state.json' in manifest['files']
        assert manifest['metadata']['context_id'] == 'test_nifti'
        assert manifest['metadata']['file_type'] == 'nifti'
        
        # Check the state
        state = json.loads(zipf.read('state.json').decode('utf-8'))
        assert state['file_type'] == 'nifti'
        assert state['tr'] == 2.0

def test_serialize_to_bytes_gifti(mock_gifti_context):
    """Test serializing GIFTI state to bytes."""
    # Add some data to the context
    mock_gifti_context._state.gifti_data = {
        'left_func': MagicMock(spec=nib.gifti.GiftiImage)
    }
    mock_gifti_context._state.gifti_data['left_func'].to_bytes = MagicMock(return_value=b'mock_bytes')
    
    # Serialize the state
    with patch.object(nib.gifti.GiftiImage, 'to_bytes', return_value=b'mock_bytes'):
        state_bytes = StateFile.serialize_to_bytes(mock_gifti_context)
    
    # Check that we got bytes back
    assert isinstance(state_bytes, bytes)
    
    # Check that the bytes contain a valid ZIP file
    buffer = io.BytesIO(state_bytes)
    with zipfile.ZipFile(buffer, 'r') as zipf:
        # Check that the expected files are in the ZIP
        file_list = zipf.namelist()
        assert 'manifest.json' in file_list
        assert 'state.json' in file_list
        
        # Check the manifest
        manifest = json.loads(zipf.read('manifest.json').decode('utf-8'))
        assert manifest['format_version'] == StateFile.FORMAT_VERSION
        assert 'state.json' in manifest['files']
        assert manifest['metadata']['context_id'] == 'test_gifti'
        assert manifest['metadata']['file_type'] == 'gifti'
        
        # Check the state
        state = json.loads(zipf.read('state.json').decode('utf-8'))
        assert state['file_type'] == 'gifti'
        assert state['tr'] == 2.0

@patch('zipfile.ZipFile')
def test_serialize_to_bytes_with_error(mock_zipfile, mock_nifti_context):
    """Test error handling during serialization."""
    # Mock the zipfile to raise an exception
    mock_zipfile.side_effect = Exception("Test exception")
    
    # Test that the exception is propagated
    with pytest.raises(Exception, match="Test exception"):
        StateFile.serialize_to_bytes(mock_nifti_context)

def test_deserialize_from_bytes_with_invalid_data():
    """Test deserializing invalid data."""
    # Create invalid data (not a ZIP file)
    invalid_data = b'not a zip file'
    
    # Test that an exception is raised
    with pytest.raises(zipfile.BadZipFile):
        StateFile.deserialize_from_bytes(invalid_data)

def test_deserialize_from_bytes_with_invalid_manifest():
    """Test deserializing data with invalid manifest."""
    # Create a ZIP file with invalid manifest
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipf:
        zipf.writestr('manifest.json', json.dumps({"not_valid": True}))
        zipf.writestr('state.json', json.dumps({"file_type": "nifti"}))
    
    buffer.seek(0)
    invalid_data = buffer.getvalue()
    
    # Test that an exception is raised
    with pytest.raises(ValueError, match="Not a valid FIND visualization state file"):
        StateFile.deserialize_from_bytes(invalid_data)

def test_deserialize_from_bytes_with_incompatible_version():
    """Test deserializing data with incompatible version."""
    # Create a ZIP file with incompatible version
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipf:
        manifest = {
            "format_version": "0.0.1",  # Different from current version
            "metadata": {"is_find_viz_state": True},
            "files": ["state.json"]
        }
        zipf.writestr('manifest.json', json.dumps(manifest))
        zipf.writestr('state.json', json.dumps({"file_type": "nifti"}))
    
    buffer.seek(0)
    incompatible_data = buffer.getvalue()
    
    # Test that an exception is raised
    with pytest.raises(FVStateVersionIncompatibleError):
        StateFile.deserialize_from_bytes(incompatible_data)

def test_deserialize_from_bytes_nifti(mock_nifti_image):
    """Test deserializing NIFTI state from bytes."""
    # Create a valid NIFTI state ZIP file
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipf:
        # Create manifest
        manifest = {
            "format_version": StateFile.FORMAT_VERSION,
            "metadata": {
                "is_find_viz_state": True,
                "context_id": "test_nifti",
                "file_type": "nifti"
            },
            "files": ["state.json", "data/func_img.nii.gz"]
        }
        zipf.writestr('manifest.json', json.dumps(manifest))
        
        # Create state
        state = {
            "file_type": "nifti",
            "tr": 2.0,
            "timepoints": {"__type__": "list", "values": [0, 1, 2, 3]},
            "global_min": -1.0,
            "global_max": 1.0,
            "timepoint": 2,
            "nifti_data": {"__type__": "dict", "values": {"func_img": "data/func_img.nii.gz"}}
        }
        zipf.writestr('state.json', json.dumps(state))
        
        # Create mock NIFTI data
        zipf.writestr('data/func_img.nii.gz', b'mock_nifti_data')
    
    buffer.seek(0)
    state_data = buffer.getvalue()
    
    # Deserialize with mocked nibabel
    with patch.object(nib.Nifti1Image, 'from_bytes', return_value=mock_nifti_image):
        context = StateFile.deserialize_from_bytes(state_data)
    
    # Check that the context was created correctly
    assert context.context_id == "test_nifti"
    assert context._state.file_type == "nifti"
    assert context._state.tr == 2.0
    assert context._state.timepoints == [0, 1, 2, 3]
    assert context._state.global_min == -1.0
    assert context._state.global_max == 1.0
    assert context._state.timepoint == 2
    assert 'func_img' in context._state.nifti_data

def test_deserialize_from_bytes_gifti(mock_gifti_image):
    """Test deserializing GIFTI state from bytes."""
    # Create a valid GIFTI state ZIP file
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipf:
        # Create manifest
        manifest = {
            "format_version": StateFile.FORMAT_VERSION,
            "metadata": {
                "is_find_viz_state": True,
                "context_id": "test_gifti",
                "file_type": "gifti"
            },
            "files": [
                "state.json",
                "data/left_func_img.gii", 
                "data/right_func_img.gii",
            ]
        }
        zipf.writestr('manifest.json', json.dumps(manifest))
        
        # Create state
        state = {
            "file_type": "gifti",
            "tr": 2.0,
            "timepoints": {"__type__": "list", "values": [0, 1, 2, 3]},
            "global_min": -1.0,
            "global_max": 1.0,
            "timepoint": 2,
            "left_input": True,
            "right_input": True,
            "gifti_data": {
                "__type__": "dict", 
                "values": {
                    "left_func": "data/left_func_img.gii",
                    "right_func": "data/right_func_img.gii"
                }
            },
            "vertices_left": {"__type__": "numpy_array", "values": [[0, 0, 0], [1, 1, 1]]},
            "faces_left": {"__type__": "numpy_array", "values": [[0, 1, 2]]},
            "vertices_right": {"__type__": "numpy_array", "values": [[3, 3, 3], [4, 4, 4]]},
            "faces_right": {"__type__": "numpy_array", "values": [[0, 1, 2]]}
        }
        zipf.writestr('state.json', json.dumps(state))
        
        # Create mock GIFTI data
        zipf.writestr('data/left_func_img.gii', b'mock_left_gifti_data')
        zipf.writestr('data/right_func_img.gii', b'mock_right_gifti_data')
    
    buffer.seek(0)
    state_data = buffer.getvalue()
    
    # Deserialize with mocked nibabel
    with patch.object(nib.gifti.GiftiImage, 'from_bytes', return_value=mock_gifti_image):
        context = StateFile.deserialize_from_bytes(state_data)
    
    # Check that the context was created correctly
    assert context.context_id == "test_gifti"
    assert context._state.file_type == "gifti"
    assert context._state.tr == 2.0
    assert context._state.timepoints == [0, 1, 2, 3]
    assert context._state.global_min == -1.0
    assert context._state.global_max == 1.0
    assert context._state.timepoint == 2
    assert context._state.left_input is True
    assert context._state.right_input is True
    assert 'left_func_img' in context._state.gifti_data
    assert 'right_func_img' in context._state.gifti_data
    
    # Check that the vertex and face data was loaded correctly
    assert np.array_equal(context._state.vertices_left, np.array([[0, 0, 0], [1, 1, 1]]))
    assert np.array_equal(context._state.faces_left, np.array([[0, 1, 2]]))
    assert np.array_equal(context._state.vertices_right, np.array([[3, 3, 3], [4, 4, 4]]))
    assert np.array_equal(context._state.faces_right, np.array([[0, 1, 2]]))
    
    # Check that both_hemispheres was set correctly
    assert context._state.both_hemispheres is True

def test_deserialize_from_bytes_version_incompatible():
    """Test deserializing state with incompatible version."""
    # Create a ZIP file with incompatible version
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipf:
        # Create manifest with incompatible version
        manifest = {
            "format_version": "999.0.0",  # Future version
            "metadata": {
                "is_find_viz_state": True,
                "context_id": "test_nifti",
                "file_type": "nifti"
            },
            "files": ["state.json"]
        }
        zipf.writestr('manifest.json', json.dumps(manifest))
        
        # Create simple state
        state = {
            "file_type": "nifti",
            "tr": 2.0
        }
        zipf.writestr('state.json', json.dumps(state))
    
    buffer.seek(0)
    state_data = buffer.getvalue()
    
    # Try to deserialize the state with incompatible version
    with pytest.raises(FVStateVersionIncompatibleError):
        StateFile.deserialize_from_bytes(state_data)
