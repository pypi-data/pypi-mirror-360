"""Tests for the CDC handler."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from evolvishub_data_handler.cdc_handler import CDCHandler
from evolvishub_data_handler.config import (
    DatabaseConfig,
    DatabaseType,
    SyncConfig,
    WatermarkConfig,
    CDCConfig
)


@pytest.fixture
def mock_config():
    """Create a mock CDC configuration."""
    return CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            table="test_table",
            watermark=WatermarkConfig(
                column="updated_at",
                type="timestamp"
            )
        ),
        destination=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            table="test_table"
        ),
        sync=SyncConfig(
            batch_size=1000,
            interval_seconds=60,
            watermark_table="sync_watermark"
        )
    )


@pytest.fixture
def mock_source_adapter():
    """Create a mock source adapter."""
    adapter = MagicMock()
    adapter.get_last_sync_timestamp.return_value = "2024-01-01 00:00:00"
    adapter.execute_query.return_value = [
        {"id": 1, "name": "test", "updated_at": "2024-01-01 00:00:01"}
    ]
    adapter.connect = MagicMock()
    adapter.disconnect = MagicMock()
    return adapter


@pytest.fixture
def mock_dest_adapter():
    """Create a mock destination adapter."""
    adapter = MagicMock()
    adapter.connect = MagicMock()
    adapter.disconnect = MagicMock()
    return adapter


def test_cdc_handler_initialization(mock_config, mock_source_adapter, mock_dest_adapter):
    """Test CDC handler initialization."""
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_factory.side_effect = [mock_source_adapter, mock_dest_adapter]
        handler = CDCHandler(mock_config)
        assert handler.source_adapter == mock_source_adapter
        assert handler.destination_adapter == mock_dest_adapter


def test_sync_process(mock_config, mock_source_adapter, mock_dest_adapter):
    """Test the sync process."""
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_factory.side_effect = [mock_source_adapter, mock_dest_adapter]
        handler = CDCHandler(mock_config)
        
        handler.sync()
        
        # Verify that the adapters were used correctly
        mock_source_adapter.connect.assert_called_once()
        mock_dest_adapter.connect.assert_called_once()
        mock_source_adapter.get_last_sync_timestamp.assert_called_once()
        mock_source_adapter.execute_query.assert_called_once()
        mock_dest_adapter.insert_data.assert_called_once()
        mock_source_adapter.disconnect.assert_called_once()
        mock_dest_adapter.disconnect.assert_called_once()


def test_continuous_sync(mock_config, mock_source_adapter, mock_dest_adapter):
    """Test continuous sync process."""
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_factory.side_effect = [mock_source_adapter, mock_dest_adapter]
        handler = CDCHandler(mock_config)
        
        # Mock time.sleep to avoid actual waiting
        with patch("time.sleep") as mock_sleep:
            # Set up the mock's side effect to return data once and then raise KeyboardInterrupt
            mock_source_adapter.execute_query.side_effect = [
                [{"id": 1, "name": "test", "updated_at": "2024-01-01 00:00:01"}],
                KeyboardInterrupt()  # This will stop the continuous sync loop
            ]
            
            # Run continuous sync
            handler.run_continuous()
            
            # Verify that the adapters were used correctly
            assert mock_source_adapter.connect.call_count == 2  # Called twice: once for first sync, once for second sync
            assert mock_dest_adapter.connect.call_count == 2  # Called twice: once for first sync, once for second sync
            assert mock_source_adapter.get_last_sync_timestamp.call_count == 2  # Called twice: once for first sync, once for second sync
            assert mock_source_adapter.execute_query.call_count == 2  # Called twice: once for first sync, once for second sync
            mock_dest_adapter.insert_data.assert_called_once()
            mock_sleep.assert_called_once()
            assert mock_source_adapter.disconnect.call_count == 2  # Called twice: once for first sync, once for second sync
            assert mock_dest_adapter.disconnect.call_count == 2  # Called twice: once for first sync, once for second sync


def test_watermark_value_selection(mock_config):
    """Test watermark value selection logic."""
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        # Test with initial value in config
        config_with_initial = mock_config.model_copy()
        config_with_initial.source.watermark.initial_value = "2024-01-01 00:00:00"
        
        # Create mock adapters for first test
        source_adapter1 = MagicMock()
        dest_adapter1 = MagicMock()
        source_adapter1.get_last_sync_timestamp.return_value = "2024-01-01 00:00:00"
        mock_factory.side_effect = [source_adapter1, dest_adapter1]
        
        handler = CDCHandler(config_with_initial)
        assert handler.source_adapter.get_last_sync_timestamp() == "2024-01-01 00:00:00"
        
        # Test without initial value
        config_without_initial = mock_config.model_copy()
        config_without_initial.source.watermark.initial_value = None
        
        # Create mock adapters for second test
        source_adapter2 = MagicMock()
        dest_adapter2 = MagicMock()
        source_adapter2.get_last_sync_timestamp.return_value = "1970-01-01 00:00:00"
        mock_factory.side_effect = [source_adapter2, dest_adapter2]
        
        handler = CDCHandler(config_without_initial)
        assert handler.source_adapter.get_last_sync_timestamp() == "1970-01-01 00:00:00" 