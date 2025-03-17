"""
Backend Data Management with DataManager singleton pattern.

This module provides a centralized data management system for the FIND viewer,
handling multiple visualization states (both NIFTI and GIFTI). 
It implements a singleton pattern to ensure consistent state across the application.

Classes:
    DataManager: Singleton manager for visualization state
"""

from typing import Dict, Optional, ClassVar, List

from findviz.logger_config import setup_logger
from findviz.viz.viewer.context import VisualizationContext
from findviz.viz.viewer.state.state_file import StateFile
from findviz.viz import exception
logger = setup_logger(__name__)


class DataManager:
    """Singleton manager for visualization state with support for multiple contexts.
    
    This class implements the singleton pattern to maintain a single source of truth
    for the visualization state across the entire application. It handles both NIFTI
    and GIFTI data types and their associated metadata.
    
    Attributes:
        _instance (ClassVar[Optional['DataManager']]): Singleton instance
        _contexts (Dict[str, VisualizationContext]): Dictionary mapping context IDs to contexts
        _active_context_id (str): ID of the currently active context
    
    Methods:
        __new__: Create or return the singleton instance
        active_context: Get the currently active visualization context
        create_analysis_context: Create a new context for analysis results
        get_context: Get a context by its ID
        get_context_ids: Get all available context IDs
        load: Load a scene file
        get_active_context_id: Get the ID of the currently active context
        save: save the current scene
        switch_context: Switch the active context to the specified ID
    """
    _instance: ClassVar[Optional['DataManager']] = None
    _contexts: Dict[str, VisualizationContext]
    _active_context_id: str
    
    def __new__(cls) -> 'DataManager':
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize instance attributes 
            cls._instance._contexts = {}  # Dictionary to store multiple visualization contexts
            cls._instance._active_context_id = "main"  # Default context is "main"
            cls._instance._contexts["main"] = VisualizationContext("main")
            logger.info("Data manager initialized")
        return cls._instance
    
    @property
    def ctx(self) -> VisualizationContext:
        """Short alias for the currently active visualization context."""
        return self._contexts[self._active_context_id]
    
    @property
    def _state(self) -> VisualizationContext:
        """Private property to get the currently active visualization state."""
        return self._contexts[self._active_context_id]

    
    def create_analysis_context(self, analysis_name: str) -> str:
        """Create a new context for analysis results.
        
        Arguments:
            analysis_name: Name of the analysis for context identification
            
        Returns:
            str: The ID of the newly created context
        """
        context_id = analysis_name
        self._contexts[context_id] = VisualizationContext(context_id)
        logger.info(f"Created new analysis context: {context_id}")
        return context_id
    
    def get_context(self, context_id: str) -> VisualizationContext:
        """Get a context by its ID.
        
        Arguments:
            context_id: The ID of the context to get

        Returns:
            VisualizationContext: The context with the specified ID
            
        Raises:
            ValueError: If the context does not exist
        """
        if context_id not in self._contexts:
            raise ValueError(f"Context {context_id} does not exist")
        return self._contexts[context_id]

    def get_context_ids(self) -> List[str]:
        """Get all available context IDs.
        
        Returns:
            List[str]: List of context IDs
        """
        return list(self._contexts.keys())
    
    def get_active_context_id(self) -> str:
        """Get the ID of the currently active context.
        
        Returns:
            str: ID of the active context
        """
        return self._active_context_id
    
    def load(self, scene_file_data: bytes) -> None:
        """Load a scene file and replace current context.
        
        Arguments:
            scene_file_data: The data to load
        """
        try:
            # Deserialize context from bytes
            context = StateFile.deserialize_from_bytes(scene_file_data)

            # Replace the main context with the loaded one
            self.switch_context("main")
            self._contexts["main"] = context
            logger.info(f"Loaded context from file with ID: {context.context_id}")
        # handle version incompatibility error higher up
        except exception.FVStateVersionIncompatibleError as e:
            raise
        except ValueError as e:
            logger.error(f"Error loading state file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during state loading: {str(e)}")
            raise ValueError(f"Failed to load state: {str(e)}")

    def save(self, file_name: str = "scene.fvstate") -> bytes:
        """Save the current scene to a .fvstate file and return the serialized data.
        
        Arguments:
            file_name: Name of the file to save to
            
        Returns:
            bytes: Serialized context data that can be served as a download
        """        
        # Get current context
        context = self.get_context(self._active_context_id)
        
        # Serialize context using our custom format
        serialized_data = StateFile.serialize_to_bytes(context)
        logger.info(f"Prepared context {self._active_context_id} for download as {file_name}")
        
        return serialized_data

    def switch_context(self, context_id: str) -> None:
        """Switch the active context to the specified ID.
        
        Arguments:
            context_id: The ID of the context to switch to
        """
        if context_id not in self._contexts:
            raise ValueError(f"Context {context_id} does not exist")
        # get original active context
        original_context_id = self._active_context_id
        # log switch if it's a new context
        if original_context_id != context_id:
            logger.info(f"Switched from {original_context_id} to {context_id}") 

        # switch to new context
        self._active_context_id = context_id       
   