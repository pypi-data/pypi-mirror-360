#!/usr/bin/env python3
"""
Advanced sync example demonstrating new features:
- Custom queries and select statements
- Different sync modes (one-time, continuous, cron)
- Cron scheduling with timezone support
- Enhanced configuration options
"""

import os
import sys
import yaml
import signal
from datetime import datetime

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler import CDCHandler
from evolvishub_data_handler.config import CDCConfig, SyncMode
from evolvishub_data_handler.config_loader import load_config


def create_sample_configs():
    """Create sample configuration files for demonstration."""
    
    # One-time sync with custom query
    one_time_config = {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "source_db",
            "username": "user",
            "password": "password",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp",
                "initial_value": "2024-01-01 00:00:00"
            },
            "query": """
                SELECT 
                    id, name, email, updated_at,
                    CASE 
                        WHEN deleted_at IS NOT NULL THEN 'delete'
                        WHEN updated_at > :last_sync THEN 'update'
                        ELSE 'insert'
                    END as operation
                FROM users 
                WHERE updated_at > :last_sync OR :last_sync IS NULL
                ORDER BY updated_at
                LIMIT :batch_size
            """
        },
        "destination": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "dest_db",
            "username": "user",
            "password": "password",
            "table": "users"
        },
        "sync": {
            "mode": "one_time",
            "batch_size": 1000
        }
    }
    
    # Continuous sync with simple select
    continuous_config = {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "source_db",
            "username": "user",
            "password": "password",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp",
                "initial_value": "2024-01-01 00:00:00"
            },
            "select": "SELECT id, name, email, updated_at FROM users"
        },
        "destination": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "dest_db",
            "username": "user",
            "password": "password",
            "table": "users"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 30,
            "batch_size": 500
        }
    }
    
    # Cron scheduled sync
    cron_config = {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "source_db",
            "username": "user",
            "password": "password",
            "table": "orders",
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
            "username": "user",
            "password": "password",
            "table": "orders"
        },
        "sync": {
            "mode": "cron",
            "cron_expression": "0 */2 * * *",  # Every 2 hours
            "timezone": "UTC",
            "batch_size": 1000
        }
    }
    
    # Save configurations
    with open("one_time_config.yaml", "w") as f:
        yaml.dump(one_time_config, f, default_flow_style=False)
    
    with open("continuous_config.yaml", "w") as f:
        yaml.dump(continuous_config, f, default_flow_style=False)
    
    with open("cron_config.yaml", "w") as f:
        yaml.dump(cron_config, f, default_flow_style=False)
    
    print("Sample configuration files created:")
    print("- one_time_config.yaml")
    print("- continuous_config.yaml") 
    print("- cron_config.yaml")


def demonstrate_one_time_sync():
    """Demonstrate one-time sync with custom query."""
    print("\n=== One-Time Sync Demo ===")
    try:
        config = load_config("one_time_config.yaml")
        handler = CDCHandler(config)
        
        print("Running one-time sync with custom query...")
        handler.sync()
        print("One-time sync completed successfully!")
        
    except Exception as e:
        print(f"Error in one-time sync: {str(e)}")


def demonstrate_continuous_sync():
    """Demonstrate continuous sync with simple select."""
    print("\n=== Continuous Sync Demo ===")
    try:
        config = load_config("continuous_config.yaml")
        handler = CDCHandler(config)
        
        # Set up signal handler for graceful shutdown
        def signal_handler(signum, frame):
            print("\nStopping continuous sync...")
            handler.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        print("Starting continuous sync (press Ctrl+C to stop)...")
        print("Sync will run every 30 seconds...")
        handler.run_continuous()
        
    except KeyboardInterrupt:
        print("Continuous sync stopped by user")
    except Exception as e:
        print(f"Error in continuous sync: {str(e)}")


def demonstrate_cron_sync():
    """Demonstrate cron-scheduled sync."""
    print("\n=== Cron Sync Demo ===")
    try:
        config = load_config("cron_config.yaml")
        handler = CDCHandler(config)
        
        # Set up signal handler for graceful shutdown
        def signal_handler(signum, frame):
            print("\nStopping cron sync...")
            handler.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        print("Starting cron sync (every 2 hours)...")
        print("Press Ctrl+C to stop...")
        handler.run_cron()
        
    except KeyboardInterrupt:
        print("Cron sync stopped by user")
    except Exception as e:
        print(f"Error in cron sync: {str(e)}")


def demonstrate_programmatic_config():
    """Demonstrate creating configuration programmatically."""
    print("\n=== Programmatic Configuration Demo ===")
    
    # Create configuration object directly
    config_dict = {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "source_db",
            "username": "user",
            "password": "password",
            "table": "products",
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
            "username": "user",
            "password": "password",
            "table": "products"
        },
        "sync": {
            "mode": "one_time",
            "batch_size": 100
        }
    }
    
    try:
        config = CDCConfig(**config_dict)
        handler = CDCHandler(config)
        
        print("Configuration created programmatically:")
        print(f"- Source: {config.source.type} ({config.source.database})")
        print(f"- Destination: {config.destination.type} ({config.destination.database})")
        print(f"- Sync mode: {config.sync.mode.value}")
        print(f"- Batch size: {config.sync.batch_size}")
        
        # Note: We're not actually running the sync here since we don't have real databases
        print("Handler created successfully (not running sync without real database)")
        
    except Exception as e:
        print(f"Error creating configuration: {str(e)}")


def main():
    """Main function to demonstrate all features."""
    print("Advanced Data Handler Sync Examples")
    print("===================================")
    
    # Create sample configurations
    create_sample_configs()
    
    # Demonstrate different sync modes
    print("\nChoose a demo to run:")
    print("1. One-time sync with custom query")
    print("2. Continuous sync with simple select")
    print("3. Cron-scheduled sync")
    print("4. Programmatic configuration")
    print("5. All demos (non-interactive)")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            demonstrate_one_time_sync()
        elif choice == "2":
            demonstrate_continuous_sync()
        elif choice == "3":
            demonstrate_cron_sync()
        elif choice == "4":
            demonstrate_programmatic_config()
        elif choice == "5":
            demonstrate_one_time_sync()
            demonstrate_programmatic_config()
            print("\nNote: Continuous and cron demos require user interaction to stop.")
        else:
            print("Invalid choice. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Error running demo: {str(e)}")
    finally:
        # Cleanup
        for config_file in ["one_time_config.yaml", "continuous_config.yaml", "cron_config.yaml"]:
            if os.path.exists(config_file):
                os.remove(config_file)
        print("\nCleanup completed.")


if __name__ == "__main__":
    main()
