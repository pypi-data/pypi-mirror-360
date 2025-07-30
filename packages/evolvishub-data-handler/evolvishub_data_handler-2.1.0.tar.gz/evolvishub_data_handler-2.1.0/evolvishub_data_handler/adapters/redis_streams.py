"""
Redis Streams adapter for lightweight event streaming CDC.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .base import BaseAdapter
from ..config import DatabaseConfig

logger = logging.getLogger(__name__)


class RedisStreamsAdapter(BaseAdapter):
    """Redis Streams adapter for lightweight event streaming CDC operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize Redis Streams adapter.
        
        Args:
            config: Database configuration with Redis-specific settings
        """
        super().__init__(config)
        
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package is required for Redis Streams adapter. "
                "Install with: pip install redis"
            )
        
        self.host = config.host
        self.port = config.port
        self.stream_name = config.table  # Use table field as stream name
        
        # Redis connection configuration
        self.redis_config = {
            'host': self.host,
            'port': self.port,
            'db': int(getattr(config, 'database', '0')),
            'decode_responses': True,
            'socket_timeout': getattr(config, 'socket_timeout', 30),
            'socket_connect_timeout': getattr(config, 'socket_connect_timeout', 30),
        }
        
        # Add authentication if provided
        if hasattr(config, 'password') and config.password:
            self.redis_config['password'] = config.password
        if hasattr(config, 'username') and config.username:
            self.redis_config['username'] = config.username
        
        # Consumer group configuration
        self.consumer_group = getattr(config, 'consumer_group', 'evolvishub_cdc')
        self.consumer_name = getattr(config, 'consumer_name', 'evolvishub_worker')
        
        # Stream configuration
        self.max_length = getattr(config, 'max_length', None)  # Stream trimming
        self.approximate_trimming = getattr(config, 'approximate_trimming', True)
        
        # Message configuration
        self.message_format = getattr(config, 'message_format', 'json')
        self.key_field = getattr(config, 'key_field', None)
        
        # CDC-specific settings
        self.watermark_field = None
        if hasattr(config, 'watermark') and config.watermark:
            self.watermark_field = config.watermark.column
        
        self.redis_client: Optional[redis.Redis] = None
        self.last_message_id = '0-0'  # Start from beginning
        
        logger.info(f"Initialized Redis Streams adapter for stream: {self.stream_name}")

    def _serialize_message(self, message: Dict[str, Any]) -> Dict[str, str]:
        """Serialize message for Redis Streams."""
        if self.message_format == 'json':
            # Redis Streams expects string values, so we JSON encode complex values
            serialized = {}
            for key, value in message.items():
                if isinstance(value, (dict, list)):
                    serialized[key] = json.dumps(value, default=str)
                else:
                    serialized[key] = str(value)
            return serialized
        else:
            raise ValueError(f"Unsupported message format: {self.message_format}")

    def _deserialize_message(self, message: Dict[str, str]) -> Dict[str, Any]:
        """Deserialize message from Redis Streams."""
        if not message:
            return {}
            
        try:
            if self.message_format == 'json':
                deserialized = {}
                for key, value in message.items():
                    # Try to parse as JSON, fall back to string
                    try:
                        deserialized[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        deserialized[key] = value
                return deserialized
            else:
                raise ValueError(f"Unsupported message format: {self.message_format}")
        except Exception as e:
            logger.warning(f"Failed to deserialize message: {e}")
            return {}

    def connect(self) -> None:
        """Connect to Redis server."""
        try:
            self.redis_client = redis.Redis(**self.redis_config)
            
            # Test connection
            self.redis_client.ping()
            
            # Create consumer group if it doesn't exist
            try:
                self.redis_client.xgroup_create(
                    self.stream_name, 
                    self.consumer_group, 
                    id='0', 
                    mkstream=True
                )
                logger.info(f"Created consumer group: {self.consumer_group}")
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
                # Consumer group already exists
                logger.debug(f"Consumer group already exists: {self.consumer_group}")
            
            logger.info(f"Connected to Redis server: {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from Redis server."""
        try:
            if self.redis_client:
                self.redis_client.close()
                self.redis_client = None
                
            logger.info("Disconnected from Redis server")
            
        except Exception as e:
            logger.warning(f"Error during Redis disconnect: {e}")

    def execute_query(self, query: str = None, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Read messages from Redis Stream.
        
        Args:
            query: Not used for Redis Streams (stream is specified in config)
            params: Query parameters including batch_size and last_sync
            
        Returns:
            List of messages from Redis Stream
        """
        if not self.redis_client:
            self.connect()
        
        batch_size = params.get('batch_size', 1000) if params else 1000
        last_sync = params.get('last_sync') if params else None
        
        messages = []
        
        try:
            # Read from consumer group
            stream_messages = self.redis_client.xreadgroup(
                self.consumer_group,
                self.consumer_name,
                {self.stream_name: '>'},  # Read new messages
                count=batch_size,
                block=5000  # Block for 5 seconds
            )
            
            for stream_name, stream_data in stream_messages:
                for message_id, fields in stream_data:
                    # Deserialize message data
                    message_data = self._deserialize_message(fields)
                    
                    if not message_data:
                        # Acknowledge empty message
                        self.redis_client.xack(self.stream_name, self.consumer_group, message_id)
                        continue
                    
                    # Add Redis metadata
                    message_data['_redis_message_id'] = message_id
                    message_data['_redis_stream'] = stream_name
                    
                    # Extract timestamp from message ID (format: timestamp-sequence)
                    timestamp_ms = int(message_id.split('-')[0])
                    message_data['_redis_timestamp'] = timestamp_ms
                    
                    # Apply watermark filtering if configured
                    if self.watermark_field and last_sync:
                        message_time = message_data.get(self.watermark_field)
                        if message_time and message_time <= last_sync:
                            # Acknowledge and skip old message
                            self.redis_client.xack(self.stream_name, self.consumer_group, message_id)
                            continue
                    
                    messages.append(message_data)
                    
                    # Acknowledge message
                    self.redis_client.xack(self.stream_name, self.consumer_group, message_id)
            
            logger.info(f"Read {len(messages)} messages from Redis Stream: {self.stream_name}")
            return messages
            
        except Exception as e:
            logger.error(f"Error reading from Redis Stream {self.stream_name}: {e}")
            raise

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Add messages to Redis Stream.
        
        Args:
            table: Redis stream name (overrides config if provided)
            data: List of messages to add
        """
        if not self.redis_client:
            self.connect()
        
        stream_name = table or self.stream_name
        
        try:
            for record in data:
                # Remove Redis metadata fields before publishing
                clean_record = {k: v for k, v in record.items() 
                              if not k.startswith('_redis_')}
                
                # Serialize message
                message_fields = self._serialize_message(clean_record)
                
                # Add message to stream
                message_id = self.redis_client.xadd(
                    stream_name,
                    message_fields,
                    maxlen=self.max_length,
                    approximate=self.approximate_trimming
                )
                
                logger.debug(f"Added message {message_id} to stream {stream_name}")
            
            logger.info(f"Added {len(data)} messages to Redis Stream: {stream_name}")
            
        except Exception as e:
            logger.error(f"Error adding to Redis Stream {stream_name}: {e}")
            raise

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update operation for Redis Streams (same as insert - add new messages)."""
        self.insert_data(table, data)

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete operation for Redis Streams (add tombstone messages)."""
        if not self.redis_client:
            self.connect()
        
        stream_name = table or self.stream_name
        
        try:
            # Create tombstone message
            if self.key_field and self.key_field in conditions:
                tombstone_fields = {
                    '_action': 'delete',
                    self.key_field: str(conditions[self.key_field]),
                    '_timestamp': str(int(time.time() * 1000))
                }
                
                # Add tombstone to stream
                message_id = self.redis_client.xadd(
                    stream_name,
                    tombstone_fields,
                    maxlen=self.max_length,
                    approximate=self.approximate_trimming
                )
                
                logger.info(f"Added tombstone message {message_id} for key {conditions[self.key_field]} to stream: {stream_name}")
            else:
                logger.warning("Cannot delete from Redis Stream without key_field configuration")
                
        except Exception as e:
            logger.error(f"Error adding tombstone to Redis Stream {stream_name}: {e}")
            raise

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get last sync timestamp from Redis Stream consumer group."""
        if not self.redis_client:
            return None
            
        try:
            # Get consumer group info
            info = self.redis_client.xinfo_groups(self.stream_name)
            for group in info:
                if group['name'] == self.consumer_group:
                    last_delivered_id = group['last-delivered-id']
                    # Extract timestamp from message ID
                    if last_delivered_id and last_delivered_id != '0-0':
                        timestamp_ms = int(last_delivered_id.split('-')[0])
                        return datetime.fromtimestamp(timestamp_ms / 1000).isoformat()
            return None
        except Exception as e:
            logger.warning(f"Failed to get last sync timestamp: {e}")
            return None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update last sync timestamp (handled by Redis Stream consumer group position)."""
        # Redis Streams handles this through consumer group position automatically
        pass

    def test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            self.connect()
            return True
        except Exception as e:
            logger.error(f"Redis connection test failed: {e}")
            return False

    def get_stream_info(self) -> Dict[str, Any]:
        """Get Redis Stream information."""
        if not self.redis_client:
            self.connect()
            
        try:
            info = self.redis_client.xinfo_stream(self.stream_name)
            return {
                'length': info['length'],
                'first_entry': info['first-entry'],
                'last_entry': info['last-entry'],
                'consumer_groups': len(self.redis_client.xinfo_groups(self.stream_name))
            }
        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            return {}

    def trim_stream(self, max_length: int, approximate: bool = True) -> int:
        """Trim Redis Stream to specified length."""
        if not self.redis_client:
            self.connect()
            
        try:
            return self.redis_client.xtrim(
                self.stream_name,
                maxlen=max_length,
                approximate=approximate
            )
        except Exception as e:
            logger.error(f"Failed to trim stream: {e}")
            return 0
