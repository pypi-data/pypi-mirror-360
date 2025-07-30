#!/usr/bin/env python3
"""
Example demonstrating SQLite watermark storage functionality.

This example shows how to:
1. Configure SQLite watermark storage
2. Resume sync from last watermark position
3. Handle sync errors with watermark tracking
4. Monitor watermark status
"""

import os
import sys
import yaml
import sqlite3
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import (
    CDCConfig, DatabaseConfig, SyncConfig, SyncMode, 
    DatabaseType, WatermarkConfig, WatermarkStorageConfig, WatermarkStorageType
)
from evolvishub_data_handler.watermark_manager import SQLiteWatermarkManager


def create_sqlite_watermark_config():
    """Create a configuration with SQLite watermark storage."""
    config = CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="source_db",
            username="user",
            password="password",
            table="users",
            watermark=WatermarkConfig(
                column="updated_at",
                type="timestamp",
                initial_value="2024-01-01 00:00:00"
            ),
            query="""
                SELECT id, name, email, updated_at,
                       CASE WHEN deleted_at IS NOT NULL THEN 'delete'
                            ELSE 'upsert' END as operation
                FROM users 
                WHERE updated_at > :last_sync OR :last_sync IS NULL
                ORDER BY updated_at 
                LIMIT :batch_size
            """
        ),
        destination=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="dest_db",
            username="user",
            password="password",
            table="users"
        ),
        sync=SyncConfig(
            mode=SyncMode.CONTINUOUS,
            interval_seconds=30,
            batch_size=1000,
            watermark_storage=WatermarkStorageConfig(
                type=WatermarkStorageType.SQLITE,
                sqlite_path="./watermarks.db",
                table_name="sync_watermark"
            )
        )
    )
    
    return config


def demonstrate_watermark_manager():
    """Demonstrate direct watermark manager usage."""
    print("=== Watermark Manager Demo ===")
    
    # Create watermark storage config
    storage_config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path="./demo_watermarks.db",
        table_name="sync_watermark"
    )
    
    # Create watermark manager
    manager = SQLiteWatermarkManager(storage_config)
    
    try:
        # Simulate watermark updates
        print("1. Setting initial watermark...")
        manager.update_watermark(
            "users", "updated_at", "2024-01-01 00:00:00", "success"
        )
        
        # Get watermark
        result = manager.get_watermark("users", "updated_at")
        if result:
            watermark_value, status = result
            print(f"   Retrieved watermark: {watermark_value} (status: {status})")
        
        # Simulate successful sync
        print("2. Updating watermark after successful sync...")
        new_watermark = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        manager.update_watermark(
            "users", "updated_at", new_watermark, "success"
        )
        
        # Simulate error
        print("3. Updating watermark after error...")
        manager.update_watermark(
            "users", "updated_at", new_watermark, "error", "Connection timeout"
        )
        
        # Get all watermarks
        print("4. All watermarks:")
        all_watermarks = manager.get_all_watermarks()
        for key, watermark in all_watermarks.items():
            print(f"   {key}: {watermark['watermark_value']} ({watermark['status']})")
            if watermark['error_message']:
                print(f"      Error: {watermark['error_message']}")
        
    finally:
        manager.close()
        # Cleanup
        if os.path.exists("./demo_watermarks.db"):
            os.remove("./demo_watermarks.db")


def demonstrate_config_creation():
    """Demonstrate creating configuration with watermark storage."""
    print("\n=== Configuration Demo ===")
    
    # Create configuration
    config = create_sqlite_watermark_config()
    
    print("Configuration created with SQLite watermark storage:")
    print(f"- Source: {config.source.type.value} ({config.source.database})")
    print(f"- Destination: {config.destination.type.value} ({config.destination.database})")
    print(f"- Sync mode: {config.sync.mode.value}")
    print(f"- Watermark storage: {config.sync.watermark_storage.type.value}")
    print(f"- SQLite path: {config.sync.watermark_storage.sqlite_path}")
    print(f"- Watermark table: {config.sync.watermark_storage.table_name}")


def demonstrate_yaml_config():
    """Demonstrate YAML configuration with watermark storage."""
    print("\n=== YAML Configuration Demo ===")
    
    config_dict = {
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
            "cron_expression": "0 */2 * * *",
            "timezone": "UTC",
            "batch_size": 1000,
            "watermark_storage": {
                "type": "sqlite",
                "sqlite_path": "/var/lib/evolvishub/watermarks.db",
                "table_name": "sync_watermark"
            }
        }
    }
    
    # Save to YAML file
    config_file = "watermark_demo_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print(f"Configuration saved to {config_file}")
    
    # Load and validate
    config = CDCConfig(**config_dict)
    print("Configuration loaded and validated successfully:")
    print(f"- Watermark storage type: {config.sync.watermark_storage.type.value}")
    print(f"- SQLite path: {config.sync.watermark_storage.sqlite_path}")
    
    # Cleanup
    os.remove(config_file)


def demonstrate_resume_functionality():
    """Demonstrate resume from last watermark functionality."""
    print("\n=== Resume Functionality Demo ===")
    
    db_path = "./resume_demo.db"
    
    # Create watermark manager
    storage_config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path=db_path,
        table_name="sync_watermark"
    )
    
    manager = SQLiteWatermarkManager(storage_config)
    
    try:
        # Simulate first sync
        print("1. First sync - no previous watermark")
        result = manager.get_watermark("orders", "updated_at")
        if result is None:
            print("   No previous watermark found, using initial value")
            initial_watermark = "2024-01-01 00:00:00"
        else:
            watermark_value, status = result
            initial_watermark = watermark_value
            print(f"   Found previous watermark: {watermark_value}")
        
        # Simulate processing and update watermark
        print("2. Processing data and updating watermark...")
        new_watermark = "2024-01-15 10:30:00"
        manager.update_watermark("orders", "updated_at", new_watermark, "success")
        print(f"   Updated watermark to: {new_watermark}")
        
        # Simulate restart and resume
        print("3. Simulating application restart...")
        manager.close()
        
        # Create new manager instance (simulating restart)
        manager = SQLiteWatermarkManager(storage_config)
        
        print("4. Resuming from last watermark...")
        result = manager.get_watermark("orders", "updated_at")
        if result:
            watermark_value, status = result
            print(f"   Resumed from watermark: {watermark_value} (status: {status})")
            
            if status == 'success':
                print("   Last sync was successful, continuing from this point")
            else:
                print("   Last sync had errors, may need to retry")
        
    finally:
        manager.close()
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)


def demonstrate_error_handling():
    """Demonstrate error handling with watermark tracking."""
    print("\n=== Error Handling Demo ===")
    
    db_path = "./error_demo.db"
    
    storage_config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path=db_path,
        table_name="sync_watermark"
    )
    
    manager = SQLiteWatermarkManager(storage_config)
    
    try:
        # Simulate successful syncs
        print("1. Successful syncs...")
        manager.update_watermark("products", "updated_at", "2024-01-01 10:00:00", "success")
        manager.update_watermark("products", "updated_at", "2024-01-01 11:00:00", "success")
        
        # Simulate error
        print("2. Sync error occurred...")
        manager.update_watermark(
            "products", "updated_at", "2024-01-01 11:00:00", 
            "error", "Database connection timeout"
        )
        
        # Check status
        result = manager.get_watermark("products", "updated_at")
        if result:
            watermark_value, status = result
            print(f"   Current watermark: {watermark_value} (status: {status})")
            
            if status == 'error':
                print("   Last sync failed, should retry from this watermark")
        
        # Simulate retry and success
        print("3. Retry successful...")
        manager.update_watermark("products", "updated_at", "2024-01-01 12:00:00", "success")
        
        result = manager.get_watermark("products", "updated_at")
        if result:
            watermark_value, status = result
            print(f"   Updated watermark: {watermark_value} (status: {status})")
        
    finally:
        manager.close()
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)


def main():
    """Run all demonstrations."""
    print("SQLite Watermark Storage Examples")
    print("=================================")
    
    try:
        demonstrate_watermark_manager()
        demonstrate_config_creation()
        demonstrate_yaml_config()
        demonstrate_resume_functionality()
        demonstrate_error_handling()
        
        print("\n=== Summary ===")
        print("All demonstrations completed successfully!")
        print("\nKey benefits of SQLite watermark storage:")
        print("✓ Persistent watermark storage across application restarts")
        print("✓ Centralized watermark management for multiple tables/sources")
        print("✓ Error tracking and status monitoring")
        print("✓ Resume capability from last successful sync point")
        print("✓ No dependency on source/destination databases for watermarks")
        print("✓ Lightweight SQLite database for watermark persistence")
        
    except Exception as e:
        print(f"Error running demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
