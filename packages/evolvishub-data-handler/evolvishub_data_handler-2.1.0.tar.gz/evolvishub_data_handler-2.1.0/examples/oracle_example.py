#!/usr/bin/env python3
"""
Oracle database adapter example.

This example demonstrates:
1. Oracle database configuration
2. Oracle-specific SQL syntax
3. TNS name configuration
4. Oracle with SQLite watermark storage
5. Error handling for Oracle connections
"""

import os
import sys
import yaml

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import (
    CDCConfig, DatabaseConfig, SyncConfig, SyncMode, 
    DatabaseType, WatermarkConfig, WatermarkStorageConfig, WatermarkStorageType
)


def create_oracle_host_config():
    """Create Oracle configuration using host and port."""
    return CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.ORACLE,
            host="oracle-server.example.com",
            port=1521,
            database="ORCL",  # Service name
            username="source_user",
            password="source_password",
            table="EMPLOYEES",
            watermark=WatermarkConfig(
                column="LAST_MODIFIED",
                type="timestamp",
                initial_value="2024-01-01 00:00:00"
            ),
            # Oracle-specific query with proper syntax
            query="""
                SELECT 
                    EMP_ID,
                    FIRST_NAME,
                    LAST_NAME,
                    EMAIL,
                    DEPARTMENT_ID,
                    SALARY,
                    LAST_MODIFIED,
                    CASE
                        WHEN DELETED_FLAG = 'Y' THEN 'delete'
                        WHEN LAST_MODIFIED > TO_TIMESTAMP(:last_sync, 'YYYY-MM-DD HH24:MI:SS') THEN 'update'
                        ELSE 'insert'
                    END as OPERATION
                FROM EMPLOYEES
                WHERE (LAST_MODIFIED > TO_TIMESTAMP(:last_sync, 'YYYY-MM-DD HH24:MI:SS') OR :last_sync IS NULL)
                    AND STATUS = 'ACTIVE'
                ORDER BY LAST_MODIFIED
                FETCH FIRST :batch_size ROWS ONLY
            """,
            additional_params={
                "encoding": "UTF-8",
                "nencoding": "UTF-8",
                "threaded": True
            }
        ),
        destination=DatabaseConfig(
            type=DatabaseType.ORACLE,
            host="oracle-dest.example.com",
            port=1521,
            database="ANALYTICS",
            username="dest_user",
            password="dest_password",
            table="EMPLOYEE_SYNC"
        ),
        sync=SyncConfig(
            mode=SyncMode.CRON,
            cron_expression="0 */6 * * *",  # Every 6 hours
            timezone="UTC",
            batch_size=1000,
            watermark_storage=WatermarkStorageConfig(
                type=WatermarkStorageType.SQLITE,
                sqlite_path="/var/lib/evolvishub/oracle_watermarks.db",
                table_name="sync_watermark"
            ),
            error_retry_attempts=5,
            error_retry_delay=15
        )
    )


def create_oracle_tns_config():
    """Create Oracle configuration using TNS names."""
    return CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.ORACLE,
            database="PROD_DB",  # TNS name from tnsnames.ora
            username="readonly_user",
            password="readonly_password",
            table="ORDERS",
            watermark=WatermarkConfig(
                column="ORDER_DATE",
                type="timestamp",
                initial_value="2024-01-01 00:00:00"
            ),
            # Simple select - framework will add WHERE, ORDER BY, LIMIT
            select="""
                SELECT 
                    ORDER_ID,
                    CUSTOMER_ID,
                    ORDER_DATE,
                    TOTAL_AMOUNT,
                    STATUS,
                    CREATED_BY
                FROM ORDERS
            """,
            additional_params={
                "min": 1,
                "max": 10,
                "increment": 2,
                "encoding": "UTF-8"
            }
        ),
        destination=DatabaseConfig(
            type=DatabaseType.ORACLE,
            database="ANALYTICS_DB",  # TNS name
            username="analytics_user",
            password="analytics_password",
            table="ORDER_ANALYTICS"
        ),
        sync=SyncConfig(
            mode=SyncMode.CONTINUOUS,
            interval_seconds=300,  # 5 minutes
            batch_size=500,
            watermark_storage=WatermarkStorageConfig(
                type=WatermarkStorageType.SQLITE,
                sqlite_path="/opt/evolvishub/oracle_orders.db",
                table_name="sync_watermark"
            )
        )
    )


def demonstrate_oracle_configurations():
    """Demonstrate different Oracle configuration options."""
    print("=== Oracle Database Configuration Examples ===")
    
    # Host/Port configuration
    print("\n1. Oracle with Host and Port:")
    host_config = create_oracle_host_config()
    print(f"   - Host: {host_config.source.host}:{host_config.source.port}")
    print(f"   - Service: {host_config.source.database}")
    print(f"   - Table: {host_config.source.table}")
    print(f"   - Watermark: {host_config.source.watermark.column}")
    print(f"   - Sync mode: {host_config.sync.mode.value}")
    print(f"   - Has custom query: {host_config.source.query is not None}")
    
    # TNS configuration
    print("\n2. Oracle with TNS Name:")
    tns_config = create_oracle_tns_config()
    print(f"   - TNS Name: {tns_config.source.database}")
    print(f"   - Table: {tns_config.source.table}")
    print(f"   - Watermark: {tns_config.source.watermark.column}")
    print(f"   - Sync mode: {tns_config.sync.mode.value}")
    print(f"   - Has simple select: {tns_config.source.select is not None}")
    
    return host_config, tns_config


def demonstrate_oracle_yaml_config():
    """Demonstrate Oracle YAML configuration."""
    print("\n=== Oracle YAML Configuration ===")
    
    config_dict = {
        "source": {
            "type": "oracle",
            "host": "oracle-prod.company.com",
            "port": 1521,
            "database": "PROD",
            "username": "etl_user",
            "password": "secure_password",
            "table": "TRANSACTIONS",
            "watermark": {
                "column": "TRANSACTION_DATE",
                "type": "timestamp",
                "initial_value": "2024-01-01 00:00:00"
            },
            "query": """
                SELECT 
                    TRANSACTION_ID,
                    ACCOUNT_ID,
                    AMOUNT,
                    TRANSACTION_TYPE,
                    TRANSACTION_DATE,
                    CASE 
                        WHEN AMOUNT > 10000 THEN 'HIGH_VALUE'
                        WHEN AMOUNT > 1000 THEN 'MEDIUM_VALUE'
                        ELSE 'LOW_VALUE'
                    END as VALUE_CATEGORY
                FROM TRANSACTIONS
                WHERE TRANSACTION_DATE > TO_TIMESTAMP(:last_sync, 'YYYY-MM-DD HH24:MI:SS')
                    OR :last_sync IS NULL
                ORDER BY TRANSACTION_DATE
                FETCH FIRST :batch_size ROWS ONLY
            """,
            "additional_params": {
                "encoding": "UTF-8",
                "nencoding": "UTF-8",
                "threaded": True
            }
        },
        "destination": {
            "type": "oracle",
            "database": "ANALYTICS_TNS",  # Using TNS name for destination
            "username": "analytics_user",
            "password": "analytics_password",
            "table": "TRANSACTION_ANALYTICS"
        },
        "sync": {
            "mode": "cron",
            "cron_expression": "0 2 * * *",  # Daily at 2 AM
            "timezone": "America/New_York",
            "batch_size": 2000,
            "watermark_storage": {
                "type": "sqlite",
                "sqlite_path": "/var/lib/evolvishub/oracle_transactions.db",
                "table_name": "sync_watermark"
            },
            "error_retry_attempts": 3,
            "error_retry_delay": 10
        }
    }
    
    # Save to YAML file
    config_file = "oracle_demo_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print(f"Configuration saved to {config_file}")
    
    # Load and validate
    config = CDCConfig(**config_dict)
    print("Configuration loaded successfully:")
    print(f"- Source: {config.source.type.value} ({config.source.database})")
    print(f"- Destination: {config.destination.type.value} ({config.destination.database})")
    print(f"- Watermark storage: {config.sync.watermark_storage.type.value}")
    print(f"- Custom query length: {len(config.source.query)} characters")
    
    # Cleanup
    os.remove(config_file)
    
    return config


def demonstrate_oracle_specific_features():
    """Demonstrate Oracle-specific features and syntax."""
    print("\n=== Oracle-Specific Features ===")
    
    print("1. Oracle SQL Syntax Examples:")
    print("   - Date conversion: TO_TIMESTAMP(:last_sync, 'YYYY-MM-DD HH24:MI:SS')")
    print("   - Pagination: FETCH FIRST :batch_size ROWS ONLY")
    print("   - System date: SYSTIMESTAMP")
    print("   - Dual table: SELECT 1 FROM dual")
    print("   - MERGE statement for upserts")
    
    print("\n2. Oracle Connection Options:")
    print("   - Host/Port: Standard TCP connection")
    print("   - TNS Name: Using tnsnames.ora configuration")
    print("   - Connection String: Direct connection string")
    print("   - Service Name vs SID: Different Oracle naming conventions")
    
    print("\n3. Oracle Data Types:")
    print("   - NUMBER: Numeric data")
    print("   - VARCHAR2: Variable-length strings")
    print("   - TIMESTAMP: Date and time with fractional seconds")
    print("   - CLOB/BLOB: Large objects")
    print("   - ROWID: Unique row identifier")
    
    print("\n4. Oracle-Specific Configuration:")
    print("   - encoding: Character encoding (UTF-8)")
    print("   - nencoding: National character encoding")
    print("   - threaded: Enable threaded mode")
    print("   - Connection pooling: min, max, increment")


def demonstrate_error_handling():
    """Demonstrate Oracle error handling scenarios."""
    print("\n=== Oracle Error Handling ===")
    
    print("Common Oracle connection errors and solutions:")
    print()
    print("1. ORA-12541: TNS:no listener")
    print("   - Check if Oracle listener is running")
    print("   - Verify host and port are correct")
    print("   - Check firewall settings")
    print()
    print("2. ORA-12154: TNS:could not resolve the connect identifier")
    print("   - Check TNS name in tnsnames.ora")
    print("   - Verify ORACLE_HOME and TNS_ADMIN environment variables")
    print()
    print("3. ORA-01017: invalid username/password")
    print("   - Verify credentials")
    print("   - Check if account is locked")
    print("   - Ensure user has necessary privileges")
    print()
    print("4. ORA-00942: table or view does not exist")
    print("   - Check table name and schema")
    print("   - Verify user has SELECT privileges")
    print("   - Use schema.table_name if needed")


def demonstrate_cli_usage():
    """Demonstrate CLI usage with Oracle configurations."""
    print("\n=== CLI Usage with Oracle ===")
    
    print("Command-line examples for Oracle:")
    print()
    print("1. One-time sync with Oracle:")
    print("   evolvishub-cdc run -c oracle_config.yaml -m one_time")
    print()
    print("2. Continuous sync with Oracle:")
    print("   evolvishub-cdc run -c oracle_config.yaml -m continuous")
    print()
    print("3. Cron sync with Oracle:")
    print("   evolvishub-cdc run -c oracle_config.yaml -m cron")
    print()
    print("4. Oracle with custom logging:")
    print("   evolvishub-cdc run -c oracle_config.yaml -l DEBUG --log-file oracle_sync.log")
    print()
    print("5. Oracle with SQLite watermarks:")
    print("   evolvishub-cdc run -c oracle_watermark_config.yaml -m continuous")


def main():
    """Run all Oracle demonstrations."""
    print("Oracle Database Adapter Examples")
    print("================================")
    
    try:
        demonstrate_oracle_configurations()
        demonstrate_oracle_yaml_config()
        demonstrate_oracle_specific_features()
        demonstrate_error_handling()
        demonstrate_cli_usage()
        
        print("\n=== Summary ===")
        print("Oracle adapter implementation completed!")
        print("\nKey features:")
        print("✓ Oracle database connectivity with oracledb package")
        print("✓ Support for host/port and TNS name configurations")
        print("✓ Oracle-specific SQL syntax (TO_TIMESTAMP, FETCH FIRST, etc.)")
        print("✓ MERGE statement for watermark upserts")
        print("✓ Connection pooling and encoding options")
        print("✓ Integration with SQLite watermark storage")
        print("✓ Comprehensive error handling")
        print("✓ YAML and INI configuration support")
        print("✓ CLI integration")
        
        print("\nOracle-specific benefits:")
        print("• Native Oracle data type handling")
        print("• Efficient pagination with FETCH FIRST")
        print("• TNS name support for enterprise environments")
        print("• Connection pooling for better performance")
        print("• Proper handling of Oracle LOBs (CLOB/BLOB)")
        print("• SYSTIMESTAMP for accurate timestamps")
        
    except Exception as e:
        print(f"Error running Oracle demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
