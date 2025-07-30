"""
Apache Pulsar adapter for event streaming CDC.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import pulsar
    PULSAR_AVAILABLE = True
except ImportError:
    PULSAR_AVAILABLE = False

from .base import BaseAdapter
from ..config import DatabaseConfig

logger = logging.getLogger(__name__)


class PulsarAdapter(BaseAdapter):
    """Apache Pulsar adapter for event streaming CDC operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize Pulsar adapter.
        
        Args:
            config: Database configuration with Pulsar-specific settings
        """
        super().__init__(config)
        
        if not PULSAR_AVAILABLE:
            raise ImportError(
                "pulsar-client package is required for Pulsar adapter. "
                "Install with: pip install pulsar-client"
            )
        
        self.service_url = f"pulsar://{config.host}:{config.port}"
        self.topic = config.table  # Use table field as topic name
        
        # Pulsar-specific configuration
        self.subscription_name = getattr(config, 'subscription_name', 'evolvishub_cdc')
        self.subscription_type = getattr(config, 'subscription_type', 'Shared')  # Will be converted to enum later
        self.consumer_name = getattr(config, 'consumer_name', 'evolvishub_consumer')

        # Producer configuration
        self.compression_type = getattr(config, 'compression_type', 'LZ4')  # Will be converted to enum later
        self.batching_enabled = getattr(config, 'batching_enabled', True)
        self.block_if_queue_full = getattr(config, 'block_if_queue_full', True)
        
        # Message configuration
        self.message_format = getattr(config, 'message_format', 'json')
        self.key_field = getattr(config, 'key_field', None)
        
        # CDC-specific settings
        self.watermark_field = None
        if hasattr(config, 'watermark') and config.watermark:
            self.watermark_field = config.watermark.column
        
        self.client: Optional[pulsar.Client] = None
        self.consumer: Optional[pulsar.Consumer] = None
        self.producer: Optional[pulsar.Producer] = None
        
        logger.info(f"Initialized Pulsar adapter for topic: {self.topic}")

    def _serialize_message(self, message: Dict[str, Any]) -> bytes:
        """Serialize message for Pulsar producer."""
        if self.message_format == 'json':
            return json.dumps(message, default=str).encode('utf-8')
        else:
            raise ValueError(f"Unsupported message format: {self.message_format}")

    def _deserialize_message(self, message: bytes) -> Dict[str, Any]:
        """Deserialize message from Pulsar consumer."""
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
        """Connect to Pulsar cluster."""
        try:
            # Create Pulsar client
            client_config = {
                'service_url': self.service_url,
                'connection_timeout_ms': getattr(self.config, 'connection_timeout_ms', 30000),
                'operation_timeout_seconds': getattr(self.config, 'operation_timeout_seconds', 30),
            }
            
            # Add authentication if configured
            if hasattr(self.config, 'auth_plugin'):
                client_config['authentication'] = pulsar.AuthenticationToken(
                    getattr(self.config, 'auth_token', '')
                )
            
            self.client = pulsar.Client(**client_config)
            
            logger.info(f"Connected to Pulsar cluster: {self.service_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Pulsar: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from Pulsar cluster."""
        try:
            if self.consumer:
                self.consumer.close()
                self.consumer = None
                
            if self.producer:
                self.producer.close()
                self.producer = None
                
            if self.client:
                self.client.close()
                self.client = None
                
            logger.info("Disconnected from Pulsar cluster")
            
        except Exception as e:
            logger.warning(f"Error during Pulsar disconnect: {e}")

    def execute_query(self, query: str = None, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Read messages from Pulsar topic.
        
        Args:
            query: Not used for Pulsar (topic is specified in config)
            params: Query parameters including batch_size and last_sync
            
        Returns:
            List of messages from Pulsar topic
        """
        if not self.client:
            self.connect()
            
        if not self.consumer:
            # Create consumer
            # Convert string subscription type to enum
            subscription_type = self.subscription_type
            if isinstance(subscription_type, str):
                subscription_type = getattr(pulsar.SubscriptionType, subscription_type, pulsar.SubscriptionType.Shared)

            consumer_config = {
                'topic': self.topic,
                'subscription_name': self.subscription_name,
                'subscription_type': subscription_type,
                'consumer_name': self.consumer_name,
                'receiver_queue_size': getattr(self.config, 'receiver_queue_size', 1000),
                'consumer_timeout_millis': getattr(self.config, 'consumer_timeout_millis', 10000),
            }
            
            self.consumer = self.client.subscribe(**consumer_config)
        
        batch_size = params.get('batch_size', 1000) if params else 1000
        last_sync = params.get('last_sync') if params else None
        
        messages = []
        message_count = 0
        
        try:
            # Receive messages
            while message_count < batch_size:
                try:
                    msg = self.consumer.receive(timeout_millis=5000)
                    
                    if msg is None:
                        break
                    
                    # Deserialize message data
                    message_data = self._deserialize_message(msg.data())
                    
                    if not message_data:
                        self.consumer.acknowledge(msg)
                        continue
                    
                    # Add Pulsar metadata
                    message_data['_pulsar_message_id'] = str(msg.message_id())
                    message_data['_pulsar_topic'] = msg.topic_name()
                    message_data['_pulsar_publish_time'] = msg.publish_timestamp()
                    message_data['_pulsar_event_time'] = msg.event_timestamp()
                    
                    # Apply watermark filtering if configured
                    if self.watermark_field and last_sync:
                        message_time = message_data.get(self.watermark_field)
                        if message_time and message_time <= last_sync:
                            self.consumer.acknowledge(msg)
                            continue
                    
                    messages.append(message_data)
                    message_count += 1
                    
                    # Acknowledge message
                    self.consumer.acknowledge(msg)
                    
                except pulsar.Timeout:
                    # No more messages available
                    break
                    
            logger.info(f"Read {len(messages)} messages from Pulsar topic: {self.topic}")
            return messages
            
        except Exception as e:
            logger.error(f"Error reading from Pulsar topic {self.topic}: {e}")
            raise

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Publish messages to Pulsar topic.
        
        Args:
            table: Pulsar topic name (overrides config if provided)
            data: List of messages to publish
        """
        if not self.client:
            self.connect()
            
        if not self.producer:
            # Create producer
            topic = table or self.topic

            # Convert string compression type to enum
            compression_type = self.compression_type
            if isinstance(compression_type, str):
                compression_type = getattr(pulsar.CompressionType, compression_type, pulsar.CompressionType.LZ4)

            producer_config = {
                'topic': topic,
                'compression_type': compression_type,
                'batching_enabled': self.batching_enabled,
                'block_if_queue_full': self.block_if_queue_full,
                'send_timeout_millis': getattr(self.config, 'send_timeout_millis', 30000),
            }
            
            self.producer = self.client.create_producer(**producer_config)
        
        try:
            for record in data:
                # Extract key if key_field is configured
                partition_key = None
                if self.key_field and self.key_field in record:
                    partition_key = str(record[self.key_field])
                
                # Remove Pulsar metadata fields before publishing
                clean_record = {k: v for k, v in record.items() 
                              if not k.startswith('_pulsar_')}
                
                # Serialize message
                message_data = self._serialize_message(clean_record)
                
                # Create message builder
                message_builder = pulsar.MessageBuilder()
                message_builder.content(message_data)
                
                if partition_key:
                    message_builder.partition_key(partition_key)
                
                # Add event timestamp if available
                if self.watermark_field and self.watermark_field in record:
                    event_time = record[self.watermark_field]
                    if isinstance(event_time, str):
                        try:
                            event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                        except ValueError:
                            pass
                    if isinstance(event_time, datetime):
                        message_builder.event_timestamp(int(event_time.timestamp() * 1000))
                
                # Send message
                message = message_builder.build()
                self.producer.send(message)
            
            # Flush producer to ensure all messages are sent
            self.producer.flush()
            
            logger.info(f"Published {len(data)} messages to Pulsar topic: {table or self.topic}")
            
        except Exception as e:
            logger.error(f"Error publishing to Pulsar topic {table or self.topic}: {e}")
            raise

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update operation for Pulsar (same as insert - publish new messages)."""
        self.insert_data(table, data)

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete operation for Pulsar (publish tombstone messages)."""
        if not self.client:
            self.connect()
            
        if not self.producer:
            topic = table or self.topic
            producer_config = {
                'topic': topic,
                'compression_type': self.compression_type,
                'batching_enabled': False,  # Disable batching for tombstones
            }
            self.producer = self.client.create_producer(**producer_config)
        
        try:
            # Create tombstone message (empty content with key)
            if self.key_field and self.key_field in conditions:
                partition_key = str(conditions[self.key_field])
                
                # Create tombstone message
                message_builder = pulsar.MessageBuilder()
                message_builder.content(b'')  # Empty content indicates deletion
                message_builder.partition_key(partition_key)
                
                # Add deletion marker property
                message_builder.property('_action', 'delete')
                
                message = message_builder.build()
                self.producer.send(message)
                self.producer.flush()
                
                logger.info(f"Published tombstone message for key {partition_key} to topic: {table or self.topic}")
            else:
                logger.warning("Cannot delete from Pulsar without key_field configuration")
                
        except Exception as e:
            logger.error(f"Error publishing tombstone to Pulsar topic {table or self.topic}: {e}")
            raise

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get last sync timestamp from Pulsar consumer position."""
        # For Pulsar, we rely on subscription position rather than timestamps
        # This is handled by the Pulsar consumer automatically
        return None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update last sync timestamp (handled by Pulsar subscription position)."""
        # Pulsar handles this through subscription position management
        pass

    def test_connection(self) -> bool:
        """Test Pulsar connection."""
        try:
            self.connect()
            return True
        except Exception as e:
            logger.error(f"Pulsar connection test failed: {e}")
            return False
