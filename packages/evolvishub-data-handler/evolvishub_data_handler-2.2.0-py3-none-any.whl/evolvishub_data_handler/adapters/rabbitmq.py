"""
RabbitMQ adapter for enterprise messaging CDC.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import time
import threading

try:
    import pika
    import pika.exceptions
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False

from .base import BaseAdapter
from ..config import DatabaseConfig

logger = logging.getLogger(__name__)


class RabbitMQAdapter(BaseAdapter):
    """RabbitMQ adapter for enterprise messaging CDC operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize RabbitMQ adapter.
        
        Args:
            config: Database configuration with RabbitMQ-specific settings
        """
        super().__init__(config)
        
        if not PIKA_AVAILABLE:
            raise ImportError(
                "pika package is required for RabbitMQ adapter. "
                "Install with: pip install pika"
            )
        
        self.host = config.host
        self.port = config.port
        self.queue_name = config.table  # Use table field as queue name
        
        # RabbitMQ connection configuration (will be created in connect())
        self.connection_config = {
            'host': self.host,
            'port': self.port,
            'virtual_host': getattr(config, 'virtual_host', '/'),
            'username': getattr(config, 'username', 'guest'),
            'password': getattr(config, 'password', 'guest'),
            'connection_attempts': getattr(config, 'connection_attempts', 3),
            'retry_delay': getattr(config, 'retry_delay', 2),
            'socket_timeout': getattr(config, 'socket_timeout', 30),
            'heartbeat': getattr(config, 'heartbeat', 600),
        }
        
        # Exchange and routing configuration
        self.exchange_name = getattr(config, 'exchange', '')
        self.exchange_type = getattr(config, 'exchange_type', 'direct')
        self.routing_key = getattr(config, 'routing_key', self.queue_name)
        
        # Queue configuration
        self.queue_durable = getattr(config, 'queue_durable', True)
        self.queue_exclusive = getattr(config, 'queue_exclusive', False)
        self.queue_auto_delete = getattr(config, 'queue_auto_delete', False)
        
        # Consumer configuration
        self.auto_ack = getattr(config, 'auto_ack', False)
        self.prefetch_count = getattr(config, 'prefetch_count', 100)
        
        # Message configuration
        self.message_format = getattr(config, 'message_format', 'json')
        self.delivery_mode = getattr(config, 'delivery_mode', 2)  # Persistent messages
        self.key_field = getattr(config, 'key_field', None)
        
        # CDC-specific settings
        self.watermark_field = None
        if hasattr(config, 'watermark') and config.watermark:
            self.watermark_field = config.watermark.column
        
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.consuming = False
        self.consumed_messages = []
        self.consume_lock = threading.Lock()
        
        logger.info(f"Initialized RabbitMQ adapter for queue: {self.queue_name}")

    def _serialize_message(self, message: Dict[str, Any]) -> bytes:
        """Serialize message for RabbitMQ producer."""
        if self.message_format == 'json':
            return json.dumps(message, default=str).encode('utf-8')
        else:
            raise ValueError(f"Unsupported message format: {self.message_format}")

    def _deserialize_message(self, message: bytes) -> Dict[str, Any]:
        """Deserialize message from RabbitMQ consumer."""
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
        """Connect to RabbitMQ server."""
        try:
            # Create connection parameters
            connection_params = pika.ConnectionParameters(
                host=self.connection_config['host'],
                port=self.connection_config['port'],
                virtual_host=self.connection_config['virtual_host'],
                credentials=pika.PlainCredentials(
                    username=self.connection_config['username'],
                    password=self.connection_config['password']
                ),
                connection_attempts=self.connection_config['connection_attempts'],
                retry_delay=self.connection_config['retry_delay'],
                socket_timeout=self.connection_config['socket_timeout'],
                heartbeat=self.connection_config['heartbeat'],
            )

            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            # Set QoS for consumer
            self.channel.basic_qos(prefetch_count=self.prefetch_count)
            
            # Declare exchange if specified
            if self.exchange_name:
                self.channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type=self.exchange_type,
                    durable=True
                )
            
            # Declare queue
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=self.queue_durable,
                exclusive=self.queue_exclusive,
                auto_delete=self.queue_auto_delete
            )
            
            # Bind queue to exchange if specified
            if self.exchange_name:
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=self.queue_name,
                    routing_key=self.routing_key
                )
            
            logger.info(f"Connected to RabbitMQ server: {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from RabbitMQ server."""
        try:
            self.consuming = False
            
            if self.channel and not self.channel.is_closed:
                self.channel.close()
                self.channel = None
                
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                self.connection = None
                
            logger.info("Disconnected from RabbitMQ server")
            
        except Exception as e:
            logger.warning(f"Error during RabbitMQ disconnect: {e}")

    def _message_callback(self, channel, method, properties, body):
        """Callback function for consuming messages."""
        try:
            # Deserialize message
            message_data = self._deserialize_message(body)
            
            if message_data:
                # Add RabbitMQ metadata
                message_data['_rabbitmq_delivery_tag'] = method.delivery_tag
                message_data['_rabbitmq_exchange'] = method.exchange
                message_data['_rabbitmq_routing_key'] = method.routing_key
                message_data['_rabbitmq_timestamp'] = getattr(properties, 'timestamp', None)
                message_data['_rabbitmq_message_id'] = getattr(properties, 'message_id', None)
                
                with self.consume_lock:
                    self.consumed_messages.append((message_data, method.delivery_tag))
            
            # Acknowledge message if auto_ack is disabled
            if not self.auto_ack:
                channel.basic_ack(delivery_tag=method.delivery_tag)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            if not self.auto_ack:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def execute_query(self, query: str = None, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Read messages from RabbitMQ queue.
        
        Args:
            query: Not used for RabbitMQ (queue is specified in config)
            params: Query parameters including batch_size and last_sync
            
        Returns:
            List of messages from RabbitMQ queue
        """
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        batch_size = params.get('batch_size', 1000) if params else 1000
        last_sync = params.get('last_sync') if params else None
        
        messages = []
        
        try:
            # Clear previous messages
            with self.consume_lock:
                self.consumed_messages.clear()
            
            # Start consuming
            self.consuming = True
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._message_callback,
                auto_ack=self.auto_ack
            )
            
            # Consume messages with timeout
            start_time = time.time()
            timeout = 10  # 10 seconds timeout
            
            while (len(self.consumed_messages) < batch_size and 
                   time.time() - start_time < timeout and 
                   self.consuming):
                
                self.connection.process_data_events(time_limit=1)
            
            # Stop consuming
            self.channel.cancel()
            self.consuming = False
            
            # Process consumed messages
            with self.consume_lock:
                for message_data, delivery_tag in self.consumed_messages:
                    # Apply watermark filtering if configured
                    if self.watermark_field and last_sync:
                        message_time = message_data.get(self.watermark_field)
                        if message_time and message_time <= last_sync:
                            continue
                    
                    messages.append(message_data)
                
                self.consumed_messages.clear()
            
            logger.info(f"Read {len(messages)} messages from RabbitMQ queue: {self.queue_name}")
            return messages
            
        except Exception as e:
            logger.error(f"Error reading from RabbitMQ queue {self.queue_name}: {e}")
            raise

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Publish messages to RabbitMQ queue.
        
        Args:
            table: RabbitMQ queue name (overrides config if provided)
            data: List of messages to publish
        """
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        queue_name = table or self.queue_name
        
        try:
            for record in data:
                # Remove RabbitMQ metadata fields before publishing
                clean_record = {k: v for k, v in record.items() 
                              if not k.startswith('_rabbitmq_')}
                
                # Serialize message
                message_body = self._serialize_message(clean_record)
                
                # Create message properties
                properties = pika.BasicProperties(
                    delivery_mode=self.delivery_mode,
                    timestamp=int(time.time()),
                    content_type='application/json',
                )
                
                # Add message ID if key_field is configured
                if self.key_field and self.key_field in record:
                    properties.message_id = str(record[self.key_field])
                
                # Add correlation ID for tracking
                properties.correlation_id = f"evolvishub_{int(time.time() * 1000)}"
                
                # Publish message
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=self.routing_key,
                    body=message_body,
                    properties=properties
                )
            
            logger.info(f"Published {len(data)} messages to RabbitMQ queue: {queue_name}")
            
        except Exception as e:
            logger.error(f"Error publishing to RabbitMQ queue {queue_name}: {e}")
            raise

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update operation for RabbitMQ (same as insert - publish new messages)."""
        self.insert_data(table, data)

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete operation for RabbitMQ (publish tombstone messages)."""
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        queue_name = table or self.queue_name
        
        try:
            # Create tombstone message
            if self.key_field and self.key_field in conditions:
                tombstone_message = {
                    '_action': 'delete',
                    self.key_field: conditions[self.key_field],
                    '_timestamp': datetime.now().isoformat()
                }
                
                message_body = self._serialize_message(tombstone_message)
                
                properties = pika.BasicProperties(
                    delivery_mode=self.delivery_mode,
                    timestamp=int(time.time()),
                    content_type='application/json',
                    message_id=str(conditions[self.key_field]),
                    headers={'action': 'delete'}
                )
                
                # Publish tombstone
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=self.routing_key,
                    body=message_body,
                    properties=properties
                )
                
                logger.info(f"Published tombstone message for key {conditions[self.key_field]} to queue: {queue_name}")
            else:
                logger.warning("Cannot delete from RabbitMQ without key_field configuration")
                
        except Exception as e:
            logger.error(f"Error publishing tombstone to RabbitMQ queue {queue_name}: {e}")
            raise

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get last sync timestamp (not directly supported by RabbitMQ)."""
        # RabbitMQ doesn't have built-in timestamp tracking like Kafka
        # This would need to be implemented using external storage
        return None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update last sync timestamp (not directly supported by RabbitMQ)."""
        # RabbitMQ doesn't have built-in timestamp tracking
        # This would need to be implemented using external storage
        pass

    def test_connection(self) -> bool:
        """Test RabbitMQ connection."""
        try:
            self.connect()
            return True
        except Exception as e:
            logger.error(f"RabbitMQ connection test failed: {e}")
            return False

    def get_queue_info(self) -> Dict[str, Any]:
        """Get RabbitMQ queue information."""
        if not self.connection or self.connection.is_closed:
            self.connect()
            
        try:
            method = self.channel.queue_declare(
                queue=self.queue_name,
                passive=True  # Don't create, just get info
            )
            
            return {
                'queue': method.method.queue,
                'message_count': method.method.message_count,
                'consumer_count': method.method.consumer_count
            }
        except Exception as e:
            logger.error(f"Failed to get queue info: {e}")
            return {}

    def purge_queue(self) -> int:
        """Purge all messages from the queue."""
        if not self.connection or self.connection.is_closed:
            self.connect()
            
        try:
            method = self.channel.queue_purge(queue=self.queue_name)
            purged_count = method.method.message_count
            logger.info(f"Purged {purged_count} messages from queue: {self.queue_name}")
            return purged_count
        except Exception as e:
            logger.error(f"Failed to purge queue: {e}")
            return 0
