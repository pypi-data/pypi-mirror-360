"""Tests for sync modes and scheduling functionality."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from evolvishub_data_handler.config import (
    CDCConfig, DatabaseConfig, SyncConfig, SyncMode, DatabaseType, WatermarkConfig
)
from evolvishub_data_handler.cdc_handler import CDCHandler


@pytest.fixture
def base_config():
    """Create a base configuration for testing."""
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
            mode=SyncMode.ONE_TIME,
            batch_size=1000
        )
    )


def test_sync_mode_one_time(base_config):
    """Test one-time sync mode."""
    base_config.sync.mode = SyncMode.ONE_TIME
    
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_adapter = MagicMock()
        mock_factory.return_value = mock_adapter
        
        handler = CDCHandler(base_config)
        handler.run()
        
        # Should call sync once
        mock_adapter.connect.assert_called()
        mock_adapter.disconnect.assert_called()


def test_sync_mode_continuous(base_config):
    """Test continuous sync mode."""
    base_config.sync.mode = SyncMode.CONTINUOUS
    base_config.sync.interval_seconds = 1
    
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_adapter = MagicMock()
        mock_factory.return_value = mock_adapter
        
        handler = CDCHandler(base_config)
        
        # Mock the stop event to stop after first iteration
        handler._stop_event.is_set = MagicMock(side_effect=[False, True])
        handler._stop_event.wait = MagicMock(return_value=True)
        
        handler.run_continuous()
        
        # Should call sync at least once
        mock_adapter.connect.assert_called()
        mock_adapter.disconnect.assert_called()


def test_sync_mode_cron(base_config):
    """Test cron sync mode."""
    base_config.sync.mode = SyncMode.CRON
    base_config.sync.cron_expression = "0 * * * *"  # Every hour
    base_config.sync.timezone = "UTC"
    
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        with patch("croniter.croniter") as mock_croniter:
            with patch("pytz.timezone") as mock_timezone:
                mock_adapter = MagicMock()
                mock_factory.return_value = mock_adapter
                
                # Mock croniter
                mock_cron_instance = MagicMock()
                mock_cron_instance.get_next.return_value = datetime.now()
                mock_croniter.return_value = mock_cron_instance
                
                # Mock timezone
                mock_tz = MagicMock()
                mock_timezone.return_value = mock_tz
                
                handler = CDCHandler(base_config)
                
                # Mock the stop event to stop immediately
                handler._stop_event.is_set = MagicMock(return_value=True)
                
                handler.run_cron()
                
                # Should initialize croniter
                mock_croniter.assert_called_once()


def test_cron_validation():
    """Test cron expression validation."""
    with pytest.raises(ValueError, match="cron_expression is required"):
        SyncConfig(
            mode=SyncMode.CRON,
            cron_expression=None
        )


def test_invalid_cron_expression():
    """Test invalid cron expression."""
    with patch("croniter.croniter") as mock_croniter:
        mock_croniter.side_effect = ValueError("Invalid cron expression")
        
        with pytest.raises(ValueError, match="Invalid cron expression"):
            SyncConfig(
                mode=SyncMode.CRON,
                cron_expression="invalid cron"
            )


def test_custom_query_config():
    """Test configuration with custom query."""
    config = CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            query="SELECT * FROM users WHERE updated_at > :last_sync",
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
            table="users"
        ),
        sync=SyncConfig(mode=SyncMode.ONE_TIME)
    )
    
    assert config.source.query is not None
    assert "SELECT * FROM users" in config.source.query


def test_simple_select_config():
    """Test configuration with simple select statement."""
    config = CDCConfig(
        source=DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            select="SELECT id, name FROM users",
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
            table="users"
        ),
        sync=SyncConfig(mode=SyncMode.ONE_TIME)
    )
    
    assert config.source.select is not None
    assert "SELECT id, name FROM users" in config.source.select


def test_query_building_with_custom_query(base_config):
    """Test query building with custom query."""
    base_config.source.query = "SELECT * FROM users WHERE updated_at > :last_sync LIMIT :batch_size"
    
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_adapter = MagicMock()
        mock_factory.return_value = mock_adapter
        
        handler = CDCHandler(base_config)
        query, params = handler._build_query("2024-01-01")
        
        assert "SELECT * FROM users" in query
        assert "%(last_sync)s" in query
        assert "%(batch_size)s" in query
        assert params["last_sync"] == "2024-01-01"
        assert params["batch_size"] == 1000


def test_query_building_with_select(base_config):
    """Test query building with simple select."""
    base_config.source.select = "SELECT id, name FROM users"
    
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_adapter = MagicMock()
        mock_factory.return_value = mock_adapter
        
        handler = CDCHandler(base_config)
        query, params = handler._build_query("2024-01-01")
        
        assert "SELECT id, name FROM users" in query
        assert "WHERE updated_at >" in query
        assert "ORDER BY updated_at" in query
        assert "LIMIT" in query


def test_query_building_default(base_config):
    """Test default query building."""
    with patch("evolvishub_data_handler.adapters.factory.AdapterFactory.create") as mock_factory:
        mock_adapter = MagicMock()
        mock_factory.return_value = mock_adapter
        
        handler = CDCHandler(base_config)
        query, params = handler._build_query("2024-01-01")
        
        assert "SELECT * FROM test_table" in query
        assert "WHERE updated_at >" in query
        assert "ORDER BY updated_at" in query
        assert "LIMIT" in query
