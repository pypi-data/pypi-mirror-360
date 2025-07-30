#!/usr/bin/env python3
"""
Kafka CDC integration examples.

This example demonstrates:
1. Database to Kafka streaming
2. Kafka to database ingestion
3. Kafka to Kafka transformation
4. Real-time event processing
5. Multi-destination fan-out
"""

import os
import sys
import yaml
import time

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import CDCConfig
from evolvishub_data_handler.cdc_handler import CDCHandler


def create_database_to_kafka_config():
    """Create configuration for streaming database changes to Kafka."""
    return {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "ecommerce",
            "username": "postgres",
            "password": "password",
            "table": "orders",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp",
                "initial_value": "2024-01-01 00:00:00"
            }
        },
        "destination": {
            "type": "kafka",
            "host": "localhost",
            "port": 9092,
            "database": "kafka_cluster",  # Kafka cluster name
            "table": "order_events",  # Kafka topic

            # Kafka-specific configuration
            "key_field": "order_id",
            "compression_type": "gzip",
            "acks": "all",
            "retries": 3
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 10,
            "batch_size": 100
        },
        "plugins": {
            "transformers": {
                "transformers": [
                    {
                        "type": "field_mapper",
                        "params": {
                            "mapping": {
                                "order_id": "id",
                                "customer_id": "customerId",
                                "order_total": "amount"
                            }
                        }
                    },
                    {
                        "type": "data_type_converter",
                        "params": {
                            "conversions": {
                                "amount": "float",
                                "customerId": "str"
                            }
                        }
                    }
                ]
            },
            "middleware": {
                "middleware": [
                    {
                        "type": "logging",
                        "params": {"level": "INFO"}
                    },
                    {
                        "type": "metrics",
                        "params": {}
                    }
                ]
            },
            "hooks": {
                "hooks": [
                    {
                        "type": "webhook",
                        "params": {
                            "url": "https://api.company.com/order-events"
                        },
                        "events": ["sync_start", "sync_end", "error"]
                    }
                ]
            }
        }
    }


def create_kafka_to_database_config():
    """Create configuration for ingesting Kafka events to database."""
    return {
        "source": {
            "type": "kafka",
            "host": "localhost",
            "port": 9092,
            "database": "kafka_cluster",  # Kafka cluster name
            "table": "user_events",  # Kafka topic

            # Kafka consumer configuration
            "group_id": "analytics_consumer",
            "auto_offset_reset": "earliest",
            "consumer_timeout_ms": 30000,
            
            # Security (if needed)
            # "security_protocol": "SASL_SSL",
            # "sasl_mechanism": "PLAIN",
            # "sasl_username": "user",
            # "sasl_password": "password",
            
            # CDC watermark based on message timestamp
            "watermark": {
                "column": "event_timestamp",
                "type": "timestamp"
            }
        },
        "destination": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "analytics",
            "username": "analytics_user",
            "password": "analytics_password",
            "table": "user_analytics"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 5,
            "batch_size": 500
        },
        "plugins": {
            "transformers": {
                "transformers": [
                    {
                        "type": "field_filter",
                        "params": {
                            "exclude": ["_kafka_offset", "_kafka_partition"]
                        }
                    },
                    {
                        "type": "date_formatter",
                        "params": {
                            "formats": {
                                "event_timestamp": {
                                    "input_format": "%Y-%m-%dT%H:%M:%SZ",
                                    "output_format": "%Y-%m-%d %H:%M:%S"
                                }
                            }
                        }
                    }
                ]
            },
            "middleware": {
                "middleware": [
                    {
                        "type": "validation",
                        "params": {
                            "rules": {
                                "user_id": {"required": True, "type": "string"},
                                "event_type": {"required": True, "type": "string"}
                            },
                            "strict": False
                        }
                    },
                    {
                        "type": "data_quality",
                        "params": {"checks": {}}
                    }
                ]
            }
        }
    }


def create_kafka_to_kafka_config():
    """Create configuration for Kafka-to-Kafka transformation."""
    return {
        "source": {
            "type": "kafka",
            "host": "localhost",
            "port": 9092,
            "database": "kafka_cluster",
            "table": "raw_events",
            "group_id": "transformation_pipeline",
            "auto_offset_reset": "latest"
        },
        "destination": {
            "type": "kafka",
            "host": "localhost",
            "port": 9092,
            "database": "kafka_cluster",
            "table": "processed_events",
            "key_field": "user_id",
            "compression_type": "snappy"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 1,  # Near real-time
            "batch_size": 50
        },
        "plugins": {
            "transformers": {
                "transformers": [
                    {
                        "type": "json_flattener",
                        "params": {
                            "fields": ["metadata", "properties"],
                            "separator": "_"
                        }
                    },
                    {
                        "type": "value_replacer",
                        "params": {
                            "rules": {
                                "event_type": [
                                    {"type": "exact", "from": "click", "to": "user_click"},
                                    {"type": "exact", "from": "view", "to": "page_view"}
                                ]
                            }
                        }
                    },
                    {
                        "type": "field_mapper",
                        "params": {
                            "mapping": {
                                "ts": "timestamp",
                                "uid": "user_id"
                            }
                        }
                    }
                ]
            }
        }
    }


def demonstrate_database_to_kafka():
    """Demonstrate streaming database changes to Kafka."""
    print("=== Database to Kafka Streaming ===")
    
    config_dict = create_database_to_kafka_config()
    
    print("Configuration:")
    print(f"  Source: {config_dict['source']['type']} -> {config_dict['source']['table']}")
    print(f"  Destination: {config_dict['destination']['type']} -> {config_dict['destination']['table']}")
    print(f"  Sync mode: {config_dict['sync']['mode']}")
    print(f"  Transformations: {len(config_dict['plugins']['transformers']['transformers'])}")
    
    # Save configuration
    with open("db_to_kafka_config.yaml", "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print("✓ Configuration saved to db_to_kafka_config.yaml")
    
    try:
        config = CDCConfig(**config_dict)
        print("✓ Configuration validated successfully")
        
        # Note: In production, you would run:
        # handler = CDCHandler(config)
        # handler.run_continuous()
        
    except Exception as e:
        print(f"⚠ Configuration validation failed: {e}")
    
    # Cleanup
    if os.path.exists("db_to_kafka_config.yaml"):
        os.remove("db_to_kafka_config.yaml")


def demonstrate_kafka_to_database():
    """Demonstrate ingesting Kafka events to database."""
    print("\n=== Kafka to Database Ingestion ===")
    
    config_dict = create_kafka_to_database_config()
    
    print("Configuration:")
    print(f"  Source: {config_dict['source']['type']} -> {config_dict['source']['table']}")
    print(f"  Destination: {config_dict['destination']['type']} -> {config_dict['destination']['table']}")
    print(f"  Consumer group: {config_dict['source']['group_id']}")
    print(f"  Validation rules: {len(config_dict['plugins']['transformers']['transformers'])}")
    
    # Save configuration
    with open("kafka_to_db_config.yaml", "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print("✓ Configuration saved to kafka_to_db_config.yaml")
    
    try:
        config = CDCConfig(**config_dict)
        print("✓ Configuration validated successfully")
        
    except Exception as e:
        print(f"⚠ Configuration validation failed: {e}")
    
    # Cleanup
    if os.path.exists("kafka_to_db_config.yaml"):
        os.remove("kafka_to_db_config.yaml")


def demonstrate_kafka_to_kafka():
    """Demonstrate Kafka-to-Kafka transformation."""
    print("\n=== Kafka to Kafka Transformation ===")
    
    config_dict = create_kafka_to_kafka_config()
    
    print("Configuration:")
    print(f"  Source topic: {config_dict['source']['table']}")
    print(f"  Destination topic: {config_dict['destination']['table']}")
    print(f"  Processing latency: {config_dict['sync']['interval_seconds']}s")
    print(f"  Transformations: {len(config_dict['plugins']['transformers']['transformers'])}")
    
    # Save configuration
    with open("kafka_to_kafka_config.yaml", "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print("✓ Configuration saved to kafka_to_kafka_config.yaml")
    
    try:
        config = CDCConfig(**config_dict)
        print("✓ Configuration validated successfully")
        
    except Exception as e:
        print(f"⚠ Configuration validation failed: {e}")
    
    # Cleanup
    if os.path.exists("kafka_to_kafka_config.yaml"):
        os.remove("kafka_to_kafka_config.yaml")


def demonstrate_cli_usage():
    """Demonstrate CLI usage for Kafka CDC."""
    print("\n=== CLI Usage Examples ===")
    
    print("Database to Kafka streaming:")
    print("  evolvishub-cdc run -c db_to_kafka_config.yaml -m continuous")
    print()
    
    print("Kafka to Database ingestion:")
    print("  evolvishub-cdc run -c kafka_to_db_config.yaml -m continuous")
    print()
    
    print("Kafka to Kafka transformation:")
    print("  evolvishub-cdc run -c kafka_to_kafka_config.yaml -m continuous")
    print()
    
    print("With custom logging:")
    print("  evolvishub-cdc run -c config.yaml -l DEBUG --log-file kafka_cdc.log")


def demonstrate_use_cases():
    """Demonstrate real-world Kafka CDC use cases."""
    print("\n=== Real-World Use Cases ===")
    
    print("🔄 Event Sourcing:")
    print("  • Database changes → Kafka event stream")
    print("  • Immutable event log for audit and replay")
    print("  • Multiple consumers for different views")
    
    print("\n📊 Real-time Analytics:")
    print("  • User events → Kafka → Analytics database")
    print("  • Stream processing for real-time dashboards")
    print("  • Data quality validation and enrichment")
    
    print("\n🔗 Microservices Integration:")
    print("  • Service A changes → Kafka → Service B updates")
    print("  • Decoupled architecture with event-driven communication")
    print("  • Reliable message delivery with Kafka guarantees")
    
    print("\n🚨 Monitoring & Alerting:")
    print("  • System events → Kafka → Monitoring systems")
    print("  • Real-time alerting on critical events")
    print("  • Metrics collection and aggregation")
    
    print("\n💾 Data Lake Ingestion:")
    print("  • Multiple sources → Kafka → Data lake (S3/GCS)")
    print("  • Schema evolution and data versioning")
    print("  • Batch and streaming data processing")


def demonstrate_advanced_features():
    """Demonstrate advanced Kafka CDC features."""
    print("\n=== Advanced Features ===")
    
    print("🔐 Security:")
    print("  • SASL/SSL authentication")
    print("  • Schema registry integration")
    print("  • Message encryption")
    
    print("\n⚡ Performance:")
    print("  • Compression (gzip, snappy, lz4)")
    print("  • Batch processing optimization")
    print("  • Parallel consumer groups")
    
    print("\n🔄 Reliability:")
    print("  • At-least-once delivery guarantees")
    print("  • Consumer offset management")
    print("  • Error handling and retry logic")
    
    print("\n📈 Monitoring:")
    print("  • Consumer lag monitoring")
    print("  • Throughput and latency metrics")
    print("  • Dead letter queue handling")


def main():
    """Run all Kafka CDC demonstrations."""
    print("Kafka CDC Integration Examples")
    print("==============================")
    
    try:
        demonstrate_database_to_kafka()
        demonstrate_kafka_to_database()
        demonstrate_kafka_to_kafka()
        demonstrate_cli_usage()
        demonstrate_use_cases()
        demonstrate_advanced_features()
        
        print("\n=== Summary ===")
        print("🎉 Kafka CDC integration examples completed!")
        
        print("\nKey capabilities:")
        print("✓ Database to Kafka streaming")
        print("✓ Kafka to database ingestion")
        print("✓ Kafka to Kafka transformation")
        print("✓ Real-time event processing")
        print("✓ Production-ready configuration")
        
        print("\nNext steps:")
        print("• Install kafka-python: pip install kafka-python")
        print("• Set up Kafka cluster or use Docker")
        print("• Configure security and monitoring")
        print("• Test with sample data")
        
    except Exception as e:
        print(f"Error running Kafka CDC demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
