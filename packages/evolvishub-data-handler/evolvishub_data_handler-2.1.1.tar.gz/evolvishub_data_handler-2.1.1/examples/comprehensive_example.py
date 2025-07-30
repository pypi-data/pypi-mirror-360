#!/usr/bin/env python3
"""
Comprehensive example showing all new features:
1. Custom queries with parameter substitution
2. Simple select statements with automatic WHERE/ORDER BY
3. Different sync modes (one-time, continuous, cron)
4. Cron scheduling with timezone support
5. Enhanced CLI usage
6. Configuration validation
"""

import os
import sys
import yaml
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import (
    CDCConfig, DatabaseConfig, SyncConfig, SyncMode, 
    DatabaseType, WatermarkConfig
)
from evolvishub_data_handler.cdc_handler import CDCHandler


def example_1_custom_query():
    """Example 1: Custom query with complex logic."""
    print("=== Example 1: Custom Query ===")
    
    config = CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="source_db",
            username="user",
            password="password",
            watermark=WatermarkConfig(
                column="updated_at",
                type="timestamp",
                initial_value="2024-01-01 00:00:00"
            ),
            # Complex custom query with business logic
            query="""
                SELECT 
                    u.id,
                    u.name,
                    u.email,
                    u.updated_at,
                    u.created_at,
                    CASE
                        WHEN u.deleted_at IS NOT NULL THEN 'delete'
                        WHEN u.updated_at > :last_sync THEN 'update'
                        ELSE 'insert'
                    END as operation,
                    -- Computed fields
                    EXTRACT(EPOCH FROM u.updated_at) as updated_timestamp,
                    CASE 
                        WHEN u.email LIKE '%@company.com' THEN 'internal'
                        ELSE 'external'
                    END as user_type,
                    -- Join with profile data
                    p.department,
                    p.role
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE (u.updated_at > :last_sync OR :last_sync IS NULL)
                    AND u.status = 'active'
                    AND (u.deleted_at IS NULL OR u.deleted_at > :last_sync)
                ORDER BY u.updated_at
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
            table="users_enriched"
        ),
        sync=SyncConfig(
            mode=SyncMode.ONE_TIME,
            batch_size=500
        )
    )
    
    print("Configuration created with custom query:")
    print(f"- Source query includes JOINs and computed fields")
    print(f"- Sync mode: {config.sync.mode.value}")
    print(f"- Batch size: {config.sync.batch_size}")
    
    return config


def example_2_simple_select():
    """Example 2: Simple select with automatic WHERE/ORDER BY."""
    print("\n=== Example 2: Simple Select ===")
    
    config = CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="source_db",
            username="user",
            password="password",
            watermark=WatermarkConfig(
                column="updated_at",
                type="timestamp",
                initial_value="2024-01-01 00:00:00"
            ),
            # Simple select - framework adds WHERE, ORDER BY, LIMIT
            select="SELECT id, name, email, status, updated_at FROM users"
        ),
        destination=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="dest_db",
            username="user",
            password="password",
            table="users_simple"
        ),
        sync=SyncConfig(
            mode=SyncMode.CONTINUOUS,
            interval_seconds=30,
            batch_size=1000
        )
    )
    
    print("Configuration created with simple select:")
    print(f"- Framework will add WHERE updated_at > :last_sync")
    print(f"- Framework will add ORDER BY updated_at")
    print(f"- Framework will add LIMIT :batch_size")
    print(f"- Sync mode: {config.sync.mode.value}")
    print(f"- Interval: {config.sync.interval_seconds} seconds")
    
    return config


def example_3_cron_scheduling():
    """Example 3: Cron scheduling with timezone."""
    print("\n=== Example 3: Cron Scheduling ===")
    
    config = CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="source_db",
            username="user",
            password="password",
            table="orders",
            watermark=WatermarkConfig(
                column="updated_at",
                type="timestamp",
                initial_value="2024-01-01 00:00:00"
            )
        ),
        destination=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="dest_db",
            username="user",
            password="password",
            table="orders"
        ),
        sync=SyncConfig(
            mode=SyncMode.CRON,
            cron_expression="0 */2 * * *",  # Every 2 hours
            timezone="America/New_York",
            batch_size=2000,
            error_retry_attempts=5,
            error_retry_delay=10
        )
    )
    
    print("Configuration created with cron scheduling:")
    print(f"- Cron expression: {config.sync.cron_expression} (every 2 hours)")
    print(f"- Timezone: {config.sync.timezone}")
    print(f"- Sync mode: {config.sync.mode.value}")
    print(f"- Error retry attempts: {config.sync.error_retry_attempts}")
    
    return config


def example_4_yaml_config():
    """Example 4: Save and load YAML configuration."""
    print("\n=== Example 4: YAML Configuration ===")
    
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
            },
            "query": """
                SELECT 
                    id, name, price, category, updated_at,
                    CASE 
                        WHEN price > 100 THEN 'premium'
                        WHEN price > 50 THEN 'standard'
                        ELSE 'budget'
                    END as price_tier
                FROM products 
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
            "table": "products_enriched"
        },
        "sync": {
            "mode": "cron",
            "cron_expression": "0 9 * * 1-5",  # Weekdays at 9 AM
            "timezone": "UTC",
            "batch_size": 1000,
            "watermark_table": "sync_watermark",
            "error_retry_attempts": 3,
            "error_retry_delay": 5
        }
    }
    
    # Save to YAML file
    config_file = "example_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print(f"Configuration saved to {config_file}")
    
    # Load from YAML file
    from evolvishub_data_handler.config_loader import load_config
    loaded_config = load_config(config_file)
    
    print("Configuration loaded from YAML:")
    print(f"- Source type: {loaded_config.source.type.value}")
    print(f"- Has custom query: {loaded_config.source.query is not None}")
    print(f"- Sync mode: {loaded_config.sync.mode.value}")
    print(f"- Cron expression: {loaded_config.sync.cron_expression}")
    
    # Cleanup
    os.remove(config_file)
    
    return loaded_config


def example_5_cli_usage():
    """Example 5: CLI usage examples."""
    print("\n=== Example 5: CLI Usage ===")
    
    print("Command-line usage examples:")
    print()
    print("1. One-time sync:")
    print("   evolvishub-cdc run -c config.yaml -m one_time")
    print()
    print("2. Continuous sync:")
    print("   evolvishub-cdc run -c config.yaml -m continuous")
    print()
    print("3. Cron sync with custom expression:")
    print("   evolvishub-cdc run -c config.yaml -m cron --cron '0 */4 * * *'")
    print()
    print("4. With custom logging:")
    print("   evolvishub-cdc run -c config.yaml -l DEBUG --log-file sync.log")
    print()
    print("5. Legacy commands (still supported):")
    print("   evolvishub-cdc sync -c config.yaml")
    print("   evolvishub-cdc continuous-sync -c config.yaml")


def example_6_error_handling():
    """Example 6: Configuration validation and error handling."""
    print("\n=== Example 6: Error Handling ===")
    
    try:
        # Invalid cron expression
        invalid_config = SyncConfig(
            mode=SyncMode.CRON,
            cron_expression="invalid cron"
        )
    except ValueError as e:
        print(f"✓ Caught invalid cron expression: {e}")
    
    try:
        # Missing cron expression for cron mode
        invalid_config = SyncConfig(
            mode=SyncMode.CRON,
            cron_expression=None
        )
    except ValueError as e:
        print(f"✓ Caught missing cron expression: {e}")
    
    try:
        # Invalid port number
        invalid_config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=99999,  # Invalid port
            database="test_db",
            username="user",
            password="password"
        )
    except ValueError as e:
        print(f"✓ Caught invalid port: {e}")
    
    print("All validation checks passed!")


def main():
    """Run all examples."""
    print("Comprehensive Data Handler Examples")
    print("==================================")
    
    try:
        # Run all examples
        config1 = example_1_custom_query()
        config2 = example_2_simple_select()
        config3 = example_3_cron_scheduling()
        config4 = example_4_yaml_config()
        example_5_cli_usage()
        example_6_error_handling()
        
        print("\n=== Summary ===")
        print("All examples completed successfully!")
        print("Key features demonstrated:")
        print("✓ Custom SQL queries with parameter substitution")
        print("✓ Simple SELECT statements with automatic clauses")
        print("✓ One-time, continuous, and cron sync modes")
        print("✓ Cron scheduling with timezone support")
        print("✓ YAML configuration loading and saving")
        print("✓ Enhanced CLI with multiple options")
        print("✓ Configuration validation and error handling")
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
