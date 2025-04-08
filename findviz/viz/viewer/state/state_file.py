"""
State serialization for FIND Viewer state files (.fvstate)
"""
import io
import json
import zipfile
import datetime

from typing import Dict, List, Union

import numpy as np
import nibabel as nib

from findviz.viz.exception import FVStateVersionIncompatibleError
from findviz.logger_config import setup_logger
from findviz.viz.viewer.context import VisualizationContext
from findviz.viz.viewer.state.viz_state import NiftiVisualizationState, GiftiVisualizationState
from findviz.viz.analysis.scaler import SignalScaler, SignalShifter

logger = setup_logger(__name__)

class StateFile:
    """Handles serialization and deserialization of VisualizationContext to custom .fvstate format.
    
    This creates a ZIP-based container with:
    - manifest.json: Contains file version, structure, and validation info
    - state.json: Contains serialized visualization state excluding large data
    - data/: Directory containing binary data for nibabel objects
    """
    
    # Current format version
    FORMAT_VERSION = "1.0.0"
    
    # Fields to exclude from JSON serialization
    EXCLUDE_FIELDS = {
        'nifti_data', 'nifti_data_preprocessed', 
        'gifti_data', 'gifti_data_preprocessed',
        'distance_data', 'func_header', 'func_affine'
    }
    
    @classmethod
    def serialize_to_bytes(cls, context: VisualizationContext) -> bytes:
        """Serialize a context to bytes in the .fvstate format.
        
        Args:
            context: The visualization context to serialize
            
        Returns:
            bytes: Serialized data in .fvstate format
        """
        # Ensure we have a state to save
        if context._state is None:
            raise ValueError("Cannot serialize context with no state")
        
        # Create an in-memory ZIP file
        buffer = io.BytesIO()
        manifest = {"format_version": cls.FORMAT_VERSION, "files": []}
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Serialize state JSON (excluding large data)
            state_dict = cls._serialize_state(context._state)
            state_json = json.dumps(state_dict, indent=2)
            zipf.writestr('state.json', state_json)
            manifest["files"].append("state.json")
            
            # Serialize large data components
            data_files = cls._serialize_data(context, zipf)
            manifest["files"].extend(data_files)
            
            # Add metadata
            manifest["metadata"] = {
                "created_at": datetime.datetime.now().isoformat(),
                "context_id": context.context_id,
                "file_type": context._state.file_type,
                "is_find_viz_state": True
            }
            
            # Write manifest
            zipf.writestr('manifest.json', json.dumps(manifest, indent=2))
        
        # Get the bytes from the buffer
        buffer.seek(0)
        return buffer.getvalue()
    
    @classmethod
    def deserialize_from_bytes(cls, data: bytes) -> VisualizationContext:
        """Deserialize bytes in .fvstate format to a VisualizationContext.
        
        Args:
            data: Bytes in .fvstate format
            
        Returns:
            VisualizationContext: Deserialized context
        """
        buffer = io.BytesIO(data)
        
        with zipfile.ZipFile(buffer, 'r') as zipf:
            # Read and validate manifest
            try:
                manifest = json.loads(zipf.read('manifest.json').decode('utf-8'))
                if manifest.get("metadata", {}).get("is_find_viz_state") is not True:
                    raise ValueError("Not a valid FIND visualization state file")
                
                # Check version compatibility
                format_version = manifest.get("format_version")
                if format_version != cls.FORMAT_VERSION:
                    raise FVStateVersionIncompatibleError(
                        message="Incompatible fvstate file version",
                        expected_version=cls.FORMAT_VERSION,
                        current_version=format_version
                    )
                
                # Read state JSON
                state_json = zipf.read('state.json').decode('utf-8')
                state_dict = json.loads(state_json)
                
                # Create context
                context_id = manifest.get("metadata", {}).get("context_id", "imported")
                context = VisualizationContext(context_id)
                
                # Restore data components and state
                file_type = manifest.get("metadata", {}).get("file_type")
                if file_type == 'nifti':
                    cls._deserialize_nifti_data(context, zipf, state_dict)
                elif file_type == 'gifti':
                    cls._deserialize_gifti_data(context, zipf, state_dict)
                else:
                    raise ValueError(f"Unsupported file type: {file_type}")
                
                return context
                
            except (KeyError, json.JSONDecodeError) as e:
                raise ValueError(f"Invalid state file format: {str(e)}")
    
    @classmethod
    def _serialize_state(cls, state: Union[NiftiVisualizationState, GiftiVisualizationState]) -> Dict:
        """Serialize state to a dictionary, excluding large data components."""
        state_dict = {}

        # Get all attributes that should be serialized
        for key, value in state.__dict__.items():
            if key.startswith('_') and key != '_ts_labels' or key in cls.EXCLUDE_FIELDS:
                continue
            # Special handling for _ts_labels to save it as ts_labels
            if key == '_ts_labels':
                state_dict['ts_labels'] = value
                continue
            # Handle special cases for complex objects
            if key == 'ts_plot_options':
                # Serialize time course plot options
                options = {}
                if value is not None:
                    for ts_id, ts_opts in value.items():
                        options[ts_id] = ts_opts.to_dict()
                    state_dict[key] = options
                else:
                    state_dict[key] = None
            elif key == 'task_plot_options':
                # Serialize task design plot options
                options = {}
                if value is not None:
                    for task_id, task_opts in value.items():
                        options[task_id] = task_opts.to_dict()
                    state_dict[key] = options
                else:
                    state_dict[key] = None
            elif key in ['time_marker_plot_options', 'annotation_marker_plot_options',
                        'distance_plot_options', 'time_course_global_plot_options']:
                # Serialize other plot options
                if value is not None:
                    state_dict[key] = value.to_dict()
                else:
                    state_dict[key] = None
                
            elif key == 'fmri_plot_options' or key == 'preprocessed_fmri_plot_options':
                # Serialize fMRI plot options
                if value is not None:
                    state_dict[key] = value.to_dict()
                else:
                    state_dict[key] = None
            # Special handling for used_colors set of TimeCourseColor objects
            elif key == 'used_colors':
                # Convert set of TimeCourseColor objects to a list of serializable representations
                color_list = []
                for color in value:
                    if hasattr(color, 'value'):
                        color_list.append(color.value)
                    else:
                        # Fallback
                        color_list.append(str(color))
                        
                state_dict[key] = {
                    "__type__": "set",
                    "__item_type__": "TimeCourseColor",
                    "values": color_list
                }
            # Convert set to list and mark it as a set for deserialization
            elif isinstance(value, set):
                state_dict[key] = {
                    "__type__": "set",
                    "values": list(value)
                }
            else:
                # Handle basic types and numpy arrays
                if isinstance(value, np.ndarray):
                    # set type as numpy array for deserialization
                    state_dict[key] = {
                        "__type__": "numpy_array",
                        "values": value.tolist()
                    }
                elif isinstance(value, (str, int, float, bool, type(None))):
                    state_dict[key] = value
                elif isinstance(value, list):
                    # Convert any numpy arrays in lists
                    state_dict[key] = {
                        "__type__": "list",
                        "values": cls._serialize_list(value)
                    }
                elif isinstance(value, dict):
                    # Convert any numpy arrays in dicts
                    state_dict[key] = {
                        "__type__": "dict",
                        "values": cls._serialize_dict(value)
                    }
                else:
                    # Skip complex objects that we don't know how to serialize
                    logger.warning(f"Skipping serialization of {key}: {type(value)}")
        
        return state_dict
    
    @classmethod
    def _serialize_list(cls, lst: List) -> List:
        """Recursively serialize a list, converting numpy arrays to lists."""
        result = []
        for item in lst:
            if isinstance(item, np.ndarray):
                result.append({
                    "__type__": "numpy_array",
                    "values": item.tolist()
                })
            elif isinstance(item, list):
                result.append({
                    "__type__": "list",
                    "values": cls._serialize_list(item)
                })
            elif isinstance(item, dict):
                result.append({
                    "__type__": "dict",
                    "values": cls._serialize_dict(item)
                })
            else:
                result.append(item)
        return result
    
    @classmethod
    def _deserialize_list(cls, lst: List) -> List:
        """Recursively deserialize a list, converting numpy arrays to lists."""
        result = []
        for item in lst:
            if isinstance(item, dict) and item.get("__type__") == "numpy_array":
                result.append(np.array(item.get("values")))
            elif isinstance(item, dict) and item.get("__type__") == "list":
                result.append(cls._deserialize_list(item.get("values")))
            elif isinstance(item, dict) and item.get("__type__") == "dict":
                result.append(cls._deserialize_dict(item.get("values")))
            else:
                result.append(item)
        return result
    
    @classmethod
    def _serialize_dict(cls, d: Dict) -> Dict:
        """Recursively serialize a dict, converting numpy arrays to lists."""
        result = {}
        for key, value in d.items():
            if isinstance(value, np.ndarray):
                result[key] = value.tolist()
            elif isinstance(value, list):
                result[key] = cls._serialize_list(value)
            elif isinstance(value, dict):
                result[key] = cls._serialize_dict(value)
            else:
                result[key] = value
        return result

    @classmethod
    def _deserialize_dict(cls, d: Dict) -> Dict:
        """Recursively deserialize a dict, converting numpy arrays to lists."""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict) and value.get("__type__") == "numpy_array":
                result[key] = np.array(value.get("values"))
            elif isinstance(value, dict) and value.get("__type__") == "list":
                result[key] = cls._deserialize_list(value.get("values"))
            elif isinstance(value, dict) and value.get("__type__") == "dict":
                result[key] = cls._deserialize_dict(value.get("values"))
            else:
                result[key] = value
        return result

    @classmethod
    def _serialize_data(cls, context: VisualizationContext, zipf: zipfile.ZipFile) -> List[str]:
        """Serialize large data components to the ZIP file.
        
        Args:
            context: The visualization context to serialize
            zipf: The ZIP file to write to
            
        Returns:
            List[str]: List of data file paths added to the ZIP
        """
        data_files = []
        
        if context._state.file_type == 'nifti':
            # Handle NIFTI data
            nifti_data = context._state.nifti_data
            
            # Save func_img if it exists
            if 'func_img' in nifti_data and nifti_data['func_img'] is not None:
                func_path = 'data/func_img.nii.gz'
                # Use nibabel's to_bytes method instead of file map manipulation
                func_bytes = nifti_data['func_img'].to_bytes()
                zipf.writestr(func_path, func_bytes)
                data_files.append(func_path)
                
            # Save anat_img if it exists
            if 'anat_img' in nifti_data and nifti_data['anat_img'] is not None:
                anat_path = 'data/anat_img.nii.gz'
                anat_bytes = nifti_data['anat_img'].to_bytes()
                zipf.writestr(anat_path, anat_bytes)
                data_files.append(anat_path)
                
            # Save mask_img if it exists
            if 'mask_img' in nifti_data and nifti_data['mask_img'] is not None:
                mask_path = 'data/mask_img.nii.gz'
                mask_bytes = nifti_data['mask_img'].to_bytes()
                zipf.writestr(mask_path, mask_bytes)
                data_files.append(mask_path)
                
            # Store preprocessed data if it exists
            if hasattr(context._state, 'nifti_data_preprocessed') and context._state.nifti_data_preprocessed:
                for key, img in context._state.nifti_data_preprocessed.items():
                    if img is not None and isinstance(img, nib.Nifti1Image):
                        img_path = f'data/preproc_{key}.nii.gz'
                        img_bytes = img.to_bytes()
                        zipf.writestr(img_path, img_bytes)
                        data_files.append(img_path)
                
        elif context._state.file_type == 'gifti':
            # Handle GIFTI data
            gifti_data = context._state.gifti_data
            
            # Save left_func_img if it exists
            if 'left_func_img' in gifti_data and gifti_data['left_func_img'] is not None:
                left_func_path = 'data/left_func_img.gii'
                left_func_bytes = gifti_data['left_func_img'].to_bytes()
                zipf.writestr(left_func_path, left_func_bytes)
                data_files.append(left_func_path)
                
            # Save right_func_img if it exists
            if 'right_func_img' in gifti_data and gifti_data['right_func_img'] is not None:
                right_func_path = 'data/right_func_img.gii'
                right_func_bytes = gifti_data['right_func_img'].to_bytes()
                zipf.writestr(right_func_path, right_func_bytes)
                data_files.append(right_func_path)
                
            # Save left_mesh if it exists
            if 'left_mesh' in gifti_data and gifti_data['left_mesh'] is not None:
                left_mesh_path = 'data/left_mesh.gii'
                left_mesh_bytes = gifti_data['left_mesh'].to_bytes()
                zipf.writestr(left_mesh_path, left_mesh_bytes)
                data_files.append(left_mesh_path)
                
            # Save right_mesh if it exists
            if 'right_mesh' in gifti_data and gifti_data['right_mesh'] is not None:
                right_mesh_path = 'data/right_mesh.gii'
                right_mesh_bytes = gifti_data['right_mesh'].to_bytes()
                zipf.writestr(right_mesh_path, right_mesh_bytes)
                data_files.append(right_mesh_path)
                
            # Store preprocessed data if it exists
            if hasattr(context._state, 'gifti_data_preprocessed') and context._state.gifti_data_preprocessed:
                for key, img in context._state.gifti_data_preprocessed.items():
                    if img is not None and isinstance(img, (nib.GiftiImage, nib.gifti.GiftiImage)):
                        img_path = f'data/preproc_{key}.gii'
                        img_bytes = img.to_bytes()
                        zipf.writestr(img_path, img_bytes)
                        data_files.append(img_path)
                            
        return data_files
    
    @classmethod
    def _deserialize_nifti_data(cls, context: VisualizationContext, 
                               zipf: zipfile.ZipFile, state_dict: Dict) -> None:
        """Deserialize NIFTI data from ZIP file and restore state.
        
        Args:
            context: The visualization context to restore
            zipf: The ZIP file containing data
            state_dict: The serialized state dictionary
        """
        # Load NIFTI data files
        func_img = anat_img = mask_img = None
        
        # Try to load func image
        if 'data/func_img.nii.gz' in zipf.namelist():
            with zipf.open('data/func_img.nii.gz') as f:
                func_data = f.read()
                func_img = nib.Nifti1Image.from_bytes(func_data)
                logger.info("Loaded func_img from state file")                
        
        # Try to load anat image
        if 'data/anat_img.nii.gz' in zipf.namelist():
            with zipf.open('data/anat_img.nii.gz') as f:
                anat_data = f.read()
                anat_img = nib.Nifti1Image.from_bytes(anat_data)
                logger.info("Loaded anat_img from state file")
                
        # Try to load mask image
        if 'data/mask_img.nii.gz' in zipf.namelist():
            with zipf.open('data/mask_img.nii.gz') as f:
                mask_data = f.read()
                mask_img = nib.Nifti1Image.from_bytes(mask_data)
                logger.info("Loaded mask_img from state file")
        
        # Create the state with the loaded images
        if func_img:
            context.create_nifti_state(func_img, anat_img, mask_img)
            logger.info("Created NIFTI state from loaded data")
            
            # Load preprocessed data if available
            preproc_data = {}
            for filename in zipf.namelist():
                if filename.startswith('data/preproc_') and filename.endswith('.nii.gz'):
                    key = filename.replace('data/preproc_', '').replace('.nii.gz', '')
                    with zipf.open(filename) as f:
                        img_data = f.read()
                        img = nib.Nifti1Image.from_bytes(img_data)
                        preproc_data[key] = img
            
            if preproc_data:
                context._state.nifti_data_preprocessed = preproc_data
                context._state.fmri_preprocessed = True
                logger.info("Loaded preprocessed NIFTI data")
            
            # Now apply the saved state parameters on top of the newly created state
            cls._apply_state_dict(context._state, state_dict)
            logger.info("Applied state parameters")
        else:
            logger.warning("Failed to load NIFTI data from state file")
            raise ValueError("State file does not contain required func_img data")
    
    @classmethod
    def _deserialize_gifti_data(cls, context: VisualizationContext, 
                               zipf: zipfile.ZipFile, state_dict: Dict) -> None:
        """Deserialize GIFTI data from ZIP file and restore state.
        
        Args:
            context: The visualization context to restore
            zipf: The ZIP file containing data
            state_dict: The serialized state dictionary
        """
        # Load GIFTI data files
        left_func_img = right_func_img = left_mesh = right_mesh = None
        
        # Try to load left func image
        if 'data/left_func_img.gii' in zipf.namelist():
            with zipf.open('data/left_func_img.gii') as f:
                left_func_data = f.read()
                left_func_img = nib.GiftiImage.from_bytes(left_func_data)
                logger.info("Loaded left_func_img from state file")
        
        # Try to load right func image
        if 'data/right_func_img.gii' in zipf.namelist():
            with zipf.open('data/right_func_img.gii') as f:
                right_func_data = f.read()
                right_func_img = nib.GiftiImage.from_bytes(right_func_data)
                logger.info("Loaded right_func_img from state file")
        
        # Try to load left mesh
        if 'data/left_mesh.gii' in zipf.namelist():
            with zipf.open('data/left_mesh.gii') as f:
                left_mesh_data = f.read()
                left_mesh = nib.GiftiImage.from_bytes(left_mesh_data)
                logger.info("Loaded left_mesh from state file")
        
        # Try to load right mesh
        if 'data/right_mesh.gii' in zipf.namelist():
            with zipf.open('data/right_mesh.gii') as f:
                right_mesh_data = f.read()
                right_mesh = nib.GiftiImage.from_bytes(right_mesh_data)
                logger.info("Loaded right_mesh from state file")
                
        # Create the state with the loaded images
        if left_func_img or right_func_img:
            context.create_gifti_state(left_func_img, right_func_img, left_mesh, right_mesh)
            logger.info("Created GIFTI state from loaded data")
            
            # Load preprocessed data if available
            preproc_data = {}
            for filename in zipf.namelist():
                if filename.startswith('data/preproc_') and filename.endswith('.gii'):
                    key = filename.replace('data/preproc_', '').replace('.gii', '')
                    with zipf.open(filename) as f:
                        img_data = f.read()
                        img = nib.GiftiImage.from_bytes(img_data)
                        preproc_data[key] = img
            
            if preproc_data:
                context._state.gifti_data_preprocessed = preproc_data
                context._state.fmri_preprocessed = True
                logger.info("Loaded preprocessed GIFTI data")
            
            # Now apply the saved state parameters on top of the newly created state
            cls._apply_state_dict(context._state, state_dict)
            logger.info("Applied state parameters")
        else:
            logger.warning("Failed to load GIFTI data from state file")
            raise ValueError("State file does not contain required GIFTI func data")
    
    @classmethod
    def _apply_state_dict(cls, state: Union[NiftiVisualizationState, GiftiVisualizationState], 
                     state_dict: Dict) -> None:
        """Apply serialized state dictionary to a visualization state object."""
        from findviz.viz.viewer.state.components import (
            TimeCoursePlotOptions, TaskDesignPlotOptions, 
            TimeMarkerPlotOptions, AnnotationMarkerPlotOptions,
            FmriPlotOptions, DistancePlotOptions, TimeCourseGlobalPlotOptions,
            TimeCourseColor
        )
        # Apply state parameters
        for key, value in state_dict.items():
            if key in cls.EXCLUDE_FIELDS:
                continue
            
            # Handle special cases
            # handle set
            if isinstance(value, dict) and value.get("__type__") == "set":
                # Special handling for TimeCourseColor set
                if value.get("__item_type__") == "TimeCourseColor":
                    color_set = set()
                    for color_data in value.get("values", []):
                        try:
                            # Try to create a TimeCourseColor from the value
                            color_set.add(TimeCourseColor(color_data))
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Failed to create TimeCourseColor from {color_data}: {e}")
                    setattr(state, key, color_set)
                else:
                    # Regular set
                    setattr(state, key, set(value.get("values", [])))
            # Special handling for ts_labels to avoid triggering the setter
            elif key == 'ts_labels':
                setattr(state, '_ts_labels', value)
            # handle time course plot options
            elif key == 'ts_plot_options':
                # Restore time course plot options
                options = {}
                if value is not None:
                    for ts_id, ts_opts in value.items():
                        plot_opt = TimeCoursePlotOptions()
                        plot_opt.update_from_dict(ts_opts)
                        options[ts_id] = plot_opt
                else:
                    options = None

                setattr(state, key, options)
            elif key == 'task_plot_options':
                # Restore task design plot options
                options = {}
                if value is not None:
                    for task_id, task_opts in value.items():
                        plot_opt = TaskDesignPlotOptions()
                        plot_opt.update_from_dict(task_opts)
                        options[task_id] = plot_opt
                else:
                    options = None

                setattr(state, key, options)
            elif key == 'time_marker_plot_options':
                options = TimeMarkerPlotOptions()
                if value is not None:
                    options.update_from_dict(value)
                else:
                    options = None

                setattr(state, key, options)
            elif key == 'annotation_marker_plot_options':
                options = AnnotationMarkerPlotOptions()
                if value is not None:
                    options.update_from_dict(value)
                else:
                    options = None

                setattr(state, key, options)
            elif key == 'fmri_plot_options' or key == 'preprocessed_fmri_plot_options':
                options = FmriPlotOptions()
                if value is not None:
                    options.update_from_dict(value)
                else:
                    options = None

                setattr(state, key, options)
            elif key == 'distance_plot_options':
                options = DistancePlotOptions()
                if value is not None:
                    options.update_from_dict(value)
                else:
                    options = None

                setattr(state, key, options)
            elif key == 'time_course_global_plot_options':
                options = TimeCourseGlobalPlotOptions()
                if value is not None:
                    options.update_from_dict(value)
                else:
                    options = None

                setattr(state, key, options)
            # handle numpy array
            elif isinstance(value, dict) and value.get("__type__") == "numpy_array":
                setattr(state, key, np.array(value.get("values")))
            # handle list
            elif isinstance(value, dict) and value.get("__type__") == "list":
                setattr(state, key, cls._deserialize_list(value.get("values")))
            # handle dict
            elif isinstance(value, dict) and value.get("__type__") == "dict":
                setattr(state, key, cls._deserialize_dict(value.get("values")))
            else:
                # For basic types
                try:
                    setattr(state, key, value)
                except Exception as e:
                    logger.warning(f"Failed to set {key}: {str(e)}")