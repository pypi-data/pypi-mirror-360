import os
import pytest
from datetime import datetime
from evolvishub_data_handler.adapters.sqlite import SQLiteAdapter
from evolvishub_data_handler.config import DatabaseConfig, DatabaseType, WatermarkConfig


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path."""
    return str(tmp_path / "test.db")


@pytest.fixture
def test_config(test_db_path):
    """Create a test configuration."""
    return DatabaseConfig(
        type=DatabaseType.SQLITE,
        database=test_db_path,
        table="test_table",
        watermark=WatermarkConfig(
            column="updated_at",
            type="timestamp"
        )
    )


@pytest.fixture
def adapter(test_config):
    """Create a SQLite adapter instance."""
    adapter = SQLiteAdapter(test_config)
    yield adapter
    # Cleanup
    if os.path.exists(test_config.database):
        os.remove(test_config.database)


def test_connect_and_disconnect(adapter):
    """Test database connection and disconnection."""
    adapter.connect()
    assert adapter.connection is not None
    
    adapter.disconnect()
    assert adapter.connection is None


def test_create_watermark_table(adapter):
    """Test watermark table creation."""
    adapter.connect()
    
    # Verify watermark table exists
    result = adapter.execute_query("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='sync_watermark'
    """)
    assert len(result) == 1
    assert result[0]['name'] == 'sync_watermark'


def test_insert_and_query_data(adapter):
    """Test data insertion and querying."""
    adapter.connect()
    
    # Create test table
    adapter.execute_query("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            updated_at TIMESTAMP
        )
    """)
    
    # Insert test data
    test_data = [
        {"id": 1, "name": "Test 1", "updated_at": "2024-01-01 10:00:00"},
        {"id": 2, "name": "Test 2", "updated_at": "2024-01-01 11:00:00"}
    ]
    adapter.insert_data("test_table", test_data)
    
    # Query data
    result = adapter.execute_query("SELECT * FROM test_table ORDER BY id")
    assert len(result) == 2
    assert result[0]["name"] == "Test 1"
    assert result[1]["name"] == "Test 2"


def test_update_data(adapter):
    """Test data update functionality."""
    adapter.connect()
    
    # Create test table
    adapter.execute_query("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            updated_at TIMESTAMP
        )
    """)
    
    # Insert initial data
    test_data = [{"id": 1, "name": "Test 1", "updated_at": "2024-01-01 10:00:00"}]
    adapter.insert_data("test_table", test_data)
    
    # Update data
    update_data = [{"id": 1, "name": "Updated Test", "updated_at": "2024-01-01 12:00:00"}]
    adapter.update_data("test_table", update_data, ["id"])
    
    # Verify update
    result = adapter.execute_query("SELECT * FROM test_table WHERE id = 1")
    assert len(result) == 1
    assert result[0]["name"] == "Updated Test"


def test_delete_data(adapter):
    """Test data deletion functionality."""
    adapter.connect()
    
    # Create test table
    adapter.execute_query("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            updated_at TIMESTAMP
        )
    """)
    
    # Insert test data
    test_data = [
        {"id": 1, "name": "Test 1", "updated_at": "2024-01-01 10:00:00"},
        {"id": 2, "name": "Test 2", "updated_at": "2024-01-01 11:00:00"}
    ]
    adapter.insert_data("test_table", test_data)
    
    # Delete data
    adapter.delete_data("test_table", {"id": 1})
    
    # Verify deletion
    result = adapter.execute_query("SELECT * FROM test_table")
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_watermark_operations(adapter):
    """Test watermark operations."""
    adapter.connect()
    
    # Test initial watermark
    watermark = adapter.get_watermark("test_table", "updated_at")
    assert watermark is None
    
    # Update watermark
    adapter.update_watermark(
        "test_table",
        "updated_at",
        "2024-01-01 10:00:00",
        "success"
    )
    
    # Get updated watermark
    watermark = adapter.get_watermark("test_table", "updated_at")
    assert watermark is not None
    assert watermark[0] == "2024-01-01 10:00:00"
    assert watermark[1] == "success"


def test_last_sync_timestamp(adapter):
    """Test last sync timestamp operations."""
    adapter.connect()
    
    # Create test table
    adapter.execute_query("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            updated_at TIMESTAMP
        )
    """)
    
    # Test initial timestamp
    timestamp = adapter.get_last_sync_timestamp()
    assert timestamp is None
    
    # Insert test data
    test_data = [{"id": 1, "name": "Test 1", "updated_at": "2024-01-01 10:00:00"}]
    adapter.insert_data("test_table", test_data)
    
    # Get timestamp
    timestamp = adapter.get_last_sync_timestamp()
    assert timestamp == "2024-01-01 10:00:00"
    
    # Update timestamp
    adapter.update_last_sync_timestamp("2024-01-01 11:00:00")
    
    # Verify update
    timestamp = adapter.get_last_sync_timestamp()
    assert timestamp == "2024-01-01 11:00:00"


def test_error_handling(adapter):
    """Test error handling."""
    adapter.connect()
    
    # Test invalid query
    with pytest.raises(Exception):
        adapter.execute_query("INVALID SQL QUERY")
    
    # Test invalid table
    with pytest.raises(Exception):
        adapter.insert_data("non_existent_table", [{"id": 1}])
    
    # Test invalid update
    with pytest.raises(Exception):
        adapter.update_data("non_existent_table", [{"id": 1}], ["id"])
    
    # Test invalid delete
    with pytest.raises(Exception):
        adapter.delete_data("non_existent_table", {"id": 1}) 