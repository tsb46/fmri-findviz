"""Tests for viewer type definitions"""
import pytest
import nibabel as nib
import numpy as np
from typing import Dict, List

from findviz.viz.viewer.types import (
    ViewerMetadataNiftiDict,
    ViewerMetadataGiftiDict,
    ViewerDataNiftiDict,
    ViewerDataGiftiDict
)
from findviz.viz.io.timecourse import TaskDesignDict

def test_viewer_metadata_nifti_dict_valid():
    """Test valid ViewerMetadataNiftiDict initialization"""
    metadata: ViewerMetadataNiftiDict = {
        'file_type': 'nifti',
        'anat_input': True,
        'mask_input': True,
        'x_slice_idx': 32,
        'y_slice_idx': 32,
        'z_slice_idx': 20,
        'view_state': 'ortho',
        'montage_slice_dir': 'z',
        'timepoints': [0, 1, 2],
        'preprocessed': False,
        'global_min': -1.0,
        'global_max': 1.0,
        'slice_len': {'x': 64, 'y': 64, 'z': 40},
        'ts_enabled': False,
        'task_enabled': False
    }
    
    # Type checking should pass
    assert isinstance(metadata, dict)
    assert metadata['file_type'] == 'nifti'
    assert isinstance(metadata['timepoints'], list)
    assert isinstance(metadata['slice_len'], dict)

def test_viewer_metadata_nifti_dict_invalid_file_type():
    """Test ViewerMetadataNiftiDict with invalid file type"""
    # Create metadata with invalid file type
    metadata: ViewerMetadataNiftiDict = {
        'file_type': 'invalid',  # Should be 'nifti'
        'anat_input': True,
        'mask_input': True,
        'x_slice_idx': 32,
        'y_slice_idx': 32,
        'z_slice_idx': 20,
        'view_state': 'ortho',
        'montage_slice_dir': 'z',
        'timepoints': [0, 1, 2],
        'preprocessed': False,
        'global_min': -1.0,
        'global_max': 1.0,
        'slice_len': {'x': 64, 'y': 64, 'z': 40},
        'ts_enabled': False,
        'task_enabled': False
    }
    
    # While TypedDict doesn't enforce runtime checking, we can verify
    # that the value doesn't match the expected literal type
    assert metadata['file_type'] != 'nifti'
    assert metadata['file_type'] not in ['nifti', 'gifti']

def test_viewer_metadata_gifti_dict_valid():
    """Test valid ViewerMetadataGiftiDict initialization"""
    metadata: ViewerMetadataGiftiDict = {
        'file_type': 'gifti',
        'left_input': True,
        'right_input': True,
        'vertices_left': [0.0, 1.0, 2.0],
        'faces_left': [0, 1, 2],
        'vertices_right': [3.0, 4.0, 5.0],
        'faces_right': [3, 4, 5],
        'timepoints': [0, 1, 2],
        'preprocessed': False,
        'global_min': 0.0,
        'global_max': 1.0,
        'ts_enabled': False,
        'task_enabled': False
    }
    
    assert isinstance(metadata, dict)
    assert metadata['file_type'] == 'gifti'
    assert isinstance(metadata['vertices_left'], list)
    assert isinstance(metadata['faces_left'], list)

def test_viewer_data_nifti_dict_valid(mock_nifti_4d, mock_nifti_3d):
    """Test valid ViewerDataNiftiDict initialization"""
    task_data: TaskDesignDict = {
        'task_regressors': {
            'condition1': {
                'block': [1.0, 0.0, 1.0],
                'hrf': [0.1, 0.2, 0.3]
            }
        },
        'tr': 2.0,
        'slicetime_ref': 0.5
    }
    
    viewer_data: ViewerDataNiftiDict = {
        'anat_input': True,
        'mask_input': True,
        'func_img': mock_nifti_4d,
        'anat_img': mock_nifti_3d,
        'mask_img': mock_nifti_3d,
        'ts': {'ROI1': [0.1, 0.2, 0.3]},
        'ts_labels': ['ROI1'],
        'task': task_data
    }
    
    assert isinstance(viewer_data, dict)
    assert isinstance(viewer_data['func_img'], nib.Nifti1Image)
    assert isinstance(viewer_data['ts'], dict)
    assert isinstance(viewer_data['task'], dict)

def test_viewer_data_nifti_dict_optional_fields():
    """Test ViewerDataNiftiDict with optional fields"""
    viewer_data: ViewerDataNiftiDict = {
        'anat_input': None,
        'mask_input': None,
        'func_img': None,
        'anat_img': None,
        'mask_img': None,
        'ts': None,
        'ts_labels': None,
        'task': None
    }
    
    assert isinstance(viewer_data, dict)
    assert viewer_data['anat_input'] is None
    assert viewer_data['ts'] is None
    assert viewer_data['task'] is None

def test_viewer_data_gifti_dict_valid(mock_gifti_func, mock_gifti_mesh):
    """Test valid ViewerDataGiftiDict initialization"""
    task_data: TaskDesignDict = {
        'task_regressors': {
            'condition1': {
                'block': [1.0, 0.0, 1.0],
                'hrf': [0.1, 0.2, 0.3]
            }
        },
        'tr': 2.0,
        'slicetime_ref': 0.5
    }
    
    viewer_data: ViewerDataGiftiDict = {
        'left_input': True,
        'right_input': True,
        'left_func_img': mock_gifti_func,
        'right_func_img': mock_gifti_func,
        'vertices_left': [0.0, 1.0, 2.0],
        'faces_left': [0, 1, 2],
        'vertices_right': [3.0, 4.0, 5.0],
        'faces_right': [3, 4, 5],
        'ts': {'ROI1': [0.1, 0.2, 0.3]},
        'ts_labels': ['ROI1'],
        'task': task_data
    }
    
    assert isinstance(viewer_data, dict)
    assert isinstance(viewer_data['left_func_img'], nib.gifti.GiftiImage)
    assert isinstance(viewer_data['vertices_left'], list)
    assert isinstance(viewer_data['ts'], dict)
    assert isinstance(viewer_data['task'], dict)

def test_viewer_data_gifti_dict_optional_fields():
    """Test ViewerDataGiftiDict with optional fields"""
    viewer_data: ViewerDataGiftiDict = {
        'left_input': None,
        'right_input': None,
        'left_func_img': None,
        'right_func_img': None,
        'vertices_left': None,
        'faces_left': None,
        'vertices_right': None,
        'faces_right': None,
        'ts': None,
        'ts_labels': None,
        'task': None
    }
    
    assert isinstance(viewer_data, dict)
    assert viewer_data['left_input'] is None
    assert viewer_data['vertices_left'] is None
    assert viewer_data['ts'] is None

def test_viewer_metadata_nifti_dict_invalid_view_state():
    """Test ViewerMetadataNiftiDict with invalid view state"""
    metadata: ViewerMetadataNiftiDict = {
        'file_type': 'nifti',
        'anat_input': True,
        'mask_input': True,
        'x_slice_idx': 32,
        'y_slice_idx': 32,
        'z_slice_idx': 20,
        'view_state': 'invalid',  # Should be 'ortho' or 'montage'
        'montage_slice_dir': 'z',
        'timepoints': [0, 1, 2],
        'preprocessed': False,
        'global_min': -1.0,
        'global_max': 1.0,
        'slice_len': {'x': 64, 'y': 64, 'z': 40},
        'ts_enabled': False,
        'task_enabled': False
    }
    
    assert metadata['view_state'] not in ['ortho', 'montage']
