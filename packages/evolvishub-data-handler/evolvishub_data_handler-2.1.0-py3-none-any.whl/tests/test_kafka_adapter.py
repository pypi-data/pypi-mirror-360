"""
Tests for Kafka adapter.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from evolvishub_data_handler.config import DatabaseConfig, DatabaseType
from evolvishub_data_handler.adapters.kafka import KafkaAdapter


class TestKafkaAdapter:
    """Test suite for Kafka adapter."""

    def test_kafka_adapter_initialization_without_kafka(self):
        """Test Kafka adapter initialization when kafka-python is not available."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            database="kafka_cluster",  # Required field
            table="test_topic"
        )
        
        with patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', False):
            with pytest.raises(ImportError, match="kafka-python package is required"):
                KafkaAdapter(config)

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    def test_kafka_adapter_initialization(self):
        """Test Kafka adapter initialization."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            database="kafka_cluster",
            table="test_topic"
        )
        
        adapter = KafkaAdapter(config)
        
        assert adapter.bootstrap_servers == "localhost:9092"
        assert adapter.topic == "test_topic"
        assert adapter.message_format == "json"
        assert adapter.consumer is None
        assert adapter.producer is None

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    def test_kafka_adapter_with_security_config(self):
        """Test Kafka adapter with security configuration."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            database="kafka_cluster",
            table="secure_topic"
        )
        
        # Add security attributes
        config.security_protocol = "SASL_SSL"
        config.sasl_mechanism = "PLAIN"
        config.sasl_username = "user"
        config.sasl_password = "password"
        
        adapter = KafkaAdapter(config)
        
        assert adapter.consumer_config['security_protocol'] == "SASL_SSL"
        assert adapter.consumer_config['sasl_mechanism'] == "PLAIN"
        assert adapter.producer_config['security_protocol'] == "SASL_SSL"

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.kafka.KafkaConsumer')
    def test_kafka_connect(self, mock_consumer_class):
        """Test Kafka connection."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        # Mock successful connection
        mock_consumer = Mock()
        mock_consumer_class.return_value = mock_consumer
        
        adapter = KafkaAdapter(config)
        adapter.connect()
        
        # Verify consumer was created and closed (for connection test)
        mock_consumer_class.assert_called_once()
        mock_consumer.close.assert_called_once()

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.kafka.KafkaConsumer')
    def test_kafka_execute_query(self, mock_consumer_class):
        """Test reading messages from Kafka topic."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        # Mock Kafka consumer
        mock_consumer = Mock()
        mock_consumer_class.return_value = mock_consumer
        
        # Mock message records
        mock_record1 = Mock()
        mock_record1.value = {"id": 1, "name": "test1", "timestamp": "2024-01-01T10:00:00Z"}
        mock_record1.offset = 100
        mock_record1.partition = 0
        mock_record1.timestamp = 1704110400000
        mock_record1.key = "key1"
        
        mock_record2 = Mock()
        mock_record2.value = {"id": 2, "name": "test2", "timestamp": "2024-01-01T11:00:00Z"}
        mock_record2.offset = 101
        mock_record2.partition = 0
        mock_record2.timestamp = 1704114000000
        mock_record2.key = "key2"
        
        # Mock poll response
        mock_topic_partition = Mock()
        mock_consumer.poll.return_value = {
            mock_topic_partition: [mock_record1, mock_record2]
        }
        
        adapter = KafkaAdapter(config)
        
        # Execute query (read messages)
        result = adapter.execute_query(params={"batch_size": 10})
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["_kafka_offset"] == 100
        assert result[0]["_kafka_partition"] == 0
        assert result[0]["_kafka_key"] == "key1"
        
        # Verify consumer was configured and used
        mock_consumer_class.assert_called_once_with("test_topic", **adapter.consumer_config)
        mock_consumer.poll.assert_called_once()
        mock_consumer.commit.assert_called_once()

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.kafka.KafkaProducer')
    def test_kafka_insert_data(self, mock_producer_class):
        """Test publishing messages to Kafka topic."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        # Mock Kafka producer
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer
        
        # Mock send future
        mock_future = Mock()
        mock_producer.send.return_value = mock_future
        
        adapter = KafkaAdapter(config)
        
        # Test data
        test_data = [
            {"id": 1, "name": "test1", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": 2, "name": "test2", "timestamp": "2024-01-01T11:00:00Z"}
        ]
        
        # Insert data (publish messages)
        adapter.insert_data("test_topic", test_data)
        
        # Verify producer was configured and used
        mock_producer_class.assert_called_once_with(**adapter.producer_config)
        assert mock_producer.send.call_count == 2
        mock_producer.flush.assert_called_once()

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.kafka.KafkaProducer')
    def test_kafka_insert_data_with_key(self, mock_producer_class):
        """Test publishing messages with keys to Kafka topic."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        config.key_field = "id"
        
        # Mock Kafka producer
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer
        
        # Mock send future
        mock_future = Mock()
        mock_producer.send.return_value = mock_future
        
        adapter = KafkaAdapter(config)
        
        # Test data
        test_data = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"}
        ]
        
        # Insert data with keys
        adapter.insert_data("test_topic", test_data)
        
        # Verify messages were sent with keys
        calls = mock_producer.send.call_args_list
        assert len(calls) == 2
        
        # Check first message
        args, kwargs = calls[0]
        assert args[0] == "test_topic"  # topic
        assert kwargs["key"] == "1"  # key from id field
        assert kwargs["value"]["id"] == 1  # message value

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.kafka.KafkaProducer')
    def test_kafka_delete_data(self, mock_producer_class):
        """Test publishing tombstone messages for deletion."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        config.key_field = "id"
        
        # Mock Kafka producer
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer
        
        # Mock send future
        mock_future = Mock()
        mock_producer.send.return_value = mock_future
        
        adapter = KafkaAdapter(config)
        
        # Delete data (send tombstone)
        adapter.delete_data("test_topic", {"id": "123"})
        
        # Verify tombstone message was sent
        mock_producer.send.assert_called_once_with("test_topic", value=None, key="123")
        mock_producer.flush.assert_called_once()

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    def test_kafka_message_serialization(self):
        """Test message serialization and deserialization."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        adapter = KafkaAdapter(config)
        
        # Test serialization
        test_message = {"id": 1, "name": "test", "timestamp": datetime.now()}
        serialized = adapter._serialize_message(test_message)
        
        assert isinstance(serialized, bytes)
        
        # Test deserialization
        deserialized = adapter._deserialize_message(serialized)
        
        assert deserialized["id"] == 1
        assert deserialized["name"] == "test"
        assert "timestamp" in deserialized

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    def test_kafka_message_deserialization_error(self):
        """Test handling of message deserialization errors."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        adapter = KafkaAdapter(config)
        
        # Test with invalid JSON
        invalid_message = b"invalid json content"
        result = adapter._deserialize_message(invalid_message)
        
        assert result == {}  # Should return empty dict on error

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    def test_kafka_disconnect(self):
        """Test Kafka disconnection."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        adapter = KafkaAdapter(config)
        
        # Mock consumer and producer
        adapter.consumer = Mock()
        adapter.producer = Mock()
        
        # Disconnect
        adapter.disconnect()
        
        # Verify cleanup
        adapter.consumer.close.assert_called_once()
        adapter.producer.flush.assert_called_once()
        adapter.producer.close.assert_called_once()
        
        assert adapter.consumer is None
        assert adapter.producer is None

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.kafka.KafkaConsumer')
    def test_kafka_test_connection(self, mock_consumer_class):
        """Test Kafka connection testing."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        # Mock successful connection
        mock_consumer = Mock()
        mock_consumer_class.return_value = mock_consumer
        
        adapter = KafkaAdapter(config)
        
        # Test connection
        result = adapter.test_connection()
        
        assert result is True
        mock_consumer.close.assert_called_once()

    @patch('evolvishub_data_handler.adapters.kafka.KAFKA_AVAILABLE', True)
    @patch('evolvishub_data_handler.adapters.kafka.KafkaConsumer')
    def test_kafka_test_connection_failure(self, mock_consumer_class):
        """Test Kafka connection testing with failure."""
        config = DatabaseConfig(
            type=DatabaseType.KAFKA,
            host="localhost",
            port=9092,
            table="test_topic"
        )
        
        # Mock connection failure
        mock_consumer_class.side_effect = Exception("Connection failed")
        
        adapter = KafkaAdapter(config)
        
        # Test connection
        result = adapter.test_connection()
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
