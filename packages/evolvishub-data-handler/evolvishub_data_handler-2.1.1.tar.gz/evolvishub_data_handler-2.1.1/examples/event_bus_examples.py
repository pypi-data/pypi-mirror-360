#!/usr/bin/env python3
"""
Event Bus Integration Examples.

This example demonstrates:
1. Apache Kafka - Industry-standard event streaming
2. Apache Pulsar - Next-generation messaging
3. Redis Streams - Lightweight event streaming
4. RabbitMQ - Enterprise messaging patterns
5. Multi-event bus architectures
"""

import os
import sys
import yaml

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvishub_data_handler.config import CDCConfig


def create_kafka_config():
    """Create Kafka event streaming configuration."""
    return {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "database": "ecommerce",
            "username": "postgres",
            "password": "password",
            "table": "orders",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp"
            }
        },
        "destination": {
            "type": "kafka",
            "host": "localhost",
            "port": 9092,
            "database": "kafka_cluster",
            "table": "order_events",
            
            # Kafka-specific settings
            "key_field": "order_id",
            "compression_type": "gzip",
            "acks": "all",
            "retries": 3,
            "security_protocol": "PLAINTEXT"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 10
        }
    }


def create_pulsar_config():
    """Create Apache Pulsar messaging configuration."""
    return {
        "source": {
            "type": "kafka",
            "host": "localhost",
            "port": 9092,
            "database": "kafka_cluster",
            "table": "order_events",
            "group_id": "pulsar_bridge"
        },
        "destination": {
            "type": "pulsar",
            "host": "localhost",
            "port": 6650,
            "database": "public/default",
            "table": "persistent://public/default/processed_orders",
            
            # Pulsar-specific settings
            "subscription_name": "cdc_subscription",
            "subscription_type": "shared",
            "compression_type": "LZ4",
            "batching_enabled": True,
            "key_field": "order_id"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 5
        }
    }


def create_redis_streams_config():
    """Create Redis Streams configuration."""
    return {
        "source": {
            "type": "pulsar",
            "host": "localhost",
            "port": 6650,
            "database": "public/default",
            "table": "persistent://public/default/processed_orders",
            "subscription_name": "redis_bridge"
        },
        "destination": {
            "type": "redis_streams",
            "host": "localhost",
            "port": 6379,
            "database": "0",
            "table": "order_stream",
            
            # Redis Streams settings
            "consumer_group": "analytics_group",
            "consumer_name": "analytics_worker",
            "max_length": 10000,
            "key_field": "order_id"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 2
        }
    }


def create_rabbitmq_config():
    """Create RabbitMQ messaging configuration."""
    return {
        "source": {
            "type": "redis_streams",
            "host": "localhost",
            "port": 6379,
            "database": "0",
            "table": "order_stream",
            "consumer_group": "rabbitmq_bridge",
            "consumer_name": "rabbitmq_worker"
        },
        "destination": {
            "type": "rabbitmq",
            "host": "localhost",
            "port": 5672,
            "database": "/",
            "table": "processed_orders",
            
            # RabbitMQ settings
            "username": "guest",
            "password": "guest",
            "exchange": "orders_exchange",
            "exchange_type": "topic",
            "routing_key": "orders.processed",
            "queue_durable": True,
            "delivery_mode": 2,
            "key_field": "order_id"
        },
        "sync": {
            "mode": "continuous",
            "interval_seconds": 1
        }
    }


def create_multi_destination_config():
    """Create configuration with multiple event bus destinations."""
    return {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "database": "analytics",
            "username": "analytics_user",
            "password": "analytics_password",
            "table": "user_events",
            "watermark": {
                "column": "event_timestamp",
                "type": "timestamp"
            }
        },
        # Note: Multi-destination would require multiple CDC handlers
        # This shows the configuration for each destination
        "destinations": [
            {
                "name": "kafka_stream",
                "type": "kafka",
                "host": "localhost",
                "port": 9092,
                "database": "kafka_cluster",
                "table": "user_events",
                "key_field": "user_id"
            },
            {
                "name": "pulsar_stream",
                "type": "pulsar",
                "host": "localhost",
                "port": 6650,
                "database": "public/default",
                "table": "persistent://public/default/user_events",
                "key_field": "user_id"
            },
            {
                "name": "redis_cache",
                "type": "redis_streams",
                "host": "localhost",
                "port": 6379,
                "database": "1",
                "table": "user_events_stream",
                "key_field": "user_id"
            }
        ],
        "sync": {
            "mode": "continuous",
            "interval_seconds": 5
        }
    }


def demonstrate_kafka_integration():
    """Demonstrate Kafka integration."""
    print("=== Apache Kafka Integration ===")
    
    config_dict = create_kafka_config()
    
    print("Features:")
    print("  • Industry-standard event streaming")
    print("  • High-throughput, low-latency messaging")
    print("  • Distributed, fault-tolerant architecture")
    print("  • Strong ordering guarantees per partition")
    
    print(f"\nConfiguration:")
    print(f"  Source: {config_dict['source']['type']} -> {config_dict['source']['table']}")
    print(f"  Destination: {config_dict['destination']['type']} -> {config_dict['destination']['table']}")
    print(f"  Key field: {config_dict['destination']['key_field']}")
    print(f"  Compression: {config_dict['destination']['compression_type']}")
    
    try:
        config = CDCConfig(**config_dict)
        print("✓ Kafka configuration validated")
    except Exception as e:
        print(f"⚠ Kafka configuration error: {e}")


def demonstrate_pulsar_integration():
    """Demonstrate Apache Pulsar integration."""
    print("\n=== Apache Pulsar Integration ===")
    
    config_dict = create_pulsar_config()
    
    print("Features:")
    print("  • Next-generation messaging platform")
    print("  • Multi-tenancy and geo-replication")
    print("  • Unified messaging and streaming")
    print("  • Schema evolution support")
    
    print(f"\nConfiguration:")
    print(f"  Source: {config_dict['source']['type']} -> {config_dict['source']['table']}")
    print(f"  Destination: {config_dict['destination']['type']} -> {config_dict['destination']['table']}")
    print(f"  Subscription: {config_dict['destination']['subscription_name']}")
    print(f"  Compression: {config_dict['destination']['compression_type']}")
    
    try:
        config = CDCConfig(**config_dict)
        print("✓ Pulsar configuration validated")
    except Exception as e:
        print(f"⚠ Pulsar configuration error: {e}")


def demonstrate_redis_streams_integration():
    """Demonstrate Redis Streams integration."""
    print("\n=== Redis Streams Integration ===")
    
    config_dict = create_redis_streams_config()
    
    print("Features:")
    print("  • Lightweight event streaming")
    print("  • Built-in persistence and replication")
    print("  • Consumer groups for load balancing")
    print("  • Automatic stream trimming")
    
    print(f"\nConfiguration:")
    print(f"  Source: {config_dict['source']['type']} -> {config_dict['source']['table']}")
    print(f"  Destination: {config_dict['destination']['type']} -> {config_dict['destination']['table']}")
    print(f"  Consumer group: {config_dict['destination']['consumer_group']}")
    print(f"  Max length: {config_dict['destination']['max_length']}")
    
    try:
        config = CDCConfig(**config_dict)
        print("✓ Redis Streams configuration validated")
    except Exception as e:
        print(f"⚠ Redis Streams configuration error: {e}")


def demonstrate_rabbitmq_integration():
    """Demonstrate RabbitMQ integration."""
    print("\n=== RabbitMQ Integration ===")
    
    config_dict = create_rabbitmq_config()
    
    print("Features:")
    print("  • Enterprise messaging patterns")
    print("  • Complex routing with exchanges")
    print("  • Message acknowledgments and durability")
    print("  • Dead letter queues and TTL")
    
    print(f"\nConfiguration:")
    print(f"  Source: {config_dict['source']['type']} -> {config_dict['source']['table']}")
    print(f"  Destination: {config_dict['destination']['type']} -> {config_dict['destination']['table']}")
    print(f"  Exchange: {config_dict['destination']['exchange']}")
    print(f"  Routing key: {config_dict['destination']['routing_key']}")
    
    try:
        config = CDCConfig(**config_dict)
        print("✓ RabbitMQ configuration validated")
    except Exception as e:
        print(f"⚠ RabbitMQ configuration error: {e}")


def demonstrate_event_bus_pipeline():
    """Demonstrate complete event bus pipeline."""
    print("\n=== Event Bus Pipeline ===")
    
    print("Complete data flow:")
    print("  PostgreSQL → Kafka → Pulsar → Redis Streams → RabbitMQ")
    print()
    print("Pipeline stages:")
    print("  1. Database CDC → Kafka (real-time streaming)")
    print("  2. Kafka → Pulsar (cross-region replication)")
    print("  3. Pulsar → Redis Streams (caching layer)")
    print("  4. Redis Streams → RabbitMQ (enterprise integration)")
    
    print("\nBenefits:")
    print("  • Fault tolerance at each stage")
    print("  • Different messaging patterns for different needs")
    print("  • Horizontal scaling capabilities")
    print("  • Technology-specific optimizations")


def demonstrate_cli_usage():
    """Demonstrate CLI usage for event bus integrations."""
    print("\n=== CLI Usage Examples ===")
    
    print("Kafka streaming:")
    print("  evolvishub-cdc run -c kafka_config.yaml -m continuous")
    print()
    
    print("Pulsar messaging:")
    print("  evolvishub-cdc run -c pulsar_config.yaml -m continuous")
    print()
    
    print("Redis Streams:")
    print("  evolvishub-cdc run -c redis_streams_config.yaml -m continuous")
    print()
    
    print("RabbitMQ messaging:")
    print("  evolvishub-cdc run -c rabbitmq_config.yaml -m continuous")
    print()
    
    print("With monitoring:")
    print("  evolvishub-cdc run -c config.yaml -l INFO --log-file event_bus.log")


def demonstrate_installation():
    """Demonstrate installation requirements."""
    print("\n=== Installation Requirements ===")
    
    print("Event bus dependencies:")
    print("  pip install kafka-python      # Apache Kafka")
    print("  pip install pulsar-client     # Apache Pulsar")
    print("  pip install redis             # Redis Streams")
    print("  pip install pika              # RabbitMQ")
    print()
    
    print("All event buses:")
    print("  pip install kafka-python pulsar-client redis pika")


def main():
    """Run all event bus demonstrations."""
    print("Event Bus Integration Examples")
    print("==============================")
    
    try:
        demonstrate_kafka_integration()
        demonstrate_pulsar_integration()
        demonstrate_redis_streams_integration()
        demonstrate_rabbitmq_integration()
        demonstrate_event_bus_pipeline()
        demonstrate_cli_usage()
        demonstrate_installation()
        
        print("\n=== Summary ===")
        print("🎉 Event bus integration examples completed!")
        
        print("\nSupported event buses:")
        print("✓ Apache Kafka - Industry-standard streaming")
        print("✓ Apache Pulsar - Next-generation messaging")
        print("✓ Redis Streams - Lightweight event streaming")
        print("✓ RabbitMQ - Enterprise messaging patterns")
        
        print("\nKey capabilities:")
        print("• Real-time event streaming")
        print("• Multi-tenant messaging")
        print("• Complex routing patterns")
        print("• Fault-tolerant architectures")
        print("• Cross-technology integration")
        
    except Exception as e:
        print(f"Error running event bus demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
