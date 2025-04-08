import pytest
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock
import nibabel as nib
import numpy as np

from findviz.cli import (
    parse_args, process_cli_inputs, 
    find_free_port, validate_files
)
from findviz.routes.shared import data_manager
from findviz.viz import exception

# Test data paths
TEST_DATA = Path(__file__).parent / "data"
NIFTI_FUNC = TEST_DATA / "test_func.nii.gz"
NIFTI_ANAT = TEST_DATA / "test_anat.nii.gz"
NIFTI_MASK = TEST_DATA / "test_mask.nii.gz"
GIFTI_LEFT_FUNC = TEST_DATA / "test_left.func.gii"
GIFTI_RIGHT_FUNC = TEST_DATA / "test_right.func.gii"
GIFTI_LEFT_MESH = TEST_DATA / "test_left.surf.gii"
GIFTI_RIGHT_MESH = TEST_DATA / "test_right.surf.gii"
TIMESERIES = TEST_DATA / "test_timeseries.csv"
TASK_DESIGN = TEST_DATA / "test_task.tsv"


@pytest.fixture
def mock_data_manager():
    """Mock DataManager instance"""
    with patch('findviz.routes.shared.data_manager') as mock:
        yield mock

@pytest.fixture
def mock_cache():
    """Mock Cache class"""
    with patch('findviz.viz.io.cache.Cache') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        # Make sure the save method is properly mocked
        mock_instance.save = MagicMock()
        yield mock_instance

@pytest.fixture
def mock_file_upload():
    """Mock FileUpload class"""
    with patch('findviz.cli.FileUpload', autospec=True) as mock:
        instance = mock.return_value
        instance.upload.return_value = {
            'file_type': 'mock_type',
            'data': 'mock_data'
        }
        yield instance

@pytest.fixture
def mock_file_exists():
    """Mock os.path.exists to always return True for test files"""
    with patch('os.path.exists') as mock:
        def side_effect(path):
            # Return True for our test paths, False otherwise
            test_paths = [
                str(NIFTI_FUNC), str(NIFTI_ANAT), str(NIFTI_MASK),
                str(GIFTI_LEFT_FUNC), str(GIFTI_RIGHT_FUNC),
                str(GIFTI_LEFT_MESH), str(GIFTI_RIGHT_MESH),
                str(TIMESERIES), str(TASK_DESIGN)
            ]
            return path in test_paths
        mock.side_effect = side_effect
        yield mock

def test_process_cli_inputs_nifti(mock_file_upload, mock_cache, mock_file_exists):
    """Test processing NIFTI inputs"""
    with patch('findviz.cli.FileUpload') as mock_class, \
         patch('findviz.viz.viewer.utils.package_nii_metadata') as mock_metadata, \
         patch('findviz.cli.data_manager') as mock_data_manager, \
         patch('findviz.cli.Cache', return_value=mock_cache):
        mock_class.return_value = mock_file_upload
        
        # Mock the enum values and attributes
        mock_file_upload.Nifti = MagicMock()
        mock_file_upload.Nifti.FUNC.value = 'nii_func'
        mock_file_upload.Nifti.ANAT.value = 'nii_anat'
        mock_file_upload.Nifti.MASK.value = 'nii_mask'
        mock_file_upload.ts_status = False
        mock_file_upload.task_status = False

        # Mock the metadata return values
        mock_metadata.return_value = {
            'timepoints': [0, 1, 2],
            'global_min': 0.0,
            'global_max': 1.0,
            'slice_len': {'x': 10, 'y': 10, 'z': 10}
        }

        # Mock the viewer metadata
        mock_data_manager.get_viewer_metadata.return_value = {
            'file_type': 'nifti',
            'timepoints': [0, 1, 2],
            'global_min': 0.0,
            'global_max': 1.0,
            'slice_len': {'x': 10, 'y': 10, 'z': 10},
            'anat_input': True,
            'mask_input': True
        }

        # Mock the upload return value
        mock_nifti = MagicMock(spec=nib.Nifti1Image)
        mock_file_upload.upload.return_value = {
            'nifti': {
                'nii_func': mock_nifti,
                'nii_anat': mock_nifti,
                'nii_mask': mock_nifti
            }
        }
        
        args = argparse.Namespace(
            file_type='nifti',
            nifti_func=str(NIFTI_FUNC),
            nifti_anat=str(NIFTI_ANAT),
            nifti_mask=str(NIFTI_MASK),
            gifti_left_func=None,
            gifti_right_func=None,
            gifti_left_mesh=None,
            gifti_right_mesh=None,
            cifti_dtseries=None,
            cifti_left_mesh=None,
            cifti_right_mesh=None,
            timeseries=None,
            ts_labels=None,
            ts_headers=None,
            task_design=None,
            tr=2.0,
            slicetime_ref=0.5
        )
        
        process_cli_inputs(args)
        
        # Verify FileUpload was called correctly
        mock_file_upload.upload.assert_called_once()
        call_args = mock_file_upload.upload.call_args[1]
        assert call_args['fmri_files']['nii_func'] == str(NIFTI_FUNC)

def test_process_cli_inputs_gifti(mock_file_upload, mock_cache, mock_file_exists):
    """Test processing GIFTI inputs"""
    with patch('findviz.cli.FileUpload') as mock_class, \
         patch('findviz.viz.viewer.utils.package_gii_metadata') as mock_metadata, \
         patch('findviz.cli.data_manager') as mock_data_manager, \
         patch('findviz.cli.Cache', return_value=mock_cache):
        mock_class.return_value = mock_file_upload

        # Mock the enum values and attributes
        mock_file_upload.Gifti = MagicMock()
        mock_file_upload.Gifti.LEFT_FUNC.value = 'left_gii_func'
        mock_file_upload.Gifti.RIGHT_FUNC.value = 'right_gii_func'
        mock_file_upload.Gifti.LEFT_MESH.value = 'left_gii_mesh'
        mock_file_upload.Gifti.RIGHT_MESH.value = 'right_gii_mesh'
        mock_file_upload.ts_status = False
        mock_file_upload.task_status = False

        # Mock the metadata return values
        mock_metadata.return_value = {
            'timepoints': [0, 1, 2],
            'global_min': 0.0,
            'global_max': 1.0
        }

        # Create the expected viewer metadata
        expected_metadata = {
            'file_type': 'gifti',
            'timepoints': [0, 1, 2],
            'global_min': 0.0,
            'global_max': 1.0,
            'left_input': True,
            'right_input': True,
            'vertices_left': [0.0, 0.0, 0.0],
            'faces_left': [0, 1, 2],
            'vertices_right': [0.0, 0.0, 0.0],
            'faces_right': [0, 1, 2]
        }

        # Mock the viewer metadata to return our expected metadata
        mock_data_manager.ctx.get_viewer_metadata.return_value = expected_metadata

        # Create mock GiftiImage with darrays
        mock_darray1 = MagicMock()
        mock_darray1.data = np.zeros((100, 3))  # vertices
        mock_darray2 = MagicMock()
        mock_darray2.data = np.zeros((50, 3))   # faces

        mock_gifti = MagicMock(spec=nib.gifti.GiftiImage)
        mock_gifti.darrays = [mock_darray1, mock_darray2]

        mock_file_upload.upload.return_value = {
            'gifti': {
                'left_gii_func': mock_gifti,
                'right_gii_func': mock_gifti,
                'left_gii_mesh': mock_gifti,
                'right_gii_mesh': mock_gifti
            }
        }
        
        args = argparse.Namespace(
            file_type='gifti',
            nifti_func=None,
            nifti_anat=None,
            nifti_mask=None,
            gifti_left_func=str(GIFTI_LEFT_FUNC),
            gifti_right_func=str(GIFTI_RIGHT_FUNC),
            gifti_left_mesh=str(GIFTI_LEFT_MESH),
            gifti_right_mesh=str(GIFTI_RIGHT_MESH),
            cifti_dtseries=None,
            cifti_left_mesh=None,
            cifti_right_mesh=None,
            timeseries=None,
            ts_labels=None,
            ts_headers=None,
            task_design=None,
            tr=None,
            slicetime_ref=0.5
        )
        
        process_cli_inputs(args)
        
        # Verify FileUpload was called correctly
        mock_file_upload.upload.assert_called_once()
        call_args = mock_file_upload.upload.call_args[1]
        assert call_args['fmri_files']['left_gii_func'] == str(GIFTI_LEFT_FUNC)
        assert call_args['fmri_files']['right_gii_func'] == str(GIFTI_RIGHT_FUNC)

        # Verify data_manager interactions
        mock_data_manager.ctx.create_gifti_state.assert_called_once_with(
            left_func_img=mock_gifti,
            right_func_img=mock_gifti,
            left_mesh=mock_gifti,
            right_mesh=mock_gifti
        )
        
        # Verify cache was created with metadata
        mock_cache.save.assert_called_once_with(expected_metadata)

def test_mutually_exclusive_inputs():
    """Test that NIFTI and GIFTI inputs are mutually exclusive"""
    test_args = [
        '--nifti-func', str(NIFTI_FUNC),
        '--gifti-left-func', str(GIFTI_LEFT_FUNC)
    ]
    
    with patch('sys.argv', ['findviz'] + test_args):
        with pytest.raises(exception.FileInputError) as exc_info:
            parse_args()

def test_process_cli_inputs_validation_error(mock_file_upload, mock_cache, mock_file_exists):
    """Test handling of validation errors"""
    with patch('findviz.cli.FileUpload') as mock_class:
        mock_class.return_value = mock_file_upload
        mock_file_upload.upload.side_effect = exception.FileValidationError(
            "Invalid file", "test_validation", "nifti", ["field"]
        )
        
        args = argparse.Namespace(
            file_type='nifti',
            nifti_func=str(NIFTI_FUNC),
            nifti_anat=None,
            nifti_mask=None,
            gifti_left_func=None,
            gifti_right_func=None,
            gifti_left_mesh=None,
            gifti_right_mesh=None,
            timeseries=None,
            ts_labels=None,
            ts_headers=None,
            task_design=None,
            tr=None,
            slicetime_ref=0.5
        )

        with pytest.raises(exception.FileValidationError):
            process_cli_inputs(args)

def test_parse_args_nifti():
    """Test parsing NIFTI command line arguments"""
    test_args = [
        '--nifti-func', str(NIFTI_FUNC),
        '--nifti-anat', str(NIFTI_ANAT),
        '--nifti-mask', str(NIFTI_MASK),
        '--tr', '2.0',
        '--slicetime-ref', '0.5'
    ]
    
    with patch('sys.argv', ['findviz'] + test_args):
        args = parse_args()
        
    assert args.nifti_func == str(NIFTI_FUNC)
    assert args.nifti_anat == str(NIFTI_ANAT)
    assert args.nifti_mask == str(NIFTI_MASK)
    assert args.tr == 2.0
    assert args.slicetime_ref == 0.5

def test_parse_args_gifti():
    """Test parsing GIFTI command line arguments"""
    test_args = [
        '--gifti-left-func', str(GIFTI_LEFT_FUNC),
        '--gifti-right-func', str(GIFTI_RIGHT_FUNC),
        '--gifti-left-mesh', str(GIFTI_LEFT_MESH),
        '--gifti-right-mesh', str(GIFTI_RIGHT_MESH)
    ]
    
    with patch('sys.argv', ['findviz'] + test_args):
        args = parse_args()
        
    assert args.gifti_left_func == str(GIFTI_LEFT_FUNC)
    assert args.gifti_right_func == str(GIFTI_RIGHT_FUNC)
    assert args.gifti_left_mesh == str(GIFTI_LEFT_MESH)
    assert args.gifti_right_mesh == str(GIFTI_RIGHT_MESH)

def test_parse_args_timeseries():
    """Test parsing timeseries arguments"""
    test_args = [
        '--nifti-func', str(NIFTI_FUNC),
        '--timeseries', str(TIMESERIES), str(TIMESERIES),
        '--ts-labels', 'ts1', 'ts2',
        '--ts-headers', 'true', 'false'
    ]
    
    with patch('sys.argv', ['findviz'] + test_args):
        args = parse_args()
        
    assert args.timeseries == [str(TIMESERIES), str(TIMESERIES)]
    assert args.ts_labels == ['ts1', 'ts2']
    assert args.ts_headers == ['true', 'false']

def test_parse_args_cifti():
    """Test parsing CIFTI command line arguments"""
    test_args = [
        '--cifti-dtseries', 'test.dtseries.nii',
        '--cifti-left-mesh', str(GIFTI_LEFT_MESH),
        '--cifti-right-mesh', str(GIFTI_RIGHT_MESH)
    ]
    
    with patch('sys.argv', ['findviz'] + test_args):
        args = parse_args()
        
    assert args.cifti_dtseries == 'test.dtseries.nii'
    assert args.cifti_left_mesh == str(GIFTI_LEFT_MESH)
    assert args.cifti_right_mesh == str(GIFTI_RIGHT_MESH)
    assert args.file_type == 'cifti'

def test_parse_args_file_type():
    """Test that file_type is correctly set based on inputs"""
    # Test NIFTI
    with patch('sys.argv', ['findviz', '--nifti-func', str(NIFTI_FUNC)]):
        args = parse_args()
        assert args.file_type == 'nifti'
    
    # Test GIFTI
    with patch('sys.argv', ['findviz', '--gifti-left-func', str(GIFTI_LEFT_FUNC)]):
        args = parse_args()
        assert args.file_type == 'gifti'
    
    # Test CIFTI
    with patch('sys.argv', ['findviz', '--cifti-dtseries', 'test.dtseries.nii']):
        args = parse_args()
        assert args.file_type == 'cifti'

def test_multiple_file_types():
    """Test that using multiple file types raises an error"""
    test_cases = [
        ['--nifti-func', str(NIFTI_FUNC), '--gifti-left-func', str(GIFTI_LEFT_FUNC)],
        ['--nifti-func', str(NIFTI_FUNC), '--cifti-dtseries', 'test.dtseries.nii'],
        ['--gifti-left-func', str(GIFTI_LEFT_FUNC), '--cifti-dtseries', 'test.dtseries.nii']
    ]
    
    for test_args in test_cases:
        with patch('sys.argv', ['findviz'] + test_args):
            with pytest.raises(exception.FileInputError) as exc_info:
                parse_args()
            assert "Only one file type" in str(exc_info.value)

def test_validate_files():
    """Test validation of file existence"""
    with patch('os.path.exists') as mock_exists:
        # Test when all files exist
        mock_exists.return_value = True
        files = {
            'file1': '/path/to/file1',
            'file2': '/path/to/file2'
        }
        validate_files(files)  # Should not raise any exception

        # Test when some files don't exist
        mock_exists.side_effect = lambda x: x == '/path/to/file1'
        files = {
            'file1': '/path/to/file1',
            'file2': '/path/to/file2'
        }
        with pytest.raises(FileNotFoundError) as exc_info:
            validate_files(files)
        assert '/path/to/file2' in str(exc_info.value)

        # Test with None values in dictionary
        mock_exists.return_value = True
        files = {
            'file1': '/path/to/file1',
            'file2': None
        }
        validate_files(files)  # Should not raise any exception

        # Test with empty dictionary
        files = {}
        validate_files(files)  # Should not raise any exception

        # Test with all None values
        files = {
            'file1': None,
            'file2': None
        }
        validate_files(files)  # Should not raise any exception

        # Test multiple missing files
        mock_exists.return_value = False
        files = {
            'file1': '/path/to/file1',
            'file2': '/path/to/file2',
            'file3': '/path/to/file3'
        }
        with pytest.raises(FileNotFoundError) as exc_info:
            validate_files(files)

def test_find_free_port():
    """Test finding an available port"""
    port = find_free_port()
    assert isinstance(port, int)
    assert port > 0