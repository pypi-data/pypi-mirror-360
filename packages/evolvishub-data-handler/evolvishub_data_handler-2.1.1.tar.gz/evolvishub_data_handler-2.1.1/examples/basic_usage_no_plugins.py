#!/usr/bin/env python3
"""
Basic usage example without any plugins.

This example demonstrates:
1. Simple database-to-database synchronization
2. No plugins required
3. Minimal configuration
4. Core functionality only
"""

import os
import sys
import yaml

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import CDCConfig
from evolvishub_data_handler.cdc_handler import CDCHandler


def create_basic_config():
    """Create a basic configuration without any plugins."""
    return {
        "source": {
            "type": "sqlite",
            "database": ":memory:",
            "table": "users",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp",
                "initial_value": "2024-01-01 00:00:00"
            }
        },
        "destination": {
            "type": "sqlite",
            "database": ":memory:",
            "table": "users_sync"
        },
        "sync": {
            "mode": "one_time",
            "batch_size": 1000
        }
        # Note: No 'plugins' section = basic functionality only
    }


def create_postgresql_config():
    """Create a PostgreSQL configuration example."""
    return {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "source_db",
            "username": "source_user",
            "password": "source_password",
            "table": "orders",
            "watermark": {
                "column": "created_at",
                "type": "timestamp",
                "initial_value": "2024-01-01 00:00:00"
            }
        },
        "destination": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "analytics_db",
            "username": "analytics_user",
            "password": "analytics_password",
            "table": "order_analytics"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 60,
            "batch_size": 500,
            "watermark_storage": {
                "type": "sqlite",
                "sqlite_path": "/var/lib/evolvishub/watermarks.db",
                "table_name": "sync_watermark"
            }
        }
    }


def demonstrate_basic_usage():
    """Demonstrate basic usage without plugins."""
    print("=== Basic Usage Without Plugins ===")
    
    # Create basic configuration
    config_dict = create_basic_config()
    
    print("Basic configuration (no plugins):")
    print(f"  - Source: {config_dict['source']['type']}")
    print(f"  - Destination: {config_dict['destination']['type']}")
    print(f"  - Sync mode: {config_dict['sync']['mode']}")
    print(f"  - Plugins section: {'plugins' in config_dict}")
    
    try:
        # Load configuration
        config = CDCConfig(**config_dict)
        print("✓ Configuration loaded successfully")
        
        # Initialize CDC handler
        handler = CDCHandler(config)
        print("✓ CDC handler initialized")
        print(f"  - Plugin manager active: {handler.plugin_manager is not None}")
        
        # Note: In a real scenario, you would run the sync
        # handler.sync()
        
        # Cleanup
        handler.stop()
        print("✓ Handler cleanup completed")
        
    except Exception as e:
        print(f"✗ Basic usage failed: {e}")


def demonstrate_yaml_configuration():
    """Demonstrate YAML configuration without plugins."""
    print("\n=== YAML Configuration Without Plugins ===")
    
    # Create PostgreSQL configuration
    config_dict = create_postgresql_config()
    
    # Save to YAML file
    config_file = "basic_config_no_plugins.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print(f"Configuration saved to {config_file}")
    
    # Show the configuration
    print("\nConfiguration contents:")
    with open(config_file, "r") as f:
        content = f.read()
        print(content)
    
    # Load and validate
    try:
        config = CDCConfig(**config_dict)
        print("✓ YAML configuration validated successfully")
        print(f"  - Source database: {config.source.database}")
        print(f"  - Destination database: {config.destination.database}")
        print(f"  - Watermark storage: {config.sync.watermark_storage.type.value}")
        
    except Exception as e:
        print(f"✗ YAML configuration validation failed: {e}")
    
    # Cleanup
    os.remove(config_file)


def demonstrate_cli_usage():
    """Demonstrate CLI usage without plugins."""
    print("\n=== CLI Usage Without Plugins ===")
    
    print("Command-line examples for basic usage:")
    print()
    print("1. One-time sync:")
    print("   evolvishub-cdc run -c config.yaml -m one_time")
    print()
    print("2. Continuous sync:")
    print("   evolvishub-cdc run -c config.yaml -m continuous")
    print()
    print("3. Cron-scheduled sync:")
    print("   evolvishub-cdc run -c config.yaml -m cron")
    print()
    print("4. With custom logging:")
    print("   evolvishub-cdc run -c config.yaml -l DEBUG --log-file sync.log")
    print()
    print("Note: All commands work the same with or without plugins!")


def demonstrate_benefits():
    """Demonstrate benefits of basic usage."""
    print("\n=== Benefits of Basic Usage ===")
    
    print("✅ Simplicity:")
    print("  • Minimal configuration required")
    print("  • No complex plugin setup")
    print("  • Easy to understand and maintain")
    
    print("\n✅ Performance:")
    print("  • No plugin overhead")
    print("  • Faster startup time")
    print("  • Lower memory usage")
    
    print("\n✅ Reliability:")
    print("  • Fewer dependencies")
    print("  • Less chance of configuration errors")
    print("  • Simpler troubleshooting")
    
    print("\n✅ Getting Started:")
    print("  • Perfect for proof of concepts")
    print("  • Quick setup for simple use cases")
    print("  • Easy migration from other tools")


def demonstrate_when_to_upgrade():
    """Show when to consider adding plugins."""
    print("\n=== When to Consider Adding Plugins ===")
    
    print("Consider plugins when you need:")
    print()
    print("🔄 Data Transformation:")
    print("  • Field name mapping")
    print("  • Data type conversions")
    print("  • Data validation and cleansing")
    
    print("\n📊 Advanced Monitoring:")
    print("  • Real-time metrics")
    print("  • Slack/email alerts")
    print("  • Performance monitoring")
    
    print("\n🔗 Custom Integrations:")
    print("  • Non-standard databases")
    print("  • API endpoints")
    print("  • Custom data sources")
    
    print("\n🚨 Production Features:")
    print("  • Comprehensive error handling")
    print("  • Audit logging")
    print("  • Quality checks")
    
    print("\nUpgrade path:")
    print("1. Start with basic configuration")
    print("2. Add plugins section when needed")
    print("3. Enable specific plugin types")
    print("4. Configure individual components")


def main():
    """Run all basic usage demonstrations."""
    print("Basic Usage Examples (No Plugins)")
    print("=================================")
    
    try:
        demonstrate_basic_usage()
        demonstrate_yaml_configuration()
        demonstrate_cli_usage()
        demonstrate_benefits()
        demonstrate_when_to_upgrade()
        
        print("\n=== Summary ===")
        print("🎉 Basic usage demonstration completed!")
        
        print("\nKey takeaways:")
        print("✓ Plugins are completely optional")
        print("✓ Basic functionality works without any plugins")
        print("✓ Simple configuration for simple use cases")
        print("✓ Easy upgrade path when more features are needed")
        
        print("\nNext steps:")
        print("• Use basic configuration for simple sync needs")
        print("• Add plugins only when specific features are required")
        print("• See plugin_system_example.py for advanced features")
        
    except Exception as e:
        print(f"Error running basic usage demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
