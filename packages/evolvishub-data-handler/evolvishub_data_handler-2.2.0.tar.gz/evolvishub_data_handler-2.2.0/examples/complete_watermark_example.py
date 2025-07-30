#!/usr/bin/env python3
"""
Complete example demonstrating SQLite watermark storage with CDC handler.

This example shows:
1. Configuration with SQLite watermark storage
2. CDC handler using centralized watermarks
3. Resume functionality across restarts
4. Error handling with watermark tracking
"""

import os
import sys
import yaml
import tempfile
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import (
    CDCConfig, DatabaseConfig, SyncConfig, SyncMode, 
    DatabaseType, WatermarkConfig, WatermarkStorageConfig, WatermarkStorageType
)
from evolvishub_data_handler.cdc_handler import CDCHandler
from evolvishub_data_handler.watermark_manager import SQLiteWatermarkManager


def create_complete_config(sqlite_path: str) -> CDCConfig:
    """Create a complete configuration with SQLite watermark storage."""
    return CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="source_db",
            username="source_user",
            password="source_password",
            table="users",
            watermark=WatermarkConfig(
                column="updated_at",
                type="timestamp",
                initial_value="2024-01-01 00:00:00"
            ),
            query="""
                SELECT 
                    id, name, email, updated_at, created_at,
                    CASE
                        WHEN deleted_at IS NOT NULL THEN 'delete'
                        WHEN updated_at > :last_sync THEN 'update'
                        ELSE 'insert'
                    END as operation
                FROM users
                WHERE (updated_at > :last_sync OR :last_sync IS NULL)
                    AND status = 'active'
                ORDER BY updated_at
                LIMIT :batch_size
            """
        ),
        destination=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="dest_db",
            username="dest_user",
            password="dest_password",
            table="users_sync"
        ),
        sync=SyncConfig(
            mode=SyncMode.CONTINUOUS,
            interval_seconds=30,
            batch_size=1000,
            watermark_storage=WatermarkStorageConfig(
                type=WatermarkStorageType.SQLITE,
                sqlite_path=sqlite_path,
                table_name="sync_watermark"
            ),
            error_retry_attempts=3,
            error_retry_delay=5
        )
    )


def demonstrate_yaml_config_with_watermarks():
    """Demonstrate YAML configuration with SQLite watermarks."""
    print("=== YAML Configuration with SQLite Watermarks ===")
    
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
            },
            "select": "SELECT id, customer_id, total_amount, status, updated_at FROM orders"
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
            "batch_size": 2000,
            "watermark_storage": {
                "type": "sqlite",
                "sqlite_path": "./orders_watermarks.db",
                "table_name": "sync_watermark"
            },
            "error_retry_attempts": 5,
            "error_retry_delay": 10
        }
    }
    
    # Save to YAML
    config_file = "complete_watermark_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print(f"Configuration saved to {config_file}")
    
    # Load and validate
    config = CDCConfig(**config_dict)
    print("Configuration loaded successfully:")
    print(f"- Source: {config.source.type.value} table '{config.source.table}'")
    print(f"- Destination: {config.destination.type.value} table '{config.destination.table}'")
    print(f"- Sync mode: {config.sync.mode.value}")
    print(f"- Watermark storage: {config.sync.watermark_storage.type.value}")
    print(f"- SQLite path: {config.sync.watermark_storage.sqlite_path}")
    
    # Cleanup
    os.remove(config_file)
    
    return config


def demonstrate_cdc_handler_with_watermarks():
    """Demonstrate CDC handler with SQLite watermark storage."""
    print("\n=== CDC Handler with SQLite Watermarks ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        sqlite_path = f.name
    
    try:
        # Create configuration
        config = create_complete_config(sqlite_path)
        
        # Create CDC handler (this will initialize the watermark manager)
        handler = CDCHandler(config)
        
        print("CDC Handler created with SQLite watermark storage:")
        print(f"- Watermark manager type: {type(handler.watermark_manager).__name__}")
        print(f"- SQLite database: {sqlite_path}")
        
        # Demonstrate watermark operations
        print("\nDemonstrating watermark operations:")
        
        # Get initial watermark (should be None or initial value)
        initial_watermark = handler._get_current_watermark()
        print(f"1. Initial watermark: {initial_watermark}")
        
        # Simulate successful sync
        print("2. Simulating successful sync...")
        new_watermark = "2024-01-15 10:30:00"
        handler._update_current_watermark(new_watermark, 'success')
        
        # Get updated watermark
        updated_watermark = handler._get_current_watermark()
        print(f"3. Updated watermark: {updated_watermark}")
        
        # Simulate error
        print("4. Simulating sync error...")
        handler._update_current_watermark(new_watermark, 'error', 'Database connection timeout')
        
        # Get watermark after error
        error_watermark = handler._get_current_watermark()
        print(f"5. Watermark after error: {error_watermark}")
        
        # Check watermark manager directly
        if handler.watermark_manager:
            all_watermarks = handler.watermark_manager.get_all_watermarks()
            print(f"6. All watermarks in storage: {len(all_watermarks)} entries")
            for key, watermark in all_watermarks.items():
                print(f"   {key}: {watermark['watermark_value']} ({watermark['status']})")
                if watermark['error_message']:
                    print(f"      Error: {watermark['error_message']}")
        
        # Cleanup handler
        handler.stop()
        
    finally:
        # Cleanup
        if os.path.exists(sqlite_path):
            os.remove(sqlite_path)


def demonstrate_restart_scenario():
    """Demonstrate restart and resume functionality."""
    print("\n=== Restart and Resume Scenario ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        sqlite_path = f.name
    
    try:
        # First session - initial sync
        print("1. First session - initial sync")
        config1 = create_complete_config(sqlite_path)
        handler1 = CDCHandler(config1)
        
        # Simulate some sync operations
        handler1._update_current_watermark("2024-01-10 08:00:00", 'success')
        handler1._update_current_watermark("2024-01-10 09:00:00", 'success')
        handler1._update_current_watermark("2024-01-10 10:00:00", 'success')
        
        last_watermark = handler1._get_current_watermark()
        print(f"   Last watermark before shutdown: {last_watermark}")
        
        # Shutdown
        handler1.stop()
        print("   Session 1 ended")
        
        # Second session - restart and resume
        print("2. Second session - restart and resume")
        config2 = create_complete_config(sqlite_path)
        handler2 = CDCHandler(config2)
        
        # Check if we resume from the correct watermark
        resumed_watermark = handler2._get_current_watermark()
        print(f"   Resumed from watermark: {resumed_watermark}")
        
        if resumed_watermark == last_watermark:
            print("   ✓ Successfully resumed from last watermark!")
        else:
            print("   ✗ Failed to resume from correct watermark")
        
        # Continue with more sync operations
        handler2._update_current_watermark("2024-01-10 11:00:00", 'success')
        handler2._update_current_watermark("2024-01-10 12:00:00", 'success')
        
        final_watermark = handler2._get_current_watermark()
        print(f"   Final watermark: {final_watermark}")
        
        # Shutdown
        handler2.stop()
        print("   Session 2 ended")
        
        # Verify persistence
        print("3. Verifying persistence...")
        storage_config = WatermarkStorageConfig(
            type=WatermarkStorageType.SQLITE,
            sqlite_path=sqlite_path,
            table_name="sync_watermark"
        )
        
        manager = SQLiteWatermarkManager(storage_config)
        try:
            all_watermarks = manager.get_all_watermarks()
            print(f"   Total watermark entries: {len(all_watermarks)}")
            for key, watermark in all_watermarks.items():
                print(f"   {key}: {watermark['watermark_value']} ({watermark['status']})")
        finally:
            manager.close()
        
    finally:
        # Cleanup
        if os.path.exists(sqlite_path):
            os.remove(sqlite_path)


def demonstrate_cli_usage():
    """Demonstrate CLI usage with SQLite watermarks."""
    print("\n=== CLI Usage with SQLite Watermarks ===")
    
    print("Command-line examples with SQLite watermark storage:")
    print()
    print("1. One-time sync with SQLite watermarks:")
    print("   evolvishub-cdc run -c sqlite_watermark_config.yaml -m one_time")
    print()
    print("2. Continuous sync with SQLite watermarks:")
    print("   evolvishub-cdc run -c sqlite_watermark_config.yaml -m continuous")
    print()
    print("3. Cron sync with SQLite watermarks:")
    print("   evolvishub-cdc run -c sqlite_watermark_config.yaml -m cron")
    print()
    print("4. With custom logging and SQLite watermarks:")
    print("   evolvishub-cdc run -c sqlite_watermark_config.yaml -l DEBUG --log-file sync.log")
    print()
    print("Example configuration file (sqlite_watermark_config.yaml):")
    print("```yaml")
    print("sync:")
    print("  watermark_storage:")
    print("    type: sqlite")
    print("    sqlite_path: /var/lib/evolvishub/watermarks.db")
    print("    table_name: sync_watermark")
    print("```")


def main():
    """Run all demonstrations."""
    print("Complete SQLite Watermark Storage Examples")
    print("==========================================")
    
    try:
        demonstrate_yaml_config_with_watermarks()
        demonstrate_cdc_handler_with_watermarks()
        demonstrate_restart_scenario()
        demonstrate_cli_usage()
        
        print("\n=== Summary ===")
        print("All demonstrations completed successfully!")
        print("\nKey features demonstrated:")
        print("✓ SQLite watermark storage configuration")
        print("✓ CDC handler integration with centralized watermarks")
        print("✓ Automatic resume from last watermark after restart")
        print("✓ Error tracking and status monitoring")
        print("✓ Persistent watermark storage across sessions")
        print("✓ YAML configuration with watermark storage options")
        print("✓ CLI usage with SQLite watermark storage")
        
        print("\nBenefits of SQLite watermark storage:")
        print("• Independent of source/destination database availability")
        print("• Survives application restarts and database maintenance")
        print("• Centralized watermark management for multiple tables")
        print("• Built-in error tracking and status monitoring")
        print("• Lightweight and reliable SQLite storage")
        print("• Easy backup and migration of watermark data")
        
    except Exception as e:
        print(f"Error running demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
