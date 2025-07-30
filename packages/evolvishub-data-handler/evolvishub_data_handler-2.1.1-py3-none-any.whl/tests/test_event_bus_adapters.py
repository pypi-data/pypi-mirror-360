"""
Tests for event bus adapters (Pulsar, Redis Streams, RabbitMQ).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from evolvishub_data_handler.config import DatabaseConfig, DatabaseType


class TestPulsarAdapter:
    """Test suite for Pulsar adapter."""

    def test_pulsar_adapter_initialization_without_pulsar(self):
        """Test Pulsar adapter initialization when pulsar-client is not available."""
        config = DatabaseConfig(
            type=DatabaseType.PULSAR,
            host="localhost",
            port=6650,
            database="public/default",
            table="test_topic"
        )
        
        with patch('evolvishub_data_handler.adapters.pulsar.PULSAR_AVAILABLE', False):
            from evolvishub_data_handler.adapters.pulsar import PulsarAdapter
            with pytest.raises(ImportError, match="pulsar-client package is required"):
                PulsarAdapter(config)

    @patch('evolvishub_data_handler.adapters.pulsar.PULSAR_AVAILABLE', True)
    def test_pulsar_adapter_initialization(self):
        """Test Pulsar adapter initialization."""
        config = DatabaseConfig(
            type=DatabaseType.PULSAR,
            host="localhost",
            port=6650,
            database="public/default",
            table="test_topic"
        )
        
        from evolvishub_data_handler.adapters.pulsar import PulsarAdapter
        adapter = PulsarAdapter(config)
        
        assert adapter.service_url == "pulsar://localhost:6650"
        assert adapter.topic == "test_topic"
        assert adapter.subscription_name == "evolvishub_cdc"
        assert adapter.message_format == "json"

    @patch('evolvishub_data_handler.adapters.pulsar.PULSAR_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.pulsar.pulsar')
    def test_pulsar_connect(self, mock_pulsar):
        """Test Pulsar connection."""
        config = DatabaseConfig(
            type=DatabaseType.PULSAR,
            host="localhost",
            port=6650,
            database="public/default",
            table="test_topic"
        )
        
        # Mock Pulsar client
        mock_client = Mock()
        mock_pulsar.Client.return_value = mock_client
        
        from evolvishub_data_handler.adapters.pulsar import PulsarAdapter
        adapter = PulsarAdapter(config)
        adapter.connect()
        
        # Verify client was created
        mock_pulsar.Client.assert_called_once()
        assert adapter.client == mock_client

    @patch('evolvishub_data_handler.adapters.pulsar.PULSAR_AVAILABLE', True)
    def test_pulsar_message_serialization(self):
        """Test Pulsar message serialization."""
        config = DatabaseConfig(
            type=DatabaseType.PULSAR,
            host="localhost",
            port=6650,
            database="public/default",
            table="test_topic"
        )
        
        from evolvishub_data_handler.adapters.pulsar import PulsarAdapter
        adapter = PulsarAdapter(config)
        
        # Test serialization
        test_message = {"id": 1, "name": "test"}
        serialized = adapter._serialize_message(test_message)
        
        assert isinstance(serialized, bytes)
        
        # Test deserialization
        deserialized = adapter._deserialize_message(serialized)
        assert deserialized["id"] == 1
        assert deserialized["name"] == "test"


class TestRedisStreamsAdapter:
    """Test suite for Redis Streams adapter."""

    def test_redis_streams_adapter_initialization_without_redis(self):
        """Test Redis Streams adapter initialization when redis is not available."""
        config = DatabaseConfig(
            type=DatabaseType.REDIS_STREAMS,
            host="localhost",
            port=6379,
            database="0",
            table="test_stream"
        )
        
        with patch('evolvishub_data_handler.adapters.redis_streams.REDIS_AVAILABLE', False):
            from evolvishub_data_handler.adapters.redis_streams import RedisStreamsAdapter
            with pytest.raises(ImportError, match="redis package is required"):
                RedisStreamsAdapter(config)

    @patch('evolvishub_data_handler.adapters.redis_streams.REDIS_AVAILABLE', True)
    def test_redis_streams_adapter_initialization(self):
        """Test Redis Streams adapter initialization."""
        config = DatabaseConfig(
            type=DatabaseType.REDIS_STREAMS,
            host="localhost",
            port=6379,
            database="0",
            table="test_stream"
        )
        
        from evolvishub_data_handler.adapters.redis_streams import RedisStreamsAdapter
        adapter = RedisStreamsAdapter(config)
        
        assert adapter.host == "localhost"
        assert adapter.port == 6379
        assert adapter.stream_name == "test_stream"
        assert adapter.consumer_group == "evolvishub_cdc"
        assert adapter.message_format == "json"

    @patch('evolvishub_data_handler.adapters.redis_streams.REDIS_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.redis_streams.redis')
    def test_redis_streams_connect(self, mock_redis):
        """Test Redis Streams connection."""
        config = DatabaseConfig(
            type=DatabaseType.REDIS_STREAMS,
            host="localhost",
            port=6379,
            database="0",
            table="test_stream"
        )
        
        # Mock Redis client
        mock_client = Mock()
        mock_redis.Redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        from evolvishub_data_handler.adapters.redis_streams import RedisStreamsAdapter
        adapter = RedisStreamsAdapter(config)
        adapter.connect()
        
        # Verify client was created and tested
        mock_redis.Redis.assert_called_once()
        mock_client.ping.assert_called_once()
        assert adapter.redis_client == mock_client

    @patch('evolvishub_data_handler.adapters.redis_streams.REDIS_AVAILABLE', True)
    def test_redis_streams_message_serialization(self):
        """Test Redis Streams message serialization."""
        config = DatabaseConfig(
            type=DatabaseType.REDIS_STREAMS,
            host="localhost",
            port=6379,
            database="0",
            table="test_stream"
        )
        
        from evolvishub_data_handler.adapters.redis_streams import RedisStreamsAdapter
        adapter = RedisStreamsAdapter(config)
        
        # Test serialization
        test_message = {"id": 1, "name": "test", "data": {"nested": "value"}}
        serialized = adapter._serialize_message(test_message)
        
        assert isinstance(serialized, dict)
        assert all(isinstance(v, str) for v in serialized.values())
        
        # Test deserialization
        deserialized = adapter._deserialize_message(serialized)
        assert deserialized["id"] == 1
        assert deserialized["name"] == "test"
        assert isinstance(deserialized["data"], dict)


class TestRabbitMQAdapter:
    """Test suite for RabbitMQ adapter."""

    def test_rabbitmq_adapter_initialization_without_pika(self):
        """Test RabbitMQ adapter initialization when pika is not available."""
        config = DatabaseConfig(
            type=DatabaseType.RABBITMQ,
            host="localhost",
            port=5672,
            database="/",
            table="test_queue"
        )
        
        with patch('evolvishub_data_handler.adapters.rabbitmq.PIKA_AVAILABLE', False):
            from evolvishub_data_handler.adapters.rabbitmq import RabbitMQAdapter
            with pytest.raises(ImportError, match="pika package is required"):
                RabbitMQAdapter(config)

    @patch('evolvishub_data_handler.adapters.rabbitmq.PIKA_AVAILABLE', True)
    def test_rabbitmq_adapter_initialization(self):
        """Test RabbitMQ adapter initialization."""
        config = DatabaseConfig(
            type=DatabaseType.RABBITMQ,
            host="localhost",
            port=5672,
            database="/",
            table="test_queue"
        )
        
        from evolvishub_data_handler.adapters.rabbitmq import RabbitMQAdapter
        adapter = RabbitMQAdapter(config)
        
        assert adapter.host == "localhost"
        assert adapter.port == 5672
        assert adapter.queue_name == "test_queue"
        assert adapter.message_format == "json"
        assert adapter.queue_durable is True

    @patch('evolvishub_data_handler.adapters.rabbitmq.PIKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.rabbitmq.pika')
    def test_rabbitmq_connect(self, mock_pika):
        """Test RabbitMQ connection."""
        config = DatabaseConfig(
            type=DatabaseType.RABBITMQ,
            host="localhost",
            port=5672,
            database="/",
            table="test_queue"
        )
        
        # Mock RabbitMQ connection and channel
        mock_connection = Mock()
        mock_channel = Mock()
        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        
        from evolvishub_data_handler.adapters.rabbitmq import RabbitMQAdapter
        adapter = RabbitMQAdapter(config)
        adapter.connect()
        
        # Verify connection was created
        mock_pika.BlockingConnection.assert_called_once()
        mock_connection.channel.assert_called_once()
        assert adapter.connection == mock_connection
        assert adapter.channel == mock_channel

    @patch('evolvishub_data_handler.adapters.rabbitmq.PIKA_AVAILABLE', True)
    def test_rabbitmq_message_serialization(self):
        """Test RabbitMQ message serialization."""
        config = DatabaseConfig(
            type=DatabaseType.RABBITMQ,
            host="localhost",
            port=5672,
            database="/",
            table="test_queue"
        )
        
        from evolvishub_data_handler.adapters.rabbitmq import RabbitMQAdapter
        adapter = RabbitMQAdapter(config)
        
        # Test serialization
        test_message = {"id": 1, "name": "test"}
        serialized = adapter._serialize_message(test_message)
        
        assert isinstance(serialized, bytes)
        
        # Test deserialization
        deserialized = adapter._deserialize_message(serialized)
        assert deserialized["id"] == 1
        assert deserialized["name"] == "test"


class TestEventBusIntegration:
    """Test event bus integration scenarios."""

    def test_event_bus_configuration_validation(self):
        """Test that all event bus configurations are valid."""
        
        # Kafka configuration
        kafka_config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            database="kafka_cluster",
            table="test_topic"
        )
        assert kafka_config.type == DatabaseType.KAFKA
        
        # Pulsar configuration
        pulsar_config = DatabaseConfig(
            type=DatabaseType.PULSAR,
            host="localhost",
            port=6650,
            database="public/default",
            table="test_topic"
        )
        assert pulsar_config.type == DatabaseType.PULSAR
        
        # Redis Streams configuration
        redis_config = DatabaseConfig(
            type=DatabaseType.REDIS_STREAMS,
            host="localhost",
            port=6379,
            database="0",
            table="test_stream"
        )
        assert redis_config.type == DatabaseType.REDIS_STREAMS
        
        # RabbitMQ configuration
        rabbitmq_config = DatabaseConfig(
            type=DatabaseType.RABBITMQ,
            host="localhost",
            port=5672,
            database="/",
            table="test_queue"
        )
        assert rabbitmq_config.type == DatabaseType.RABBITMQ

    def test_adapter_factory_registration(self):
        """Test that all event bus adapters are registered in the factory."""
        from evolvishub_data_handler.adapters.factory import AdapterFactory
        
        # Force initialization
        AdapterFactory._adapters.clear()
        AdapterFactory._initialize_adapters()
        
        available_types = list(AdapterFactory._adapters.keys())
        
        # Check that event bus types are available (if dependencies are installed)
        event_bus_types = [
            DatabaseType.KAFKA,
            DatabaseType.PULSAR,
            DatabaseType.REDIS_STREAMS,
            DatabaseType.RABBITMQ
        ]
        
        for event_bus_type in event_bus_types:
            # Adapter might not be available if dependencies aren't installed
            # This is expected behavior
            if event_bus_type in available_types:
                assert AdapterFactory._adapters[event_bus_type] is not None

    def test_event_bus_adapter_creation(self):
        """Test creating event bus adapters through the factory."""
        from evolvishub_data_handler.adapters.factory import AdapterFactory
        
        # Test configurations
        configs = [
            DatabaseConfig(
                type=DatabaseType.KAFKA,
                host="localhost",
                port=9092,
                database="kafka_cluster",
                table="test_topic"
            ),
            DatabaseConfig(
                type=DatabaseType.PULSAR,
                host="localhost",
                port=6650,
                database="public/default",
                table="test_topic"
            ),
            DatabaseConfig(
                type=DatabaseType.REDIS_STREAMS,
                host="localhost",
                port=6379,
                database="0",
                table="test_stream"
            ),
            DatabaseConfig(
                type=DatabaseType.RABBITMQ,
                host="localhost",
                port=5672,
                database="/",
                table="test_queue"
            )
        ]
        
        for config in configs:
            try:
                adapter = AdapterFactory.create(config)
                assert adapter is not None
                assert adapter.config.type == config.type
            except ValueError as e:
                # Expected if dependencies are not installed
                assert "Unsupported database type" in str(e) or "Available types" in str(e)
            except ImportError:
                # Expected if dependencies are not installed
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
