"""
Base plugin system for extensible components.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel
import importlib
import inspect
from loguru import logger


class PluginType(str, Enum):
    """Types of plugins supported."""
    ADAPTER = "adapter"
    TRANSFORMER = "transformer"
    MIDDLEWARE = "middleware"
    HOOK = "hook"
    VALIDATOR = "validator"
    FORMATTER = "formatter"


class PluginMetadata(BaseModel):
    """Metadata for plugin registration."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = []
    config_schema: Optional[Dict[str, Any]] = None


class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize plugin with configuration."""
        self.config = config or {}
        self._metadata: Optional[PluginMetadata] = None
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        return True
    
    def get_dependencies(self) -> List[str]:
        """Get list of required dependencies."""
        return self.metadata.dependencies


class PluginRegistry:
    """Registry for managing plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, Type[BasePlugin]] = {}
        self._instances: Dict[str, BasePlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
    
    def register(self, plugin_class: Type[BasePlugin], name: Optional[str] = None) -> None:
        """Register a plugin class."""
        if not issubclass(plugin_class, BasePlugin):
            raise ValueError(f"Plugin must inherit from BasePlugin: {plugin_class}")
        
        # Create temporary instance to get metadata
        temp_instance = plugin_class()
        metadata = temp_instance.metadata
        plugin_name = name or metadata.name
        
        if plugin_name in self._plugins:
            logger.warning(f"Plugin '{plugin_name}' already registered, overwriting")
        
        self._plugins[plugin_name] = plugin_class
        self._metadata[plugin_name] = metadata
        
        logger.info(f"Registered plugin: {plugin_name} (type: {metadata.plugin_type})")
    
    def unregister(self, name: str) -> None:
        """Unregister a plugin."""
        if name in self._instances:
            self._instances[name].cleanup()
            del self._instances[name]
        
        if name in self._plugins:
            del self._plugins[name]
        
        if name in self._metadata:
            del self._metadata[name]
        
        logger.info(f"Unregistered plugin: {name}")
    
    def get_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> BasePlugin:
        """Get plugin instance."""
        if name not in self._plugins:
            raise ValueError(f"Plugin not found: {name}")
        
        # Return existing instance if no config provided
        if name in self._instances and config is None:
            return self._instances[name]
        
        # Create new instance
        plugin_class = self._plugins[name]
        instance = plugin_class(config)
        
        # Validate configuration
        if config and not instance.validate_config(config):
            raise ValueError(f"Invalid configuration for plugin: {name}")
        
        instance.initialize()
        self._instances[name] = instance
        
        return instance
    
    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[str]:
        """List registered plugins."""
        if plugin_type is None:
            return list(self._plugins.keys())
        
        return [
            name for name, metadata in self._metadata.items()
            if metadata.plugin_type == plugin_type
        ]
    
    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """Get plugin metadata."""
        return self._metadata.get(name)
    
    def load_from_module(self, module_path: str) -> None:
        """Load plugins from a module."""
        try:
            module = importlib.import_module(module_path)
            
            # Find all plugin classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    self.register(obj)
                    
        except ImportError as e:
            logger.error(f"Failed to load plugin module {module_path}: {e}")
            raise
    
    def load_from_directory(self, directory: str) -> None:
        """Load all plugins from a directory."""
        import os
        import sys
        
        if not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")
        
        # Add directory to Python path
        if directory not in sys.path:
            sys.path.insert(0, directory)
        
        # Load all Python files as modules
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    self.load_from_module(module_name)
                except Exception as e:
                    logger.warning(f"Failed to load plugin from {filename}: {e}")


# Global plugin registry
plugin_registry = PluginRegistry()
