"""Tests for Oracle database adapter."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from evolvishub_data_handler.config import DatabaseConfig, DatabaseType, WatermarkConfig
from evolvishub_data_handler.adapters.oracle import OracleAdapter


@pytest.fixture
def oracle_config():
    """Create Oracle database configuration for testing."""
    return DatabaseConfig(
        type=DatabaseType.ORACLE,
        host="localhost",
        port=1521,
        database="ORCL",
        username="test_user",
        password="test_password",
        table="test_table",
        watermark=WatermarkConfig(
            column="updated_at",
            type="timestamp",
            initial_value="2024-01-01 00:00:00"
        )
    )


@pytest.fixture
def oracle_tns_config():
    """Create Oracle TNS configuration for testing."""
    return DatabaseConfig(
        type=DatabaseType.ORACLE,
        database="PROD_DB",  # TNS name
        username="test_user",
        password="test_password",
        table="test_table"
    )


def test_oracle_adapter_import_error():
    """Test Oracle adapter when oracledb is not available."""
    with patch.dict('sys.modules', {'oracledb': None, 'cx_Oracle': None}):
        with patch('evolvishub_data_handler.adapters.oracle.oracledb', None):
            with pytest.raises(ImportError, match="oracledb package is required"):
                from evolvishub_data_handler.adapters.oracle import OracleAdapter
                config = DatabaseConfig(
                    type=DatabaseType.ORACLE,
                    host="localhost",
                    database="test",
                    username="user",
                    password="pass"
                )
                OracleAdapter(config)


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_adapter_initialization(mock_oracledb, oracle_config):
    """Test Oracle adapter initialization."""
    adapter = OracleAdapter(oracle_config)
    assert adapter.config == oracle_config
    assert adapter.connection is None


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_connect_with_host_port(mock_oracledb, oracle_config):
    """Test Oracle connection with host and port."""
    mock_connection = Mock()
    mock_oracledb.connect.return_value = mock_connection
    mock_oracledb.makedsn.return_value = "mock_dsn"
    
    adapter = OracleAdapter(oracle_config)
    adapter.connect()
    
    # Verify makedsn was called
    mock_oracledb.makedsn.assert_called_once_with(
        host="localhost",
        port=1521,
        service_name="ORCL"
    )
    
    # Verify connect was called
    mock_oracledb.connect.assert_called_once_with(
        user="test_user",
        password="test_password",
        dsn="mock_dsn"
    )
    
    assert adapter.connection == mock_connection
    assert adapter.connection.autocommit is False


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_connect_with_tns(mock_oracledb, oracle_tns_config):
    """Test Oracle connection with TNS name."""
    mock_connection = Mock()
    mock_oracledb.connect.return_value = mock_connection
    
    adapter = OracleAdapter(oracle_tns_config)
    adapter.connect()
    
    # Verify connect was called with TNS name
    mock_oracledb.connect.assert_called_once_with(
        user="test_user",
        password="test_password",
        dsn="PROD_DB"
    )
    
    assert adapter.connection == mock_connection


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_disconnect(mock_oracledb, oracle_config):
    """Test Oracle disconnection."""
    mock_connection = Mock()
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    adapter.disconnect()
    
    mock_connection.close.assert_called_once()
    assert adapter.connection is None


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_execute_query(mock_oracledb, oracle_config):
    """Test Oracle query execution."""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    # Mock cursor description and fetchall
    mock_cursor.description = [('ID', None), ('NAME', None)]
    mock_cursor.fetchall.return_value = [(1, 'John'), (2, 'Jane')]
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    result = adapter.execute_query("SELECT * FROM users", {"param": "value"})
    
    mock_cursor.execute.assert_called_once_with("SELECT * FROM users", {"param": "value"})
    assert result == [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_insert_data(mock_oracledb, oracle_config):
    """Test Oracle data insertion."""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    data = [
        {"id": 1, "name": "John", "email": "john@example.com"},
        {"id": 2, "name": "Jane", "email": "jane@example.com"}
    ]
    
    adapter.insert_data("users", data)
    
    # Verify executemany was called
    mock_cursor.executemany.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_update_data(mock_oracledb, oracle_config):
    """Test Oracle data update."""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    data = {"id": 1, "name": "John Updated", "email": "john.updated@example.com"}
    
    adapter.update_data("users", data, "id")
    
    # Verify execute was called
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_delete_data(mock_oracledb, oracle_config):
    """Test Oracle data deletion."""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    # Test with string conditions
    adapter.delete_data("users", "id = 1")
    mock_cursor.execute.assert_called_with("DELETE FROM users WHERE id = 1")
    
    # Test with dict conditions
    adapter.delete_data("users", {"id": 1})
    mock_cursor.execute.assert_called_with("DELETE FROM users WHERE id = :id", {"id": 1})
    
    assert mock_connection.commit.call_count == 2


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_get_watermark(mock_oracledb, oracle_config):
    """Test Oracle watermark retrieval."""
    mock_connection = Mock()
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    # Mock execute_query to return watermark
    adapter.execute_query = Mock(return_value=[{"updated_at": "2024-01-15 10:30:00"}])
    
    result = adapter.get_watermark("users", "updated_at")
    
    assert result == "2024-01-15 10:30:00"
    adapter.execute_query.assert_called_once()


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_update_watermark(mock_oracledb, oracle_config):
    """Test Oracle watermark update."""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    adapter.update_watermark("users", "updated_at", "2024-01-15 10:30:00", "success")
    
    # Verify MERGE statement was executed
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_get_last_sync_timestamp(mock_oracledb, oracle_config):
    """Test Oracle last sync timestamp retrieval."""
    mock_connection = Mock()
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    # Mock execute_query to return timestamp
    adapter.execute_query = Mock(return_value=[{"watermark_value": "2024-01-15 10:30:00"}])
    
    result = adapter.get_last_sync_timestamp()
    
    assert result == "2024-01-15 10:30:00"


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_create_watermark_table(mock_oracledb, oracle_config):
    """Test Oracle watermark table creation."""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [0]  # Table doesn't exist
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    adapter.create_watermark_table()
    
    # Verify table creation was attempted
    assert mock_cursor.execute.call_count == 2  # Check existence + create table
    mock_connection.commit.assert_called_once()


@patch('evolvishub_data_handler.adapters.oracle.oracledb')
def test_oracle_test_connection(mock_oracledb, oracle_config):
    """Test Oracle connection test."""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [1]
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    adapter = OracleAdapter(oracle_config)
    adapter.connection = mock_connection
    
    result = adapter.test_connection()
    
    assert result is True
    mock_cursor.execute.assert_called_once_with("SELECT 1 FROM dual")


def test_oracle_adapter_in_factory():
    """Test that Oracle adapter is registered in factory."""
    from evolvishub_data_handler.adapters.factory import AdapterFactory
    from evolvishub_data_handler.config import DatabaseType
    
    # Check that Oracle is in the adapters registry
    assert DatabaseType.ORACLE in AdapterFactory._adapters
    
    # Test creating Oracle adapter through factory
    config = DatabaseConfig(
        type=DatabaseType.ORACLE,
        host="localhost",
        database="test",
        username="user",
        password="pass"
    )
    
    with patch('evolvishub_data_handler.adapters.oracle.oracledb'):
        adapter = AdapterFactory.create(config)
        assert isinstance(adapter, OracleAdapter)
