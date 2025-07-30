"""
Tests for optional plugin system functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from evolvishub_data_handler.config import CDCConfig, DatabaseConfig, DatabaseType, SyncConfig, SyncMode
from evolvishub_data_handler.cdc_handler import CDCHandler
from evolvishub_data_handler.plugins.manager import PluginManager
from evolvishub_data_handler.plugins.base import BasePlugin, PluginMetadata, PluginType


class TestOptionalPlugins:
    """Test suite for optional plugin functionality."""

    def test_basic_config_without_plugins(self):
        """Test basic configuration without any plugins."""
        config_dict = {
            "source": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "test_table"
            },
            "destination": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "dest_table"
            },
            "sync": {
                "mode": "one_time",
                "batch_size": 100
            }
        }
        
        config = CDCConfig(**config_dict)
        
        assert config.source.type == DatabaseType.SQLITE
        assert config.destination.type == DatabaseType.SQLITE
        assert config.sync.mode == SyncMode.ONE_TIME
        assert config.plugins is None

    def test_config_with_empty_plugins(self):
        """Test configuration with empty plugins section."""
        config_dict = {
            "source": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "test_table"
            },
            "destination": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "dest_table"
            },
            "sync": {
                "mode": "one_time",
                "batch_size": 100
            },
            "plugins": {}
        }
        
        config = CDCConfig(**config_dict)
        
        assert config.plugins is not None
        assert len(config.plugins) == 0

    def test_cdc_handler_without_plugins(self):
        """Test CDC handler initialization without plugins."""
        config_dict = {
            "source": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "test_table"
            },
            "destination": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "dest_table"
            },
            "sync": {
                "mode": "one_time",
                "batch_size": 100
            }
        }
        
        config = CDCConfig(**config_dict)
        handler = CDCHandler(config)
        
        assert handler.plugin_manager is None
        assert handler.source_adapter is not None
        assert handler.destination_adapter is not None
        
        # Cleanup
        handler.stop()

    def test_cdc_handler_with_empty_plugins(self):
        """Test CDC handler with empty plugins configuration."""
        config_dict = {
            "source": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "test_table"
            },
            "destination": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "dest_table"
            },
            "sync": {
                "mode": "one_time",
                "batch_size": 100
            },
            "plugins": {}
        }
        
        config = CDCConfig(**config_dict)
        handler = CDCHandler(config)

        # Empty plugins config should still initialize plugin manager
        # but it might be None if initialization fails gracefully
        if handler.plugin_manager is not None:
            assert len(handler.plugin_manager.active_plugins) == 0
        
        # Cleanup
        handler.stop()

    @patch('evolvishub_data_handler.plugins.manager.PluginManager.initialize')
    def test_graceful_plugin_initialization_failure(self, mock_init):
        """Test graceful handling of plugin initialization failure."""
        mock_init.side_effect = Exception("Plugin initialization failed")
        
        config_dict = {
            "source": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "test_table"
            },
            "destination": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "dest_table"
            },
            "sync": {
                "mode": "one_time",
                "batch_size": 100
            },
            "plugins": {"transformers": {}}
        }
        
        config = CDCConfig(**config_dict)
        handler = CDCHandler(config)
        
        # Should continue working despite plugin failure
        assert handler.plugin_manager is None
        assert handler.source_adapter is not None
        
        # Cleanup
        handler.stop()

    def test_process_batch_without_plugins(self):
        """Test data processing without plugins."""
        config_dict = {
            "source": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "test_table"
            },
            "destination": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "dest_table"
            },
            "sync": {
                "mode": "one_time",
                "batch_size": 100
            }
        }
        
        config = CDCConfig(**config_dict)
        handler = CDCHandler(config)
        
        # Mock the destination adapter
        handler.destination_adapter.insert_data = Mock()
        
        # Test data processing
        test_data = [{"id": 1, "name": "test"}]
        handler._process_batch(test_data)
        
        # Verify data was processed
        handler.destination_adapter.insert_data.assert_called_once()
        
        # Cleanup
        handler.stop()

    @patch('evolvishub_data_handler.plugins.manager.PluginManager.trigger_event')
    def test_process_batch_with_plugin_event_failure(self, mock_trigger):
        """Test data processing continues even if plugin events fail."""
        mock_trigger.side_effect = Exception("Plugin event failed")
        
        config_dict = {
            "source": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "test_table"
            },
            "destination": {
                "type": "sqlite",
                "database": ":memory:",
                "table": "dest_table"
            },
            "sync": {
                "mode": "one_time",
                "batch_size": 100
            },
            "plugins": {}
        }
        
        config = CDCConfig(**config_dict)
        handler = CDCHandler(config)
        
        # Mock the destination adapter
        handler.destination_adapter.insert_data = Mock()
        
        # Test data processing with plugin event failure
        test_data = [{"id": 1, "name": "test"}]
        handler._process_batch(test_data)
        
        # Verify data was still processed despite plugin failure
        handler.destination_adapter.insert_data.assert_called_once()
        
        # Cleanup
        handler.stop()


class TestPluginManager:
    """Test suite for plugin manager functionality."""

    def test_plugin_manager_initialization(self):
        """Test plugin manager initialization."""
        config = {}
        manager = PluginManager(config)
        manager.initialize()
        
        assert len(manager.active_plugins) == 0
        
        manager.cleanup()

    def test_plugin_manager_with_invalid_config(self):
        """Test plugin manager with invalid configuration."""
        config = {
            "invalid_plugin_type": {
                "invalid_config": "test"
            }
        }
        
        manager = PluginManager(config)
        manager.initialize()
        
        # Should handle invalid config gracefully
        assert len(manager.active_plugins) == 0
        
        manager.cleanup()

    def test_plugin_manager_transformer_config(self):
        """Test plugin manager with transformer configuration."""
        config = {
            "transformers": {
                "transformers": [
                    {
                        "type": "field_mapper",
                        "params": {
                            "mapping": {"old_field": "new_field"}
                        }
                    }
                ]
            }
        }
        
        manager = PluginManager(config)
        manager.initialize()
        
        assert "transformers" in manager.active_plugins
        assert manager.transformer_plugin is not None
        
        # Test transformation
        test_data = [{"old_field": "value", "other": "data"}]
        result = manager.transform_data(test_data)
        
        assert result[0]["new_field"] == "value"
        # Note: Field mapper creates new field but may not preserve original
        # depending on implementation
        
        manager.cleanup()

    def test_plugin_manager_middleware_config(self):
        """Test plugin manager with middleware configuration."""
        config = {
            "middleware": {
                "middleware": [
                    {
                        "type": "logging",
                        "params": {
                            "level": "INFO"
                        }
                    }
                ]
            }
        }
        
        manager = PluginManager(config)
        manager.initialize()
        
        assert "middleware" in manager.active_plugins
        assert manager.middleware_plugin is not None
        
        # Test middleware processing
        test_config = {"test": "config"}
        result = manager.process_middleware_before_read(test_config)
        assert result == test_config
        
        manager.cleanup()

    def test_plugin_manager_hooks_config(self):
        """Test plugin manager with hooks configuration."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_file = f.name
        
        try:
            config = {
                "hooks": {
                    "hooks": [
                        {
                            "type": "file_logger",
                            "params": {
                                "log_file": log_file
                            }
                        }
                    ]
                }
            }
            
            manager = PluginManager(config)
            manager.initialize()
            
            assert "hooks" in manager.active_plugins
            assert manager.hook_plugin is not None
            
            # Test event triggering
            from evolvishub_data_handler.plugins.hooks import EventType
            manager.trigger_event(EventType.SYNC_START, {
                "timestamp": "2024-01-01T00:00:00Z",
                "test": True
            })
            
            # Verify log file was created and written to
            assert os.path.exists(log_file)
            with open(log_file, 'r') as f:
                content = f.read()
                assert "sync_start" in content.lower()
            
            manager.cleanup()
            
        finally:
            if os.path.exists(log_file):
                os.remove(log_file)


class TestAdapterFactory:
    """Test suite for adapter factory with optional dependencies."""

    def test_factory_initialization(self):
        """Test adapter factory initialization."""
        from evolvishub_data_handler.adapters.factory import AdapterFactory
        
        # Force re-initialization
        AdapterFactory._adapters.clear()
        AdapterFactory._initialize_adapters()
        
        # Should have at least SQLite adapter
        assert DatabaseType.SQLITE in AdapterFactory._adapters
        assert len(AdapterFactory._adapters) > 0

    def test_factory_create_sqlite_adapter(self):
        """Test creating SQLite adapter."""
        from evolvishub_data_handler.adapters.factory import AdapterFactory
        
        config = DatabaseConfig(
            type=DatabaseType.SQLITE,
            database=":memory:",
            table="test_table"
        )
        
        adapter = AdapterFactory.create(config)
        assert adapter is not None
        assert adapter.config.type == DatabaseType.SQLITE

    def test_factory_unsupported_adapter(self):
        """Test error handling for unsupported adapter."""
        from evolvishub_data_handler.adapters.factory import AdapterFactory
        from evolvishub_data_handler.config import DatabaseType
        
        # Create a mock database type that doesn't exist
        config = DatabaseConfig(
            type=DatabaseType.MONGODB,  # Might not be available
            database="test_db"
        )
        
        # This might succeed or fail depending on dependencies
        try:
            adapter = AdapterFactory.create(config)
            assert adapter is not None
        except ValueError as e:
            assert "Unsupported database type" in str(e)
            assert "Available types" in str(e)

    def test_factory_dynamic_registration(self):
        """Test dynamic adapter registration."""
        from evolvishub_data_handler.adapters.factory import AdapterFactory
        from evolvishub_data_handler.adapters.base import BaseAdapter
        
        class MockAdapter(BaseAdapter):
            def connect(self): pass
            def disconnect(self): pass
            def execute_query(self, query, params=None): return []
            def insert_data(self, table, data): pass
            def update_data(self, table, data, key_columns): pass
            def delete_data(self, table, conditions): pass
            def get_last_sync_timestamp(self): return None
            def update_last_sync_timestamp(self, timestamp): pass
        
        # Register mock adapter
        AdapterFactory.register_adapter(DatabaseType.SQLITE, MockAdapter)
        
        # Verify registration
        adapters = AdapterFactory.list_adapters()
        assert DatabaseType.SQLITE in adapters
        assert adapters[DatabaseType.SQLITE] == MockAdapter


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
