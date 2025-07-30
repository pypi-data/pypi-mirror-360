"""
Kafka adapter for event streaming CDC.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

from .base import BaseAdapter
from ..config import DatabaseConfig

logger = logging.getLogger(__name__)


class KafkaAdapter(BaseAdapter):
    """Kafka adapter for event streaming CDC operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize Kafka adapter.
        
        Args:
            config: Database configuration with Kafka-specific settings
        """
        super().__init__(config)
        
        if not KAFKA_AVAILABLE:
            raise ImportError(
                "kafka-python package is required for Kafka adapter. "
                "Install with: pip install kafka-python"
            )
        
        self.bootstrap_servers = f"{config.host}:{config.port}"
        self.topic = config.table  # Use table field as topic name
        
        # Kafka-specific configuration
        self.consumer_config = self._build_consumer_config()
        self.producer_config = self._build_producer_config()
        
        self.consumer: Optional[KafkaConsumer] = None
        self.producer: Optional[KafkaProducer] = None
        
        # CDC-specific settings
        self.message_format = getattr(config, 'message_format', 'json')
        self.key_field = getattr(config, 'key_field', None)
        self.watermark_field = None
        if hasattr(config, 'watermark') and config.watermark:
            self.watermark_field = config.watermark.column
        
        logger.info(f"Initialized Kafka adapter for topic: {self.topic}")

    def _build_consumer_config(self) -> Dict[str, Any]:
        """Build Kafka consumer configuration."""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'auto_offset_reset': getattr(self.config, 'auto_offset_reset', 'earliest'),
            'enable_auto_commit': False,  # Manual commit for CDC reliability
            'group_id': getattr(self.config, 'group_id', 'evolvishub_cdc'),
            'value_deserializer': self._deserialize_message,
            'key_deserializer': lambda x: x.decode('utf-8') if x else None,
            'consumer_timeout_ms': getattr(self.config, 'consumer_timeout_ms', 10000),
        }
        
        # Add security configuration if provided
        if hasattr(self.config, 'security_protocol'):
            config['security_protocol'] = self.config.security_protocol
            
        if hasattr(self.config, 'sasl_mechanism'):
            config['sasl_mechanism'] = self.config.sasl_mechanism
            config['sasl_plain_username'] = getattr(self.config, 'sasl_username', '')
            config['sasl_plain_password'] = getattr(self.config, 'sasl_password', '')
        
        return config

    def _build_producer_config(self) -> Dict[str, Any]:
        """Build Kafka producer configuration."""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'value_serializer': self._serialize_message,
            'key_serializer': lambda x: x.encode('utf-8') if x else None,
            'acks': getattr(self.config, 'acks', 'all'),  # Wait for all replicas
            'retries': getattr(self.config, 'retries', 3),
            'compression_type': getattr(self.config, 'compression_type', 'gzip'),
        }
        
        # Add security configuration if provided
        if hasattr(self.config, 'security_protocol'):
            config['security_protocol'] = self.config.security_protocol
            
        if hasattr(self.config, 'sasl_mechanism'):
            config['sasl_mechanism'] = self.config.sasl_mechanism
            config['sasl_plain_username'] = getattr(self.config, 'sasl_username', '')
            config['sasl_plain_password'] = getattr(self.config, 'sasl_password', '')
        
        return config

    def _serialize_message(self, message: Dict[str, Any]) -> bytes:
        """Serialize message for Kafka producer."""
        if self.message_format == 'json':
            return json.dumps(message, default=str).encode('utf-8')
        else:
            raise ValueError(f"Unsupported message format: {self.message_format}")

    def _deserialize_message(self, message: bytes) -> Dict[str, Any]:
        """Deserialize message from Kafka consumer."""
        if message is None:
            return {}
            
        try:
            if self.message_format == 'json':
                return json.loads(message.decode('utf-8'))
            else:
                raise ValueError(f"Unsupported message format: {self.message_format}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to deserialize message: {e}")
            return {}

    def connect(self) -> None:
        """Connect to Kafka cluster."""
        try:
            # Test connection by creating a temporary consumer
            test_consumer = KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                consumer_timeout_ms=5000
            )
            test_consumer.close()
            
            logger.info(f"Connected to Kafka cluster: {self.bootstrap_servers}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from Kafka cluster."""
        try:
            if self.consumer:
                self.consumer.close()
                self.consumer = None
                
            if self.producer:
                self.producer.flush()
                self.producer.close()
                self.producer = None
                
            logger.info("Disconnected from Kafka cluster")
            
        except Exception as e:
            logger.warning(f"Error during Kafka disconnect: {e}")

    def execute_query(self, query: str = None, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Read messages from Kafka topic.
        
        Args:
            query: Not used for Kafka (topic is specified in config)
            params: Query parameters including batch_size and last_sync
            
        Returns:
            List of messages from Kafka topic
        """
        if not self.consumer:
            self.consumer = KafkaConsumer(self.topic, **self.consumer_config)
            
        batch_size = params.get('batch_size', 1000) if params else 1000
        last_sync = params.get('last_sync') if params else None
        
        messages = []
        message_count = 0
        
        try:
            # Poll for messages
            message_batch = self.consumer.poll(timeout_ms=10000, max_records=batch_size)
            
            for topic_partition, records in message_batch.items():
                for record in records:
                    message_data = record.value
                    
                    if not message_data:
                        continue
                    
                    # Add Kafka metadata
                    message_data['_kafka_offset'] = record.offset
                    message_data['_kafka_partition'] = record.partition
                    message_data['_kafka_timestamp'] = record.timestamp
                    message_data['_kafka_key'] = record.key
                    
                    # Apply watermark filtering if configured
                    if self.watermark_field and last_sync:
                        message_time = message_data.get(self.watermark_field)
                        if message_time and message_time <= last_sync:
                            continue
                    
                    messages.append(message_data)
                    message_count += 1
                    
                    if message_count >= batch_size:
                        break
                        
                if message_count >= batch_size:
                    break
            
            # Commit offsets after successful processing
            if messages:
                self.consumer.commit()
                
            logger.info(f"Read {len(messages)} messages from Kafka topic: {self.topic}")
            return messages
            
        except Exception as e:
            logger.error(f"Error reading from Kafka topic {self.topic}: {e}")
            raise

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Publish messages to Kafka topic.
        
        Args:
            table: Kafka topic name (overrides config if provided)
            data: List of messages to publish
        """
        if not self.producer:
            self.producer = KafkaProducer(**self.producer_config)
            
        topic = table or self.topic
        
        try:
            for record in data:
                # Extract key if key_field is configured
                key = None
                if self.key_field and self.key_field in record:
                    key = str(record[self.key_field])
                
                # Remove Kafka metadata fields before publishing
                clean_record = {k: v for k, v in record.items() 
                              if not k.startswith('_kafka_')}
                
                # Send message
                future = self.producer.send(topic, value=clean_record, key=key)
                
                # Optional: wait for confirmation (can be disabled for performance)
                if getattr(self.config, 'wait_for_confirmation', True):
                    future.get(timeout=10)
            
            # Ensure all messages are sent
            self.producer.flush()
            
            logger.info(f"Published {len(data)} messages to Kafka topic: {topic}")
            
        except Exception as e:
            logger.error(f"Error publishing to Kafka topic {topic}: {e}")
            raise

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update operation for Kafka (same as insert - publish new messages)."""
        self.insert_data(table, data)

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete operation for Kafka (publish tombstone messages)."""
        if not self.producer:
            self.producer = KafkaProducer(**self.producer_config)
            
        topic = table or self.topic
        
        try:
            # Create tombstone message (null value with key)
            if self.key_field and self.key_field in conditions:
                key = str(conditions[self.key_field])
                
                # Send tombstone message
                future = self.producer.send(topic, value=None, key=key)
                
                if getattr(self.config, 'wait_for_confirmation', True):
                    future.get(timeout=10)
                
                self.producer.flush()
                
                logger.info(f"Published tombstone message for key {key} to topic: {topic}")
            else:
                logger.warning("Cannot delete from Kafka without key_field configuration")
                
        except Exception as e:
            logger.error(f"Error publishing tombstone to Kafka topic {topic}: {e}")
            raise

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get last sync timestamp from Kafka consumer offset."""
        # For Kafka, we rely on consumer group offsets rather than timestamps
        # This is handled by the Kafka consumer automatically
        return None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update last sync timestamp (handled by Kafka consumer commits)."""
        # Kafka handles this through consumer offset commits
        pass

    def test_connection(self) -> bool:
        """Test Kafka connection."""
        try:
            self.connect()
            return True
        except Exception as e:
            logger.error(f"Kafka connection test failed: {e}")
            return False
