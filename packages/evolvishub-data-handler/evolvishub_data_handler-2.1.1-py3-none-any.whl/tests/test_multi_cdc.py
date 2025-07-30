"""
Tests for multi-source multi-destination CDC functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from evolvishub_data_handler.config import (
    MultiCDCConfig, SourceDestinationMapping, DatabaseConfig, DatabaseType,
    SyncConfig, SyncMode, WatermarkConfig, WatermarkType
)
from evolvishub_data_handler.multi_cdc_handler import MultiCDCHandler, MappingResult


class TestMultiCDCConfig:
    """Test multi-CDC configuration."""

    def test_multi_cdc_config_creation(self):
        """Test creating a multi-CDC configuration."""
        source_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="source_db",
            table="source_table"
        )
        
        dest_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="dest_db",
            table="dest_table"
        )
        
        mapping = SourceDestinationMapping(
            name="test_mapping",
            source=source_db,
            destination=dest_db
        )
        
        config = MultiCDCConfig(
            name="test_config",
            mappings=[mapping]
        )
        
        assert config.name == "test_config"
        assert len(config.mappings) == 1
        assert config.mappings[0].name == "test_mapping"
        assert config.parallel_execution is True
        assert config.max_workers == 5

    def test_multi_cdc_config_validation(self):
        """Test multi-CDC configuration validation."""
        # Test empty mappings
        with pytest.raises(ValueError, match="At least one mapping must be defined"):
            MultiCDCConfig(name="test", mappings=[])
        
        # Test duplicate mapping names
        source_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="source_db",
            table="source_table"
        )
        
        dest_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="dest_db",
            table="dest_table"
        )
        
        mapping1 = SourceDestinationMapping(
            name="duplicate_name",
            source=source_db,
            destination=dest_db
        )
        
        mapping2 = SourceDestinationMapping(
            name="duplicate_name",
            source=source_db,
            destination=dest_db
        )
        
        with pytest.raises(ValueError, match="Mapping names must be unique"):
            MultiCDCConfig(name="test", mappings=[mapping1, mapping2])

    def test_source_destination_mapping_config(self):
        """Test source-destination mapping configuration."""
        source_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="source-host",
            database="source_db",
            table="source_table"
        )
        
        dest_db = DatabaseConfig(
            type=DatabaseType.MYSQL,
            host="dest-host",
            database="dest_db",
            table="dest_table"
        )
        
        watermark = WatermarkConfig(
            column="updated_at",
            type=WatermarkType.TIMESTAMP
        )
        
        mapping = SourceDestinationMapping(
            name="test_mapping",
            description="Test mapping description",
            source=source_db,
            destination=dest_db,
            watermark=watermark,
            column_mapping={"old_col": "new_col"},
            exclude_columns=["temp_col"],
            custom_query="SELECT * FROM table WHERE id > %(last_sync)s"
        )
        
        assert mapping.name == "test_mapping"
        assert mapping.description == "Test mapping description"
        assert mapping.source.type == DatabaseType.POSTGRESQL
        assert mapping.destination.type == DatabaseType.MYSQL
        assert mapping.watermark.column == "updated_at"
        assert mapping.column_mapping == {"old_col": "new_col"}
        assert mapping.exclude_columns == ["temp_col"]
        assert "SELECT * FROM table" in mapping.custom_query
        assert mapping.enabled is True


class TestMappingResult:
    """Test mapping result tracking."""

    def test_mapping_result_lifecycle(self):
        """Test mapping result start/finish lifecycle."""
        result = MappingResult("test_mapping")
        
        assert result.mapping_name == "test_mapping"
        assert result.start_time is None
        assert result.end_time is None
        assert result.success is False
        assert result.error is None
        assert result.records_processed == 0
        
        # Start execution
        result.start()
        assert result.start_time is not None
        
        # Finish successfully
        result.finish(success=True, records_processed=100)
        assert result.end_time is not None
        assert result.success is True
        assert result.records_processed == 100
        assert result.duration_seconds > 0

    def test_mapping_result_with_error(self):
        """Test mapping result with error."""
        result = MappingResult("test_mapping")
        result.start()
        
        error = Exception("Test error")
        result.finish(success=False, error=error)
        
        assert result.success is False
        assert result.error == error


class TestMultiCDCHandler:
    """Test multi-CDC handler functionality."""

    def create_test_config(self):
        """Create a test multi-CDC configuration."""
        source_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="source_db",
            table="source_table"
        )
        
        dest_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="dest_db",
            table="dest_table"
        )
        
        mapping1 = SourceDestinationMapping(
            name="mapping1",
            source=source_db.model_copy(update={"table": "table1"}),
            destination=dest_db.model_copy(update={"table": "dest_table1"})
        )
        
        mapping2 = SourceDestinationMapping(
            name="mapping2",
            source=source_db.model_copy(update={"table": "table2"}),
            destination=dest_db.model_copy(update={"table": "dest_table2"}),
            enabled=False  # Disabled mapping
        )
        
        return MultiCDCConfig(
            name="test_config",
            mappings=[mapping1, mapping2],
            parallel_execution=False,
            max_workers=2
        )

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_multi_cdc_handler_initialization(self, mock_cdc_handler):
        """Test multi-CDC handler initialization."""
        config = self.create_test_config()
        
        # Mock CDCHandler creation
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        handler = MultiCDCHandler(config)
        
        assert handler.config == config
        assert len(handler.mapping_handlers) == 1  # Only enabled mappings
        assert "mapping1" in handler.mapping_handlers
        assert "mapping2" not in handler.mapping_handlers  # Disabled

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_execute_mapping(self, mock_cdc_handler):
        """Test executing a single mapping."""
        config = self.create_test_config()
        
        # Mock CDCHandler
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        # Mock adapters
        mock_source_adapter = Mock()
        mock_dest_adapter = Mock()
        mock_handler.source_adapter = mock_source_adapter
        mock_handler.destination_adapter = mock_dest_adapter
        
        # Mock data
        test_data = [{"id": 1, "name": "test"}]
        mock_source_adapter.execute_query.return_value = test_data
        
        handler = MultiCDCHandler(config)
        result = handler.execute_mapping("mapping1")
        
        assert result.mapping_name == "mapping1"
        assert result.success is True
        assert result.records_processed >= 0

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_execute_mapping_with_custom_query(self, mock_cdc_handler):
        """Test executing mapping with custom query."""
        config = self.create_test_config()
        
        # Add custom query to mapping
        config.mappings[0].custom_query = "SELECT * FROM table WHERE id > %(last_sync)s"
        
        # Mock CDCHandler
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        # Mock adapters
        mock_source_adapter = Mock()
        mock_dest_adapter = Mock()
        mock_handler.source_adapter = mock_source_adapter
        mock_handler.destination_adapter = mock_dest_adapter
        
        # Mock data
        test_data = [{"id": 1, "name": "test"}]
        mock_source_adapter.execute_query.return_value = test_data
        
        handler = MultiCDCHandler(config)
        result = handler.execute_mapping("mapping1")
        
        # Verify custom query was used
        mock_source_adapter.execute_query.assert_called_with(config.mappings[0].custom_query)
        mock_dest_adapter.insert_data.assert_called_once()
        
        assert result.success is True

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_execute_mapping_with_column_mapping(self, mock_cdc_handler):
        """Test executing mapping with column mapping."""
        config = self.create_test_config()
        
        # Add column mapping
        config.mappings[0].column_mapping = {"old_name": "new_name"}
        config.mappings[0].custom_query = "SELECT * FROM table"
        
        # Mock CDCHandler
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        # Mock adapters
        mock_source_adapter = Mock()
        mock_dest_adapter = Mock()
        mock_handler.source_adapter = mock_source_adapter
        mock_handler.destination_adapter = mock_dest_adapter
        
        # Mock data with old column name
        test_data = [{"id": 1, "old_name": "test_value", "other_col": "other_value"}]
        mock_source_adapter.execute_query.return_value = test_data
        
        handler = MultiCDCHandler(config)
        result = handler.execute_mapping("mapping1")
        
        # Verify column mapping was applied
        call_args = mock_dest_adapter.insert_data.call_args
        inserted_data = call_args[0][1]  # Second argument is the data
        
        assert "new_name" in inserted_data[0]
        assert "old_name" not in inserted_data[0]
        assert inserted_data[0]["new_name"] == "test_value"
        assert inserted_data[0]["other_col"] == "other_value"

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_execute_mapping_with_exclude_columns(self, mock_cdc_handler):
        """Test executing mapping with excluded columns."""
        config = self.create_test_config()
        
        # Add exclude columns
        config.mappings[0].exclude_columns = ["temp_col"]
        config.mappings[0].custom_query = "SELECT * FROM table"
        
        # Mock CDCHandler
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        # Mock adapters
        mock_source_adapter = Mock()
        mock_dest_adapter = Mock()
        mock_handler.source_adapter = mock_source_adapter
        mock_handler.destination_adapter = mock_dest_adapter
        
        # Mock data with excluded column
        test_data = [{"id": 1, "name": "test", "temp_col": "exclude_me"}]
        mock_source_adapter.execute_query.return_value = test_data
        
        handler = MultiCDCHandler(config)
        result = handler.execute_mapping("mapping1")
        
        # Verify excluded column was removed
        call_args = mock_dest_adapter.insert_data.call_args
        inserted_data = call_args[0][1]
        
        assert "temp_col" not in inserted_data[0]
        assert "id" in inserted_data[0]
        assert "name" in inserted_data[0]

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_execute_all_mappings_sequential(self, mock_cdc_handler):
        """Test executing all mappings sequentially."""
        config = self.create_test_config()
        config.parallel_execution = False
        
        # Mock CDCHandler
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        # Mock adapters
        mock_source_adapter = Mock()
        mock_dest_adapter = Mock()
        mock_handler.source_adapter = mock_source_adapter
        mock_handler.destination_adapter = mock_dest_adapter
        mock_source_adapter.execute_query.return_value = []
        
        handler = MultiCDCHandler(config)
        results = handler.execute_all_mappings()
        
        assert len(results) == 1  # Only enabled mappings
        assert results[0].mapping_name == "mapping1"

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_get_summary(self, mock_cdc_handler):
        """Test getting execution summary."""
        config = self.create_test_config()
        
        # Mock CDCHandler
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        handler = MultiCDCHandler(config)
        
        # Add some mock results
        result1 = MappingResult("mapping1")
        result1.start()
        result1.finish(success=True, records_processed=100)
        
        result2 = MappingResult("mapping1")
        result2.start()
        result2.finish(success=False, error=Exception("Test error"))
        
        handler.results = [result1, result2]
        
        summary = handler.get_summary()
        
        assert summary["config_name"] == "test_config"
        assert summary["total_mappings"] == 2
        assert summary["enabled_mappings"] == 1
        assert summary["total_executions"] == 2
        assert summary["successful_executions"] == 1
        assert summary["failed_executions"] == 1
        assert summary["total_records_processed"] == 100

    @patch('evolvishub_data_handler.multi_cdc_handler.CDCHandler')
    def test_get_mapping_status(self, mock_cdc_handler):
        """Test getting mapping status."""
        config = self.create_test_config()
        
        # Mock CDCHandler
        mock_handler = Mock()
        mock_cdc_handler.return_value = mock_handler
        
        handler = MultiCDCHandler(config)
        
        # Add mock result
        result = MappingResult("mapping1")
        result.start()
        result.finish(success=True, records_processed=50)
        handler.results = [result]
        
        status_list = handler.get_mapping_status()
        
        assert len(status_list) == 2  # All mappings (enabled and disabled)
        
        # Check enabled mapping
        mapping1_status = next(s for s in status_list if s["name"] == "mapping1")
        assert mapping1_status["enabled"] is True
        assert mapping1_status["total_executions"] == 1
        assert mapping1_status["last_execution"]["success"] is True
        assert mapping1_status["last_execution"]["records_processed"] == 50
        
        # Check disabled mapping
        mapping2_status = next(s for s in status_list if s["name"] == "mapping2")
        assert mapping2_status["enabled"] is False
        assert mapping2_status["total_executions"] == 0
        assert mapping2_status["last_execution"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
