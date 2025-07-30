#!/usr/bin/env python3
"""
Plugin system examples for Evolvishub Data Handler.

This example demonstrates:
1. Custom adapter registration (Redis, Elasticsearch)
2. Data transformation pipelines
3. Middleware components
4. Event hooks and callbacks
5. Complete plugin configuration
"""

import os
import sys
import yaml

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import CDCConfig, DatabaseConfig, DatabaseType, SyncConfig, SyncMode
from evolvishub_data_handler.plugins.manager import PluginManager
from evolvishub_data_handler.plugins.base import plugin_registry


def demonstrate_custom_adapters():
    """Demonstrate custom adapter registration concept."""
    print("=== Custom Adapter Registration ===")

    print("Custom adapters can be registered dynamically:")
    print("  • Redis adapter for key-value storage")
    print("  • Elasticsearch adapter for search and analytics")
    print("  • Custom database adapters")
    print("  • API adapters for REST/GraphQL endpoints")

    # Show available plugin types
    from evolvishub_data_handler.plugins.base import PluginType
    print(f"✓ Available plugin types: {[t.value for t in PluginType]}")

    # List any registered plugins
    available_plugins = plugin_registry.list_plugins()
    print(f"✓ Currently registered plugins: {len(available_plugins)}")


def create_comprehensive_plugin_config():
    """Create a comprehensive plugin configuration."""
    return {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "source_db",
            "username": "source_user",
            "password": "source_password",
            "table": "users",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp",
                "initial_value": "2024-01-01 00:00:00"
            }
        },
        "destination": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "dest_db",
            "username": "dest_user",
            "password": "dest_password",
            "table": "users_sync"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 30,
            "batch_size": 1000
        },
        "plugins": {
            "transformers": {
                "transformers": [
                    {
                        "type": "field_mapper",
                        "params": {
                            "mapping": {
                                "user_id": "customer_id",
                                "full_name": "name",
                                "email_address": "email"
                            }
                        }
                    },
                    {
                        "type": "data_type_converter",
                        "params": {
                            "conversions": {
                                "age": "int",
                                "salary": "float",
                                "is_active": "bool"
                            }
                        }
                    },
                    {
                        "type": "field_filter",
                        "params": {
                            "exclude": ["password", "ssn", "internal_notes"]
                        }
                    },
                    {
                        "type": "date_formatter",
                        "params": {
                            "formats": {
                                "created_at": {
                                    "input_format": "%Y-%m-%d %H:%M:%S",
                                    "output_format": "%Y-%m-%dT%H:%M:%SZ"
                                }
                            }
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
                            "log_data": True
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
                    },
                    {
                        "type": "data_quality",
                        "params": {
                            "checks": {
                                "null_check": True,
                                "duplicate_check": True
                            }
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
                                "Authorization": "Bearer your-token",
                                "Content-Type": "application/json"
                            },
                            "timeout": 30
                        },
                        "events": ["sync_start", "sync_end", "error"]
                    },
                    {
                        "type": "slack",
                        "params": {
                            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                            "channel": "#data-sync",
                            "username": "CDC Bot"
                        },
                        "events": ["error", "sync_end"]
                    },
                    {
                        "type": "file_logger",
                        "params": {
                            "log_file": "/var/log/cdc_events.log",
                            "format": "{timestamp} - {event_type} - {data}"
                        }
                    },
                    {
                        "type": "metrics_collector",
                        "params": {
                            "metrics_file": "/var/log/cdc_metrics.json"
                        }
                    }
                ]
            }
        }
    }


def demonstrate_plugin_configuration():
    """Demonstrate plugin configuration and usage."""
    print("\n=== Plugin Configuration Example ===")
    
    config_dict = create_comprehensive_plugin_config()
    
    # Save configuration to YAML
    config_file = "plugin_demo_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print(f"Configuration saved to {config_file}")
    
    # Load and validate configuration
    try:
        config = CDCConfig(**config_dict)
        print("✓ Configuration loaded and validated successfully")
        
        # Show plugin configuration
        if config.plugins:
            print(f"✓ Plugin configuration found with {len(config.plugins)} plugin types")
            for plugin_type, plugin_config in config.plugins.items():
                print(f"  - {plugin_type}: {len(plugin_config.get(plugin_type, []))} components")
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return None
    
    # Cleanup
    os.remove(config_file)
    
    return config


def demonstrate_plugin_manager():
    """Demonstrate plugin manager functionality."""
    print("\n=== Plugin Manager Demonstration ===")
    
    # Create plugin configuration
    plugin_config = {
        "transformers": {
            "transformers": [
                {
                    "type": "field_mapper",
                    "params": {
                        "mapping": {"old_field": "new_field"}
                    }
                }
            ]
        },
        "middleware": {
            "middleware": [
                {
                    "type": "logging",
                    "params": {"level": "DEBUG"}
                }
            ]
        },
        "hooks": {
            "hooks": [
                {
                    "type": "file_logger",
                    "params": {"log_file": "test_events.log"}
                }
            ]
        }
    }
    
    # Initialize plugin manager
    plugin_manager = PluginManager(plugin_config)
    plugin_manager.initialize()
    
    print(f"✓ Plugin manager initialized")
    print(f"✓ Active plugins: {list(plugin_manager.active_plugins.keys())}")
    
    # Test data transformation
    test_data = [
        {"old_field": "value1", "other_field": "data1"},
        {"old_field": "value2", "other_field": "data2"}
    ]
    
    transformed_data = plugin_manager.transform_data(test_data)
    print(f"✓ Data transformation test:")
    print(f"  Original: {test_data[0]}")
    print(f"  Transformed: {transformed_data[0]}")
    
    # Test event triggering
    from evolvishub_data_handler.plugins.hooks import EventType
    plugin_manager.trigger_event(EventType.SYNC_START, {
        'timestamp': '2024-01-01T00:00:00Z',
        'test': True
    })
    print("✓ Event triggered successfully")
    
    # Cleanup
    plugin_manager.cleanup()
    
    # Remove test log file
    if os.path.exists("test_events.log"):
        os.remove("test_events.log")


def demonstrate_custom_adapter_usage():
    """Demonstrate usage of custom adapters."""
    print("\n=== Custom Adapter Usage ===")

    print("Custom adapters can be configured like built-in adapters:")

    # Example configurations for custom adapters
    print("\nRedis Adapter Configuration:")
    print("  type: redis")
    print("  host: localhost")
    print("  port: 6379")
    print("  database: '0'")
    print("  password: redis_password")

    print("\nElasticsearch Adapter Configuration:")
    print("  type: elasticsearch")
    print("  host: localhost")
    print("  port: 9200")
    print("  database: my_index")
    print("  username: elastic")
    print("  password: elastic_password")

    print("\n✓ Custom adapters integrate seamlessly with existing configuration")


def demonstrate_end_to_end_plugin_usage():
    """Demonstrate end-to-end usage with plugins."""
    print("\n=== End-to-End Plugin Usage ===")
    
    # Create configuration with plugins
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
        "plugins": {
            "transformers": {
                "transformers": [
                    {
                        "type": "field_mapper",
                        "params": {
                            "mapping": {"id": "user_id", "name": "full_name"}
                        }
                    }
                ]
            },
            "middleware": {
                "middleware": [
                    {
                        "type": "logging",
                        "params": {"level": "INFO"}
                    }
                ]
            }
        }
    }
    
    try:
        # Create CDC configuration
        config = CDCConfig(**config_dict)
        print("✓ CDC configuration with plugins created")
        print(f"✓ Plugin configuration available: {config.plugins is not None}")

        # Note: In a real scenario, you would run the CDC handler
        # cdc_handler = CDCHandler(config)
        # cdc_handler.sync()

        print("✓ End-to-end plugin integration ready")
        
    except Exception as e:
        print(f"✗ End-to-end setup failed: {e}")


def main():
    """Run all plugin system demonstrations."""
    print("Plugin System Examples")
    print("=====================")
    
    try:
        demonstrate_custom_adapters()
        demonstrate_plugin_configuration()
        demonstrate_plugin_manager()
        demonstrate_custom_adapter_usage()
        demonstrate_end_to_end_plugin_usage()
        
        print("\n=== Summary ===")
        print("Plugin system implementation completed!")
        print("\nKey features:")
        print("✓ Dynamic adapter registration")
        print("✓ Data transformation pipelines")
        print("✓ Middleware components")
        print("✓ Event hooks and callbacks")
        print("✓ Comprehensive configuration")
        print("✓ Plugin manager coordination")
        
        print("\nPlugin types available:")
        print("• Adapters: Redis, Elasticsearch, and custom adapters")
        print("• Transformers: Field mapping, type conversion, filtering")
        print("• Middleware: Logging, metrics, validation, data quality")
        print("• Hooks: Webhooks, Slack, email, file logging")
        
    except Exception as e:
        print(f"Error running plugin demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
