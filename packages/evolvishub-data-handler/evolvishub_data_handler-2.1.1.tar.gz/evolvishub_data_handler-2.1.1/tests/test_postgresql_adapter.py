"""Tests for PostgreSQL adapter."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from evolvishub_data_handler.adapters.postgresql import PostgreSQLAdapter
from evolvishub_data_handler.config import DatabaseConfig, DatabaseType, WatermarkConfig


@pytest.fixture
def test_db_config() -> DatabaseConfig:
    """Create a test database configuration."""
    return DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="test_db",
        username="test_user",
        password="test_password",
        table="test_table",  # Added required table field
        watermark=WatermarkConfig(
            column="updated_at",
            type="timestamp",
            initial_value="1970-01-01 00:00:00",
        ),
    )


@pytest.fixture
def mock_psycopg2():
    """Mock psycopg2 connection and cursor."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn, mock_cursor


@pytest.fixture
def postgres_adapter(test_db_config):
    """Create a PostgreSQL adapter instance."""
    return PostgreSQLAdapter(test_db_config)


def test_connect(test_db_config):
    """Test database connection."""
    with patch("psycopg2.connect") as mock_connect:
        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()
        mock_connect.assert_called_once_with(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_password",
        )


def test_disconnect(test_db_config):
    """Test database disconnection."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()
        adapter.disconnect()
        
        mock_conn.close.assert_called_once()


def test_execute_query(test_db_config):
    """Test query execution."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()

        query = "SELECT * FROM test_table"
        adapter.execute_query(query)

        mock_cursor.execute.assert_called_once_with(query, {})


def test_insert_data(test_db_config):
    """Test data insertion."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()

        data = {"id": 1, "name": "test"}
        adapter.insert_data("test_table", data)

        expected_query = "INSERT INTO test_table (id, name) VALUES (%s, %s)"
        mock_cursor.execute.assert_called_once_with(expected_query, [(1, "test")])


def test_update_data(test_db_config):
    """Test data update."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()

        data = {"name": "updated"}
        adapter.update_data("test_table", data, "id")

        expected_query = "UPDATE test_table SET name = %s WHERE id = %s"
        mock_cursor.execute.assert_called_once_with(expected_query, ["updated", None])


def test_delete_data(test_db_config):
    """Test data deletion."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()

        adapter.delete_data("test_table", "id = 1")

        expected_query = "DELETE FROM test_table WHERE id = 1"
        mock_cursor.execute.assert_called_once_with(expected_query, {})


def test_get_watermark(test_db_config):
    """Test watermark retrieval."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("2024-01-01 00:00:00",)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()

        watermark = adapter.get_watermark("test_table", "updated_at")
        assert watermark == "2024-01-01 00:00:00"


def test_update_watermark(test_db_config):
    """Test watermark update."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()
        
        adapter.update_watermark("sync_watermark", "updated_at", "2024-01-02 00:00:00")
        
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()


def test_get_last_sync_timestamp(test_db_config):
    """Test last sync timestamp retrieval."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("2024-01-01 00:00:00",)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()

        timestamp = adapter.get_last_sync_timestamp()
        assert timestamp == "2024-01-01 00:00:00"


def test_update_last_sync_timestamp(test_db_config):
    """Test last sync timestamp update."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        adapter = PostgreSQLAdapter(test_db_config)
        adapter.connect()
        
        adapter.update_last_sync_timestamp("2024-01-02 00:00:00")
        
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once() 