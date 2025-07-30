#!/usr/bin/env python3
"""
Watermark Demonstration for Multi-CDC.

This example shows how watermarks work independently for each mapping
in a multi-source CDC configuration.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import (
    MultiCDCConfig, SourceDestinationMapping, DatabaseConfig, DatabaseType,
    SyncConfig, SyncMode, WatermarkConfig, WatermarkType
)


def demonstrate_independent_watermarks():
    """Demonstrate how watermarks work independently for each mapping."""
    
    print("=== Independent Watermark Management ===\n")
    
    # Common source database
    source_db = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="source-db.company.com",
        database="customer_analytics",
        username="analytics_user",
        password="analytics_password"
    )
    
    # Common destination database
    dest_db = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="warehouse-db.company.com",
        database="data_warehouse",
        username="warehouse_user",
        password="warehouse_password"
    )
    
    # Create mappings with different watermark configurations
    mappings = [
        # Mapping 1: Timestamp watermark
        SourceDestinationMapping(
            name="customer_demographics",
            source=source_db.model_copy(update={"table": "vw_customer_demographics"}),
            destination=dest_db.model_copy(update={"table": "dim_customer_demographics"}),
            watermark=WatermarkConfig(
                column="last_updated",
                type=WatermarkType.TIMESTAMP,
                storage_type="sqlite",
                storage_path="./watermarks/customer_demographics.db"
            )
        ),
        
        # Mapping 2: Different timestamp column
        SourceDestinationMapping(
            name="purchase_behavior",
            source=source_db.model_copy(update={"table": "vw_customer_purchase_behavior"}),
            destination=dest_db.model_copy(update={"table": "fact_customer_behavior"}),
            watermark=WatermarkConfig(
                column="analysis_date",
                type=WatermarkType.TIMESTAMP,
                storage_type="sqlite",
                storage_path="./watermarks/purchase_behavior.db"
            )
        ),
        
        # Mapping 3: Integer watermark
        SourceDestinationMapping(
            name="geographic_distribution",
            source=source_db.model_copy(update={"table": "vw_customer_geography"}),
            destination=dest_db.model_copy(update={"table": "dim_customer_geography"}),
            watermark=WatermarkConfig(
                column="version_id",
                type=WatermarkType.INTEGER,
                storage_type="sqlite",
                storage_path="./watermarks/geographic_distribution.db"
            )
        ),
        
        # Mapping 4: No watermark (full sync)
        SourceDestinationMapping(
            name="lifetime_value",
            source=source_db.model_copy(update={"table": "vw_customer_ltv"}),
            destination=dest_db.model_copy(update={"table": "fact_customer_ltv"}),
            # No watermark specified - will do full sync each time
        )
    ]
    
    config = MultiCDCConfig(
        name="customer_analytics_watermarks",
        mappings=mappings,
        parallel_execution=True
    )
    
    print("Watermark Configuration Summary:")
    print("=" * 50)
    
    for mapping in config.mappings:
        print(f"\nMapping: {mapping.name}")
        print(f"  Source Table: {mapping.source.table}")
        print(f"  Destination Table: {mapping.destination.table}")
        
        if mapping.watermark:
            print(f"  Watermark Column: {mapping.watermark.column}")
            print(f"  Watermark Type: {mapping.watermark.type.value}")
            print(f"  Storage Path: {mapping.watermark.storage_path}")
            print(f"  ✓ Incremental sync enabled")
        else:
            print(f"  Watermark: None")
            print(f"  ⚠ Full sync each time")


def demonstrate_watermark_scenarios():
    """Demonstrate different watermark scenarios."""
    
    print("\n=== Watermark Scenarios ===\n")
    
    scenarios = [
        {
            "name": "First Run (No Previous Watermark)",
            "description": "Initial sync - fetches all data",
            "watermark_state": None,
            "query_behavior": "SELECT * FROM table ORDER BY watermark_column"
        },
        {
            "name": "Incremental Sync",
            "description": "Subsequent runs - only new/updated data",
            "watermark_state": "2024-01-15 10:30:00",
            "query_behavior": "SELECT * FROM table WHERE watermark_column > '2024-01-15 10:30:00'"
        },
        {
            "name": "Custom Query with Watermark",
            "description": "Custom SQL with watermark parameter",
            "watermark_state": "2024-01-15 10:30:00",
            "query_behavior": "Custom query with %(last_sync)s parameter"
        },
        {
            "name": "No Watermark",
            "description": "Full sync every time",
            "watermark_state": "N/A",
            "query_behavior": "SELECT * FROM table (full table scan)"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Last Watermark: {scenario['watermark_state']}")
        print(f"   Query Behavior: {scenario['query_behavior']}")
        print()


def demonstrate_parallel_watermark_execution():
    """Demonstrate how watermarks work in parallel execution."""
    
    print("=== Parallel Execution with Independent Watermarks ===\n")
    
    print("When running multiple mappings in parallel:")
    print()
    
    execution_timeline = [
        {
            "time": "10:00:00",
            "mapping1": "Start: customer_demographics (last_sync: 2024-01-15 09:45:00)",
            "mapping2": "Start: purchase_behavior (last_sync: 2024-01-15 09:30:00)",
            "mapping3": "Start: geographic_distribution (last_sync: version_id = 1250)"
        },
        {
            "time": "10:00:05",
            "mapping1": "Query: WHERE last_updated > '2024-01-15 09:45:00'",
            "mapping2": "Query: WHERE analysis_date > '2024-01-15 09:30:00'",
            "mapping3": "Query: WHERE version_id > 1250"
        },
        {
            "time": "10:00:15",
            "mapping1": "Fetched: 150 records",
            "mapping2": "Fetched: 75 records",
            "mapping3": "Fetched: 25 records"
        },
        {
            "time": "10:00:30",
            "mapping1": "Complete: Update watermark to 2024-01-15 10:00:25",
            "mapping2": "Complete: Update watermark to 2024-01-15 10:00:20",
            "mapping3": "Complete: Update watermark to version_id = 1275"
        }
    ]
    
    for step in execution_timeline:
        print(f"Time {step['time']}:")
        print(f"  Mapping 1: {step['mapping1']}")
        print(f"  Mapping 2: {step['mapping2']}")
        print(f"  Mapping 3: {step['mapping3']}")
        print()
    
    print("Key Points:")
    print("• Each mapping maintains its own watermark independently")
    print("• Watermarks are stored in separate SQLite files")
    print("• Parallel execution doesn't interfere with watermark tracking")
    print("• Each mapping fetches only its incremental data")
    print("• Watermarks are updated only after successful sync")


def demonstrate_watermark_storage():
    """Demonstrate watermark storage options."""
    
    print("=== Watermark Storage Options ===\n")
    
    storage_options = [
        {
            "type": "SQLite (Default)",
            "config": "storage_type: sqlite",
            "path": "./watermarks/mapping_name.db",
            "benefits": [
                "Persistent across restarts",
                "ACID compliance",
                "No external dependencies",
                "Separate file per mapping"
            ]
        },
        {
            "type": "In-Memory",
            "config": "storage_type: memory",
            "path": "N/A",
            "benefits": [
                "Fastest performance",
                "No disk I/O",
                "Good for testing"
            ],
            "limitations": [
                "Lost on restart",
                "Not suitable for production"
            ]
        },
        {
            "type": "Custom Database",
            "config": "storage_type: database",
            "path": "Custom connection string",
            "benefits": [
                "Centralized storage",
                "Shared across instances",
                "Enterprise features"
            ]
        }
    ]
    
    for option in storage_options:
        print(f"Storage Type: {option['type']}")
        print(f"Configuration: {option['config']}")
        print(f"Path: {option['path']}")
        print("Benefits:")
        for benefit in option['benefits']:
            print(f"  • {benefit}")
        if 'limitations' in option:
            print("Limitations:")
            for limitation in option['limitations']:
                print(f"  • {limitation}")
        print()


def demonstrate_watermark_best_practices():
    """Demonstrate watermark best practices."""
    
    print("=== Watermark Best Practices ===\n")
    
    best_practices = [
        {
            "practice": "Use Indexed Columns",
            "description": "Ensure watermark columns have proper database indexes",
            "example": "CREATE INDEX idx_last_updated ON customer_table(last_updated);"
        },
        {
            "practice": "Choose Appropriate Types",
            "description": "Use timestamp for time-based data, integer for version-based",
            "example": "timestamp: last_updated, modified_at\ninteger: version_id, sequence_number"
        },
        {
            "practice": "Handle Time Zones",
            "description": "Use UTC timestamps to avoid timezone issues",
            "example": "Store: 2024-01-15 10:30:00 UTC\nNot: 2024-01-15 10:30:00 EST"
        },
        {
            "practice": "Separate Storage Paths",
            "description": "Use different watermark files for each mapping",
            "example": "./watermarks/customer_demographics.db\n./watermarks/purchase_behavior.db"
        },
        {
            "practice": "Monitor Watermark Progress",
            "description": "Track watermark advancement to detect issues",
            "example": "Log watermark values and time differences"
        }
    ]
    
    for i, practice in enumerate(best_practices, 1):
        print(f"{i}. {practice['practice']}")
        print(f"   Description: {practice['description']}")
        print(f"   Example: {practice['example']}")
        print()


def main():
    """Run all watermark demonstrations."""
    try:
        demonstrate_independent_watermarks()
        demonstrate_watermark_scenarios()
        demonstrate_parallel_watermark_execution()
        demonstrate_watermark_storage()
        demonstrate_watermark_best_practices()
        
        print("=== Summary ===")
        print("🎉 Watermark demonstration completed!")
        
        print("\nKey Takeaways:")
        print("✓ Each mapping has independent watermark tracking")
        print("✓ Different watermark columns and types per mapping")
        print("✓ Parallel execution doesn't interfere with watermarks")
        print("✓ Persistent storage ensures resumability")
        print("✓ Only incremental data is fetched per mapping")
        print("✓ Production-ready with proper error handling")
        
    except Exception as e:
        print(f"Error running watermark demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
