"""Tests for configuration validation."""
import pytest
from pydantic import ValidationError

from evolvishub_data_handler.config import (
    DatabaseConfig,
    DatabaseType,
    SyncConfig,
    WatermarkConfig,
    CDCConfig
)


def test_database_config_validation():
    """Test database configuration validation."""
    # Valid configuration
    config = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        username="test_user",
        password="test_pass",
        table="test_table"
    )
    assert config.type == DatabaseType.POSTGRESQL
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.database == "test_db"
    assert config.username == "test_user"
    assert config.password == "test_pass"
    assert config.table == "test_table"

    # Invalid configuration - negative port
    with pytest.raises(ValidationError):
        DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=-1,
            database="test_db",
            username="test_user",
            password="test_pass",
            table="test_table"
        )

    # Invalid configuration - missing required fields
    with pytest.raises(ValidationError):
        DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost"
        )

    # Invalid configuration - negative connection timeout
    with pytest.raises(ValidationError):
        DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            table="test_table",
            connection_timeout=-1,
        )

    # Invalid configuration - negative pool size
    with pytest.raises(ValidationError):
        DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            table="test_table",
            pool_size=-1,
        )

    # Invalid configuration - negative max overflow
    with pytest.raises(ValidationError):
        DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            table="test_table",
            max_overflow=-1,
        )


def test_watermark_config_validation():
    """Test watermark configuration validation."""
    # Valid configuration
    config = WatermarkConfig(
        column="updated_at",
        type="timestamp"
    )
    assert config.column == "updated_at"
    assert config.type == "timestamp"

    # Invalid configuration - missing required fields
    with pytest.raises(ValidationError):
        WatermarkConfig(
            column="updated_at"
        )

    # Invalid type
    with pytest.raises(ValidationError):
        WatermarkConfig(
            column="updated_at",
            type="invalid_type",  # Invalid type
        )

    # Missing required field
    with pytest.raises(ValidationError):
        WatermarkConfig(
            # Missing column
            type="timestamp",
        )


def test_sync_config_validation():
    """Test sync configuration validation."""
    # Valid configuration
    config = SyncConfig(
        batch_size=1000,
        interval_seconds=60,
        watermark_table="sync_watermark"
    )
    assert config.batch_size == 1000
    assert config.interval_seconds == 60
    assert config.watermark_table == "sync_watermark"

    # Invalid configuration - negative batch size
    with pytest.raises(ValidationError) as exc_info:
        SyncConfig(
            batch_size=-1,
            interval_seconds=60,
            watermark_table="sync_watermark"
        )
    assert "batch_size" in str(exc_info.value)

    # Invalid configuration - negative interval
    with pytest.raises(ValidationError) as exc_info:
        SyncConfig(
            batch_size=1000,
            interval_seconds=-1,
            watermark_table="sync_watermark"
        )
    assert "interval_seconds" in str(exc_info.value)

    # Invalid configuration - negative retry attempts
    with pytest.raises(ValidationError) as exc_info:
        SyncConfig(
            batch_size=1000,
            interval_seconds=60,
            watermark_table="sync_watermark",
            error_retry_attempts=-1
        )
    assert "error_retry_attempts" in str(exc_info.value)

    # Invalid configuration - negative retry delay
    with pytest.raises(ValidationError) as exc_info:
        SyncConfig(
            batch_size=1000,
            interval_seconds=60,
            watermark_table="sync_watermark",
            error_retry_delay=-1
        )
    assert "error_retry_delay" in str(exc_info.value)

    # Invalid configuration - invalid compression type
    with pytest.raises(ValidationError) as exc_info:
        SyncConfig(
            batch_size=1000,
            interval_seconds=60,
            watermark_table="sync_watermark",
            compression="invalid"
        )
    assert "compression" in str(exc_info.value)


def test_cdc_config_validation():
    """Test CDC configuration validation."""
    # Valid configuration
    config = CDCConfig(
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
    assert config.source.type == DatabaseType.POSTGRESQL
    assert config.destination.type == DatabaseType.POSTGRESQL
    assert config.sync.batch_size == 1000

    # Invalid configuration - missing required fields
    with pytest.raises(ValidationError) as exc_info:
        CDCConfig(
            source=DatabaseConfig(
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
    assert "destination" in str(exc_info.value) 