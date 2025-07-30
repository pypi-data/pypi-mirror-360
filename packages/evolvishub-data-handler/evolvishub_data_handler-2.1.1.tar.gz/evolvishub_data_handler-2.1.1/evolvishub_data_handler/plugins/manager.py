"""
Plugin manager for coordinating all plugins.
"""

from typing import Any, Dict, List, Optional
from .base import BasePlugin, PluginRegistry, PluginType, plugin_registry
from .adapters import AdapterPlugin
from .transformers import TransformerPlugin
from .middleware import MiddlewarePlugin
from .hooks import HookPlugin, EventType
from loguru import logger


class PluginManager:
    """Central manager for all plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize plugin manager."""
        self.config = config or {}
        self.registry = plugin_registry
        self.active_plugins: Dict[str, BasePlugin] = {}
        
        # Core plugin instances
        self.adapter_plugin: Optional[AdapterPlugin] = None
        self.transformer_plugin: Optional[TransformerPlugin] = None
        self.middleware_plugin: Optional[MiddlewarePlugin] = None
        self.hook_plugin: Optional[HookPlugin] = None
    
    def initialize(self) -> None:
        """Initialize all plugins."""
        logger.info("Initializing plugin manager")
        
        # Load external plugins if configured
        self._load_external_plugins()
        
        # Initialize core plugins
        self._initialize_core_plugins()
        
        # Initialize custom plugins
        self._initialize_custom_plugins()
        
        logger.info(f"Plugin manager initialized with {len(self.active_plugins)} plugins")
    
    def cleanup(self) -> None:
        """Cleanup all plugins."""
        logger.info("Cleaning up plugin manager")
        
        for plugin_name, plugin in self.active_plugins.items():
            try:
                plugin.cleanup()
                logger.debug(f"Cleaned up plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin_name}: {e}")
        
        self.active_plugins.clear()
        self.adapter_plugin = None
        self.transformer_plugin = None
        self.middleware_plugin = None
        self.hook_plugin = None
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get active plugin by name."""
        return self.active_plugins.get(name)
    
    def trigger_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Trigger an event through the hook plugin."""
        if self.hook_plugin:
            self.hook_plugin.trigger_event(event_type, data)
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform data through the transformer plugin."""
        if self.transformer_plugin:
            return self.transformer_plugin.transform_data(data)
        return data
    
    def process_middleware_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process middleware before read."""
        if self.middleware_plugin:
            return self.middleware_plugin.process_before_read(config)
        return config
    
    def process_middleware_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process middleware after read."""
        if self.middleware_plugin:
            return self.middleware_plugin.process_after_read(data)
        return data
    
    def process_middleware_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process middleware before write."""
        if self.middleware_plugin:
            return self.middleware_plugin.process_before_write(data)
        return data
    
    def process_middleware_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """Process middleware after write."""
        if self.middleware_plugin:
            self.middleware_plugin.process_after_write(data, result)
    
    def _load_external_plugins(self) -> None:
        """Load external plugins from configuration."""
        external_plugins = self.config.get('external_plugins', {})
        
        # Load from modules
        modules = external_plugins.get('modules', [])
        for module_path in modules:
            try:
                self.registry.load_from_module(module_path)
                logger.info(f"Loaded plugins from module: {module_path}")
            except Exception as e:
                logger.error(f"Failed to load plugins from module {module_path}: {e}")
        
        # Load from directories
        directories = external_plugins.get('directories', [])
        for directory_path in directories:
            try:
                self.registry.load_from_directory(directory_path)
                logger.info(f"Loaded plugins from directory: {directory_path}")
            except Exception as e:
                logger.error(f"Failed to load plugins from directory {directory_path}: {e}")
    
    def _initialize_core_plugins(self) -> None:
        """Initialize core plugins."""
        # Initialize adapter plugin
        adapter_config = self.config.get('adapters', {})
        if adapter_config:
            self.adapter_plugin = AdapterPlugin(adapter_config)
            self.adapter_plugin.initialize()
            self.active_plugins['adapters'] = self.adapter_plugin
        
        # Initialize transformer plugin
        transformer_config = self.config.get('transformers', {})
        if transformer_config:
            self.transformer_plugin = TransformerPlugin(transformer_config)
            self.transformer_plugin.initialize()
            self.active_plugins['transformers'] = self.transformer_plugin
        
        # Initialize middleware plugin
        middleware_config = self.config.get('middleware', {})
        if middleware_config:
            self.middleware_plugin = MiddlewarePlugin(middleware_config)
            self.middleware_plugin.initialize()
            self.active_plugins['middleware'] = self.middleware_plugin
        
        # Initialize hook plugin
        hooks_config = self.config.get('hooks', {})
        if hooks_config:
            self.hook_plugin = HookPlugin(hooks_config)
            self.hook_plugin.initialize()
            self.active_plugins['hooks'] = self.hook_plugin
    
    def _initialize_custom_plugins(self) -> None:
        """Initialize custom plugins from registry."""
        custom_plugins = self.config.get('custom_plugins', {})
        
        for plugin_name, plugin_config in custom_plugins.items():
            try:
                plugin = self.registry.get_plugin(plugin_name, plugin_config)
                self.active_plugins[plugin_name] = plugin
                logger.info(f"Initialized custom plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to initialize custom plugin {plugin_name}: {e}")
    
    def list_available_plugins(self) -> Dict[str, List[str]]:
        """List all available plugins by type."""
        result = {}
        
        for plugin_type in PluginType:
            result[plugin_type.value] = self.registry.list_plugins(plugin_type)
        
        return result
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a plugin."""
        metadata = self.registry.get_metadata(plugin_name)
        if metadata:
            return metadata.dict()
        return None
    
    def register_plugin(self, plugin_class, name: Optional[str] = None) -> None:
        """Register a new plugin class."""
        self.registry.register(plugin_class, name)
    
    def create_plugin_config_template(self) -> Dict[str, Any]:
        """Create a template configuration for all plugins."""
        return {
            "external_plugins": {
                "modules": [
                    "my_custom_plugins.adapters",
                    "my_custom_plugins.transformers"
                ],
                "directories": [
                    "/path/to/plugin/directory"
                ]
            },
            "adapters": {
                "auto_register": True,
                "adapters": {
                    "redis": {
                        "module": "my_plugins.redis_adapter",
                        "class": "RedisAdapter"
                    },
                    "elasticsearch": {
                        "module": "my_plugins.elasticsearch_adapter", 
                        "class": "ElasticsearchAdapter"
                    }
                }
            },
            "transformers": {
                "transformers": [
                    {
                        "type": "field_mapper",
                        "params": {
                            "mapping": {
                                "old_field": "new_field",
                                "user_id": "customer_id"
                            }
                        }
                    },
                    {
                        "type": "data_type_converter",
                        "params": {
                            "conversions": {
                                "age": "int",
                                "salary": "float",
                                "created_at": "datetime"
                            }
                        }
                    },
                    {
                        "type": "field_filter",
                        "params": {
                            "include": ["id", "name", "email"],
                            "exclude": ["password", "ssn"]
                        }
                    }
                ]
            },
            "middleware": {
                "middleware": [
                    {
                        "type": "logging",
                        "params": {
                            "level": "INFO",
                            "log_data": False
                        }
                    },
                    {
                        "type": "metrics",
                        "params": {}
                    },
                    {
                        "type": "validation",
                        "params": {
                            "rules": {
                                "email": {
                                    "required": True,
                                    "type": "string"
                                },
                                "age": {
                                    "type": "number",
                                    "min": 0,
                                    "max": 150
                                }
                            },
                            "strict": False
                        }
                    }
                ]
            },
            "hooks": {
                "hooks": [
                    {
                        "type": "webhook",
                        "params": {
                            "url": "https://api.example.com/webhook",
                            "headers": {
                                "Authorization": "Bearer token"
                            }
                        },
                        "events": ["sync_start", "sync_end", "error"]
                    },
                    {
                        "type": "slack",
                        "params": {
                            "webhook_url": "https://hooks.slack.com/...",
                            "channel": "#data-sync",
                            "username": "CDC Bot"
                        },
                        "events": ["error"]
                    },
                    {
                        "type": "file_logger",
                        "params": {
                            "log_file": "/var/log/cdc_events.log"
                        }
                    }
                ]
            },
            "custom_plugins": {
                "my_custom_plugin": {
                    "param1": "value1",
                    "param2": "value2"
                }
            }
        }
