#!/usr/bin/env python3
"""
Multi-Source Multi-Destination CDC Example.

This example demonstrates how to configure and run CDC with multiple data sources
and destinations, such as syncing 5 different views to different destination tables.
"""

import os
import sys
import yaml
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import (
    MultiCDCConfig, SourceDestinationMapping, DatabaseConfig, DatabaseType,
    SyncConfig, SyncMode, WatermarkConfig, WatermarkType
)
from evolvishub_data_handler.multi_cdc_handler import MultiCDCHandler


def create_customer_views_config():
    """Create configuration for syncing 5 customer views to different destination tables."""
    
    # Common source database (where the views are)
    source_db = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="source-db.company.com",
        port=5432,
        database="customer_analytics",
        username="analytics_user",
        password="analytics_password"
    )
    
    # Common destination database
    destination_db = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="warehouse-db.company.com", 
        port=5432,
        database="data_warehouse",
        username="warehouse_user",
        password="warehouse_password"
    )
    
    # Global sync settings
    global_sync = SyncConfig(
        mode=SyncMode.CONTINUOUS,
        interval_seconds=300,  # 5 minutes
        batch_size=1000
    )
    
    # Define mappings for each view
    mappings = [
        # Customer Demographics View
        SourceDestinationMapping(
            name="customer_demographics",
            description="Customer demographic information",
            source=source_db.model_copy(update={"table": "vw_customer_demographics"}),
            destination=destination_db.model_copy(update={"table": "dim_customer_demographics"}),
            watermark=WatermarkConfig(
                column="last_updated",
                type=WatermarkType.TIMESTAMP
            ),
            column_mapping={
                "customer_id": "customer_key",
                "birth_date": "date_of_birth",
                "registration_date": "customer_since"
            },
            exclude_columns=["internal_notes", "temp_field"]
        ),
        
        # Customer Purchase Behavior View
        SourceDestinationMapping(
            name="purchase_behavior",
            description="Customer purchase patterns and behavior",
            source=source_db.model_copy(update={"table": "vw_customer_purchase_behavior"}),
            destination=destination_db.model_copy(update={"table": "fact_customer_behavior"}),
            watermark=WatermarkConfig(
                column="analysis_date",
                type=WatermarkType.TIMESTAMP
            ),
            custom_query="""
                SELECT 
                    customer_id,
                    total_purchases,
                    avg_order_value,
                    last_purchase_date,
                    customer_segment,
                    analysis_date
                FROM vw_customer_purchase_behavior 
                WHERE analysis_date > %(last_sync)s
                ORDER BY analysis_date
            """
        ),
        
        # Customer Geographic Distribution
        SourceDestinationMapping(
            name="geographic_distribution",
            description="Customer geographic distribution data",
            source=source_db.model_copy(update={"table": "vw_customer_geography"}),
            destination=destination_db.model_copy(update={"table": "dim_customer_geography"}),
            watermark=WatermarkConfig(
                column="updated_at",
                type=WatermarkType.TIMESTAMP
            ),
            sync=SyncConfig(
                mode=SyncMode.CONTINUOUS,
                interval_seconds=600,  # 10 minutes - less frequent
                batch_size=500
            )
        ),
        
        # Customer Engagement Metrics
        SourceDestinationMapping(
            name="engagement_metrics",
            description="Customer engagement and activity metrics",
            source=source_db.model_copy(update={"table": "vw_customer_engagement"}),
            destination=destination_db.model_copy(update={"table": "fact_customer_engagement"}),
            watermark=WatermarkConfig(
                column="metric_date",
                type=WatermarkType.TIMESTAMP
            ),
            column_mapping={
                "customer_id": "customer_key",
                "email_opens": "email_open_count",
                "website_visits": "web_visit_count",
                "app_sessions": "mobile_session_count"
            }
        ),
        
        # Customer Lifetime Value
        SourceDestinationMapping(
            name="lifetime_value",
            description="Customer lifetime value calculations",
            source=source_db.model_copy(update={"table": "vw_customer_ltv"}),
            destination=destination_db.model_copy(update={"table": "fact_customer_ltv"}),
            watermark=WatermarkConfig(
                column="calculation_date",
                type=WatermarkType.TIMESTAMP
            ),
            sync=SyncConfig(
                mode=SyncMode.CONTINUOUS,
                interval_seconds=1800,  # 30 minutes - least frequent
                batch_size=200
            ),
            custom_query="""
                SELECT 
                    customer_id,
                    current_ltv,
                    predicted_ltv,
                    ltv_segment,
                    calculation_date,
                    model_version
                FROM vw_customer_ltv 
                WHERE calculation_date > %(last_sync)s
                  AND model_version = 'v2.1'
                ORDER BY calculation_date
            """
        )
    ]
    
    # Create multi-CDC configuration
    config = MultiCDCConfig(
        name="customer_analytics_sync",
        description="Sync customer analytics views to data warehouse",
        global_sync=global_sync,
        mappings=mappings,
        parallel_execution=True,
        max_workers=3,
        stop_on_error=False,
        enable_monitoring=True,
        log_level="INFO"
    )
    
    return config


def create_event_bus_multi_config():
    """Create configuration for syncing to multiple event buses."""
    
    # Source database
    source_db = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        database="ecommerce",
        username="postgres",
        password="password"
    )
    
    # Different event bus destinations
    kafka_dest = DatabaseConfig(
        type=DatabaseType.KAFKA,
        host="localhost",
        port=9092,
        database="kafka_cluster"
    )
    
    pulsar_dest = DatabaseConfig(
        type=DatabaseType.PULSAR,
        host="localhost",
        port=6650,
        database="public/default"
    )
    
    redis_dest = DatabaseConfig(
        type=DatabaseType.REDIS_STREAMS,
        host="localhost",
        port=6379,
        database="0"
    )
    
    # Real-time sync for event buses
    realtime_sync = SyncConfig(
        mode=SyncMode.CONTINUOUS,
        interval_seconds=10,
        batch_size=100
    )
    
    mappings = [
        # Orders to Kafka
        SourceDestinationMapping(
            name="orders_to_kafka",
            description="Stream order events to Kafka",
            source=source_db.model_copy(update={"table": "orders"}),
            destination=kafka_dest.model_copy(update={"table": "order_events"}),
            sync=realtime_sync,
            watermark=WatermarkConfig(column="updated_at", type=WatermarkType.TIMESTAMP)
        ),
        
        # Customer events to Pulsar
        SourceDestinationMapping(
            name="customers_to_pulsar",
            description="Stream customer events to Pulsar",
            source=source_db.model_copy(update={"table": "customers"}),
            destination=pulsar_dest.model_copy(update={"table": "persistent://public/default/customer_events"}),
            sync=realtime_sync,
            watermark=WatermarkConfig(column="updated_at", type=WatermarkType.TIMESTAMP)
        ),
        
        # Product updates to Redis Streams
        SourceDestinationMapping(
            name="products_to_redis",
            description="Stream product updates to Redis",
            source=source_db.model_copy(update={"table": "products"}),
            destination=redis_dest.model_copy(update={"table": "product_updates"}),
            sync=realtime_sync,
            watermark=WatermarkConfig(column="updated_at", type=WatermarkType.TIMESTAMP)
        )
    ]
    
    return MultiCDCConfig(
        name="ecommerce_event_streaming",
        description="Stream ecommerce data to multiple event buses",
        global_sync=realtime_sync,
        mappings=mappings,
        parallel_execution=True,
        max_workers=3,
        stop_on_error=False,
        log_level="INFO"
    )


def demonstrate_multi_cdc():
    """Demonstrate multi-source CDC functionality."""
    print("=== Multi-Source Multi-Destination CDC Example ===\n")
    
    # Create customer views configuration
    print("1. Customer Analytics Views Configuration:")
    customer_config = create_customer_views_config()
    
    print(f"   Configuration: {customer_config.name}")
    print(f"   Description: {customer_config.description}")
    print(f"   Number of mappings: {len(customer_config.mappings)}")
    print(f"   Parallel execution: {customer_config.parallel_execution}")
    print(f"   Max workers: {customer_config.max_workers}")
    
    print("\n   Mappings:")
    for mapping in customer_config.mappings:
        print(f"   • {mapping.name}: {mapping.source.table} → {mapping.destination.table}")
        if mapping.custom_query:
            print(f"     - Uses custom query")
        if mapping.column_mapping:
            print(f"     - Column mapping: {len(mapping.column_mapping)} columns")
        if mapping.exclude_columns:
            print(f"     - Excludes: {mapping.exclude_columns}")
    
    # Create event bus configuration
    print("\n2. Event Bus Streaming Configuration:")
    event_config = create_event_bus_multi_config()
    
    print(f"   Configuration: {event_config.name}")
    print(f"   Description: {event_config.description}")
    print(f"   Number of mappings: {len(event_config.mappings)}")
    
    print("\n   Event Bus Mappings:")
    for mapping in event_config.mappings:
        dest_type = mapping.destination.type.value
        print(f"   • {mapping.name}: {mapping.source.table} → {dest_type}")
    
    # Demonstrate handler creation (without actual execution)
    print("\n3. Multi-CDC Handler Creation:")
    try:
        handler = MultiCDCHandler(customer_config)
        print(f"   ✓ Handler created successfully")
        print(f"   ✓ Initialized {len(handler.mapping_handlers)} mapping handlers")
        
        # Get status
        status = handler.get_mapping_status()
        print(f"   ✓ Mapping status retrieved for {len(status)} mappings")
        
        # Get summary
        summary = handler.get_summary()
        print(f"   ✓ Summary: {summary['enabled_mappings']}/{summary['total_mappings']} mappings enabled")
        
    except Exception as e:
        print(f"   ⚠ Handler creation failed (expected without actual databases): {e}")
    
    print("\n4. Configuration Export:")
    
    # Export to YAML
    config_dict = customer_config.model_dump()
    yaml_config = yaml.dump(config_dict, default_flow_style=False, indent=2)
    
    print("   Customer analytics configuration (YAML):")
    print("   " + "\n   ".join(yaml_config.split("\n")[:20]))  # Show first 20 lines
    print("   ... (truncated)")


def demonstrate_execution_patterns():
    """Demonstrate different execution patterns."""
    print("\n=== Execution Patterns ===\n")
    
    print("1. Sequential Execution:")
    print("   - Mappings execute one after another")
    print("   - Safer for resource-constrained environments")
    print("   - Easier debugging and monitoring")
    
    print("\n2. Parallel Execution:")
    print("   - Multiple mappings execute simultaneously")
    print("   - Faster overall completion time")
    print("   - Better resource utilization")
    print("   - Configurable worker pool size")
    
    print("\n3. Error Handling:")
    print("   - stop_on_error=True: Stop all if one fails")
    print("   - stop_on_error=False: Continue with other mappings")
    print("   - Individual mapping results tracked")
    
    print("\n4. Monitoring:")
    print("   - Real-time status for each mapping")
    print("   - Execution history and metrics")
    print("   - Success/failure tracking")
    print("   - Performance statistics")


def demonstrate_cli_usage():
    """Demonstrate CLI usage for multi-CDC."""
    print("\n=== CLI Usage ===\n")
    
    print("Multi-CDC configuration file (multi_customer_sync.yaml):")
    print("""
name: customer_analytics_sync
description: Sync customer analytics views to data warehouse
global_sync:
  mode: continuous
  interval_seconds: 300
  batch_size: 1000
mappings:
  - name: customer_demographics
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_demographics
    destination:
      type: postgresql
      host: warehouse-db.company.com
      database: data_warehouse
      table: dim_customer_demographics
    watermark:
      column: last_updated
      type: timestamp
  # ... more mappings
parallel_execution: true
max_workers: 3
""")
    
    print("CLI commands:")
    print("  # Run multi-CDC configuration")
    print("  evolvishub-cdc run-multi -c multi_customer_sync.yaml")
    print()
    print("  # Run specific mapping only")
    print("  evolvishub-cdc run-multi -c multi_customer_sync.yaml --mapping customer_demographics")
    print()
    print("  # Run in sequential mode")
    print("  evolvishub-cdc run-multi -c multi_customer_sync.yaml --sequential")
    print()
    print("  # Monitor status")
    print("  evolvishub-cdc status -c multi_customer_sync.yaml")


def main():
    """Run all multi-CDC demonstrations."""
    try:
        demonstrate_multi_cdc()
        demonstrate_execution_patterns()
        demonstrate_cli_usage()
        
        print("\n=== Summary ===")
        print("🎉 Multi-source multi-destination CDC examples completed!")
        
        print("\nKey benefits:")
        print("• Configure multiple source-destination pairs in one file")
        print("• Parallel or sequential execution")
        print("• Individual mapping configuration and monitoring")
        print("• Custom queries and column mapping")
        print("• Event bus integration for real-time streaming")
        print("• Production-ready error handling and monitoring")
        
    except Exception as e:
        print(f"Error running multi-CDC demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
