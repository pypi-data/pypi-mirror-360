"""Tests for watermark storage functionality."""
import pytest
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path

from evolvishub_data_handler.config import (
    WatermarkStorageConfig, WatermarkStorageType
)
from evolvishub_data_handler.watermark_manager import (
    SQLiteWatermarkManager, FileWatermarkManager, create_watermark_manager
)


@pytest.fixture
def temp_sqlite_path():
    """Create a temporary SQLite file path."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def temp_json_path():
    """Create a temporary JSON file path."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_watermark_storage_config_validation():
    """Test watermark storage configuration validation."""
    # Valid SQLite config
    config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path="/tmp/test.db"
    )
    assert config.type == WatermarkStorageType.SQLITE
    assert config.sqlite_path == "/tmp/test.db"
    
    # Valid file config
    config = WatermarkStorageConfig(
        type=WatermarkStorageType.FILE,
        file_path="/tmp/test.json"
    )
    assert config.type == WatermarkStorageType.FILE
    assert config.file_path == "/tmp/test.json"
    
    # Invalid SQLite config (missing path)
    with pytest.raises(ValueError, match="sqlite_path is required"):
        WatermarkStorageConfig(
            type=WatermarkStorageType.SQLITE,
            sqlite_path=None
        )
    
    # Invalid file config (missing path)
    with pytest.raises(ValueError, match="file_path is required"):
        WatermarkStorageConfig(
            type=WatermarkStorageType.FILE,
            file_path=None
        )


def test_sqlite_watermark_manager(temp_sqlite_path):
    """Test SQLite watermark manager functionality."""
    config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path=temp_sqlite_path,
        table_name="test_watermark"
    )
    
    manager = SQLiteWatermarkManager(config)
    
    try:
        # Test initial state - no watermark
        result = manager.get_watermark("users", "updated_at")
        assert result is None
        
        # Test setting watermark
        manager.update_watermark("users", "updated_at", "2024-01-01 10:00:00", "success")
        
        # Test getting watermark
        result = manager.get_watermark("users", "updated_at")
        assert result is not None
        watermark_value, status = result
        assert watermark_value == "2024-01-01 10:00:00"
        assert status == "success"
        
        # Test updating watermark
        manager.update_watermark("users", "updated_at", "2024-01-01 11:00:00", "success")
        
        result = manager.get_watermark("users", "updated_at")
        watermark_value, status = result
        assert watermark_value == "2024-01-01 11:00:00"
        assert status == "success"
        
        # Test error status
        manager.update_watermark("users", "updated_at", "2024-01-01 11:00:00", "error", "Connection failed")
        
        result = manager.get_watermark("users", "updated_at")
        watermark_value, status = result
        assert watermark_value == "2024-01-01 11:00:00"
        assert status == "error"
        
        # Test multiple tables
        manager.update_watermark("orders", "created_at", "2024-01-01 12:00:00", "success")
        
        result = manager.get_watermark("orders", "created_at")
        watermark_value, status = result
        assert watermark_value == "2024-01-01 12:00:00"
        assert status == "success"
        
        # Test get all watermarks
        all_watermarks = manager.get_all_watermarks()
        assert len(all_watermarks) == 2
        assert "users.updated_at" in all_watermarks
        assert "orders.created_at" in all_watermarks
        
    finally:
        manager.close()


def test_file_watermark_manager(temp_json_path):
    """Test file watermark manager functionality."""
    config = WatermarkStorageConfig(
        type=WatermarkStorageType.FILE,
        file_path=temp_json_path
    )
    
    manager = FileWatermarkManager(config)
    
    try:
        # Test initial state - no watermark
        result = manager.get_watermark("users", "updated_at")
        assert result is None
        
        # Test setting watermark
        manager.update_watermark("users", "updated_at", "2024-01-01 10:00:00", "success")
        
        # Test getting watermark
        result = manager.get_watermark("users", "updated_at")
        assert result is not None
        watermark_value, status = result
        assert watermark_value == "2024-01-01 10:00:00"
        assert status == "success"
        
        # Test file persistence
        manager.close()
        
        # Create new manager instance
        manager = FileWatermarkManager(config)
        result = manager.get_watermark("users", "updated_at")
        assert result is not None
        watermark_value, status = result
        assert watermark_value == "2024-01-01 10:00:00"
        assert status == "success"
        
    finally:
        manager.close()


def test_watermark_manager_factory(temp_sqlite_path, temp_json_path):
    """Test watermark manager factory function."""
    # Test SQLite manager creation
    sqlite_config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path=temp_sqlite_path
    )
    
    manager = create_watermark_manager(sqlite_config)
    assert isinstance(manager, SQLiteWatermarkManager)
    manager.close()
    
    # Test file manager creation
    file_config = WatermarkStorageConfig(
        type=WatermarkStorageType.FILE,
        file_path=temp_json_path
    )
    
    manager = create_watermark_manager(file_config)
    assert isinstance(manager, FileWatermarkManager)
    manager.close()
    
    # Test unsupported type
    with pytest.raises(ValueError, match="Unsupported watermark storage type"):
        invalid_config = WatermarkStorageConfig(
            type=WatermarkStorageType.DATABASE  # Not supported by factory
        )
        create_watermark_manager(invalid_config)


def test_sqlite_persistence(temp_sqlite_path):
    """Test SQLite watermark persistence across manager instances."""
    config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path=temp_sqlite_path
    )
    
    # First manager instance
    manager1 = SQLiteWatermarkManager(config)
    manager1.update_watermark("products", "updated_at", "2024-01-01 15:00:00", "success")
    manager1.close()
    
    # Second manager instance (simulating restart)
    manager2 = SQLiteWatermarkManager(config)
    result = manager2.get_watermark("products", "updated_at")
    assert result is not None
    watermark_value, status = result
    assert watermark_value == "2024-01-01 15:00:00"
    assert status == "success"
    manager2.close()


def test_file_persistence(temp_json_path):
    """Test file watermark persistence across manager instances."""
    config = WatermarkStorageConfig(
        type=WatermarkStorageType.FILE,
        file_path=temp_json_path
    )
    
    # First manager instance
    manager1 = FileWatermarkManager(config)
    manager1.update_watermark("products", "updated_at", "2024-01-01 15:00:00", "success")
    manager1.close()
    
    # Verify file was created and contains data
    assert os.path.exists(temp_json_path)
    with open(temp_json_path, 'r') as f:
        data = json.load(f)
    assert "products.updated_at" in data
    
    # Second manager instance (simulating restart)
    manager2 = FileWatermarkManager(config)
    result = manager2.get_watermark("products", "updated_at")
    assert result is not None
    watermark_value, status = result
    assert watermark_value == "2024-01-01 15:00:00"
    assert status == "success"
    manager2.close()


def test_directory_creation(temp_sqlite_path):
    """Test that directories are created automatically."""
    # Use a path in a non-existent directory
    nested_path = os.path.join(os.path.dirname(temp_sqlite_path), "nested", "dir", "test.db")
    
    config = WatermarkStorageConfig(
        type=WatermarkStorageType.SQLITE,
        sqlite_path=nested_path
    )
    
    manager = SQLiteWatermarkManager(config)
    
    try:
        # Directory should be created automatically
        assert os.path.exists(os.path.dirname(nested_path))
        
        # Manager should work normally
        manager.update_watermark("test", "id", "123", "success")
        result = manager.get_watermark("test", "id")
        assert result is not None
        
    finally:
        manager.close()
        # Cleanup nested directory
        import shutil
        nested_dir = os.path.join(os.path.dirname(temp_sqlite_path), "nested")
        if os.path.exists(nested_dir):
            shutil.rmtree(nested_dir)
