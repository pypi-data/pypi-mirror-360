"""Pytest configuration and fixtures."""
import os
import tempfile
from typing import Generator

import pytest
from loguru import logger
from datetime import datetime

from evolvishub_data_handler.config import (
    DatabaseConfig,
    DatabaseType,
    SyncConfig,
    WatermarkConfig,
)


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_config() -> dict:
    """Create a test configuration."""
    return {
        "source": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp",
                "initial_value": "1970-01-01 00:00:00",
            },
        },
        "destination": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
            "watermark": {
                "column": "updated_at",
                "type": "timestamp",
                "initial_value": "1970-01-01 00:00:00",
            },
        },
        "sync": {
            "batch_size": 1000,
            "interval_seconds": 60,
            "watermark_table": "sync_watermark",
        },
    }


@pytest.fixture
def test_db_config() -> DatabaseConfig:
    """Create a test database configuration."""
    return DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        user="test_user",
        password="test_password",
        table="test_table",
        watermark=WatermarkConfig(
            column="updated_at",
            type="timestamp",
            initial_value="1970-01-01 00:00:00",
        ),
    )


@pytest.fixture
def test_sync_config() -> SyncConfig:
    """Create a test sync configuration."""
    return SyncConfig(
        batch_size=1000,
        interval_seconds=60,
        watermark_table="sync_watermark",
    )


@pytest.fixture
def test_watermark_config() -> WatermarkConfig:
    """Create a test watermark configuration."""
    return WatermarkConfig(
        column="updated_at",
        type="timestamp",
        initial_value="1970-01-01 00:00:00",
    )


@pytest.fixture(autouse=True)
def setup_logging() -> None:
    """Set up logging for tests."""
    logger.remove()
    logger.add(
        os.path.join("logs", "test.log"),
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
    ) 