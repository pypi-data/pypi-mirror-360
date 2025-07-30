"""
Tests for data transformation plugins.
"""

import pytest
from datetime import datetime
import json

from evolvishub_data_handler.plugins.transformers import (
    FieldMapperTransformer,
    DataTypeConverterTransformer,
    FieldFilterTransformer,
    ValueReplacerTransformer,
    DateFormatterTransformer,
    JsonFlattenerTransformer,
    TransformerPlugin
)


class TestFieldMapperTransformer:
    """Test field mapping transformer."""

    def test_field_mapping(self):
        """Test basic field mapping."""
        transformer = FieldMapperTransformer({
            "mapping": {
                "old_name": "new_name",
                "user_id": "customer_id"
            }
        })
        
        data = [
            {"old_name": "John", "user_id": 123, "email": "john@example.com"},
            {"old_name": "Jane", "user_id": 456, "email": "jane@example.com"}
        ]
        
        result = transformer.transform(data)
        
        assert len(result) == 2
        assert result[0]["new_name"] == "John"
        assert result[0]["customer_id"] == 123
        assert result[0]["email"] == "john@example.com"  # Unmapped field preserved
        assert "old_name" in result[0]  # Original field preserved

    def test_empty_mapping(self):
        """Test transformer with empty mapping."""
        transformer = FieldMapperTransformer({"mapping": {}})
        
        data = [{"name": "John", "age": 30}]
        result = transformer.transform(data)
        
        assert result == data

    def test_missing_fields(self):
        """Test mapping with missing fields."""
        transformer = FieldMapperTransformer({
            "mapping": {"nonexistent": "new_field"}
        })
        
        data = [{"name": "John", "age": 30}]
        result = transformer.transform(data)
        
        assert result[0]["name"] == "John"
        assert result[0]["age"] == 30
        assert "new_field" not in result[0]


class TestDataTypeConverterTransformer:
    """Test data type conversion transformer."""

    def test_type_conversions(self):
        """Test various type conversions."""
        transformer = DataTypeConverterTransformer({
            "conversions": {
                "age": "int",
                "salary": "float",
                "name": "str",
                "active": "bool"
            }
        })
        
        data = [
            {"age": "30", "salary": "50000.50", "name": 123, "active": "true"},
            {"age": "25", "salary": "45000", "name": "Jane", "active": "false"}
        ]
        
        result = transformer.transform(data)
        
        assert isinstance(result[0]["age"], int)
        assert result[0]["age"] == 30
        assert isinstance(result[0]["salary"], float)
        assert result[0]["salary"] == 50000.50
        assert isinstance(result[0]["name"], str)
        assert result[0]["name"] == "123"
        assert isinstance(result[0]["active"], bool)

    def test_datetime_conversion(self):
        """Test datetime conversion."""
        transformer = DataTypeConverterTransformer({
            "conversions": {"created_at": "datetime"}
        })
        
        data = [{"created_at": "2024-01-01T10:00:00"}]
        result = transformer.transform(data)
        
        assert isinstance(result[0]["created_at"], datetime)

    def test_invalid_conversions(self):
        """Test handling of invalid conversions."""
        transformer = DataTypeConverterTransformer({
            "conversions": {"age": "int"}
        })
        
        data = [{"age": "invalid_number"}]
        result = transformer.transform(data)
        
        # Should preserve original value on conversion failure
        assert result[0]["age"] == "invalid_number"


class TestFieldFilterTransformer:
    """Test field filtering transformer."""

    def test_include_fields(self):
        """Test including specific fields."""
        transformer = FieldFilterTransformer({
            "include": ["name", "email"]
        })
        
        data = [{"name": "John", "email": "john@example.com", "password": "secret", "age": 30}]
        result = transformer.transform(data)
        
        assert "name" in result[0]
        assert "email" in result[0]
        assert "password" not in result[0]
        assert "age" not in result[0]

    def test_exclude_fields(self):
        """Test excluding specific fields."""
        transformer = FieldFilterTransformer({
            "exclude": ["password", "ssn"]
        })
        
        data = [{"name": "John", "email": "john@example.com", "password": "secret", "ssn": "123-45-6789"}]
        result = transformer.transform(data)
        
        assert "name" in result[0]
        assert "email" in result[0]
        assert "password" not in result[0]
        assert "ssn" not in result[0]

    def test_include_and_exclude(self):
        """Test both include and exclude filters."""
        transformer = FieldFilterTransformer({
            "include": ["name", "email", "password"],
            "exclude": ["password"]
        })
        
        data = [{"name": "John", "email": "john@example.com", "password": "secret", "age": 30}]
        result = transformer.transform(data)
        
        assert "name" in result[0]
        assert "email" in result[0]
        assert "password" not in result[0]  # Excluded takes precedence
        assert "age" not in result[0]  # Not included


class TestValueReplacerTransformer:
    """Test value replacement transformer."""

    def test_exact_replacement(self):
        """Test exact value replacement."""
        transformer = ValueReplacerTransformer({
            "rules": {
                "status": [
                    {"type": "exact", "from": "active", "to": "ACTIVE"},
                    {"type": "exact", "from": "inactive", "to": "INACTIVE"}
                ]
            }
        })
        
        data = [
            {"name": "John", "status": "active"},
            {"name": "Jane", "status": "inactive"},
            {"name": "Bob", "status": "pending"}
        ]
        
        result = transformer.transform(data)
        
        assert result[0]["status"] == "ACTIVE"
        assert result[1]["status"] == "INACTIVE"
        assert result[2]["status"] == "pending"  # Unchanged

    def test_regex_replacement(self):
        """Test regex value replacement."""
        transformer = ValueReplacerTransformer({
            "rules": {
                "phone": [
                    {"type": "regex", "from": r"\D", "to": ""}  # Remove non-digits
                ]
            }
        })
        
        data = [{"phone": "(555) 123-4567"}]
        result = transformer.transform(data)
        
        assert result[0]["phone"] == "5551234567"


class TestDateFormatterTransformer:
    """Test date formatting transformer."""

    def test_date_formatting(self):
        """Test date format conversion."""
        transformer = DateFormatterTransformer({
            "formats": {
                "created_at": {
                    "input_format": "%Y-%m-%d %H:%M:%S",
                    "output_format": "%Y-%m-%dT%H:%M:%SZ"
                }
            }
        })
        
        data = [{"created_at": "2024-01-01 10:30:00"}]
        result = transformer.transform(data)
        
        assert result[0]["created_at"] == "2024-01-01T10:30:00Z"

    def test_datetime_object_formatting(self):
        """Test formatting datetime objects."""
        transformer = DateFormatterTransformer({
            "formats": {
                "timestamp": {
                    "output_format": "%Y-%m-%d"
                }
            }
        })
        
        data = [{"timestamp": datetime(2024, 1, 1, 10, 30, 0)}]
        result = transformer.transform(data)
        
        assert result[0]["timestamp"] == "2024-01-01"

    def test_invalid_date_format(self):
        """Test handling of invalid date formats."""
        transformer = DateFormatterTransformer({
            "formats": {
                "date": {
                    "input_format": "%Y-%m-%d",
                    "output_format": "%m/%d/%Y"
                }
            }
        })
        
        data = [{"date": "invalid-date"}]
        result = transformer.transform(data)
        
        # Should preserve original value on format failure
        assert result[0]["date"] == "invalid-date"


class TestJsonFlattenerTransformer:
    """Test JSON flattening transformer."""

    def test_json_flattening(self):
        """Test flattening JSON fields."""
        transformer = JsonFlattenerTransformer({
            "fields": ["profile"],
            "separator": "_"
        })
        
        data = [
            {
                "id": 1,
                "name": "John",
                "profile": {"age": 30, "city": "New York", "preferences": {"theme": "dark"}}
            }
        ]
        
        result = transformer.transform(data)
        
        assert result[0]["id"] == 1
        assert result[0]["name"] == "John"
        assert "profile" not in result[0]
        assert result[0]["profile_age"] == 30
        assert result[0]["profile_city"] == "New York"
        assert result[0]["profile_preferences"] == {"theme": "dark"}  # Nested objects not flattened

    def test_json_string_flattening(self):
        """Test flattening JSON string fields."""
        transformer = JsonFlattenerTransformer({
            "fields": ["metadata"],
            "separator": "."
        })
        
        data = [
            {
                "id": 1,
                "metadata": '{"version": "1.0", "author": "John"}'
            }
        ]
        
        result = transformer.transform(data)
        
        assert "metadata" not in result[0]
        assert result[0]["metadata.version"] == "1.0"
        assert result[0]["metadata.author"] == "John"

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON."""
        transformer = JsonFlattenerTransformer({
            "fields": ["data"]
        })
        
        data = [{"data": "invalid-json"}]
        result = transformer.transform(data)
        
        # Should preserve original value on JSON parse failure
        assert result[0]["data"] == "invalid-json"


class TestTransformerPlugin:
    """Test transformer plugin integration."""

    def test_transformer_plugin_initialization(self):
        """Test transformer plugin initialization."""
        config = {
            "transformers": [
                {
                    "type": "field_mapper",
                    "params": {"mapping": {"old": "new"}}
                },
                {
                    "type": "data_type_converter",
                    "params": {"conversions": {"age": "int"}}
                }
            ]
        }
        
        plugin = TransformerPlugin(config)
        plugin.initialize()
        
        assert len(plugin.transformers) == 2
        assert plugin.transformers[0].get_name() == "FieldMapper"
        assert plugin.transformers[1].get_name() == "DataTypeConverter"
        
        plugin.cleanup()

    def test_transformer_pipeline(self):
        """Test complete transformation pipeline."""
        config = {
            "transformers": [
                {
                    "type": "field_mapper",
                    "params": {"mapping": {"user_id": "customer_id"}}
                },
                {
                    "type": "data_type_converter",
                    "params": {"conversions": {"customer_id": "str"}}
                },
                {
                    "type": "field_filter",
                    "params": {"exclude": ["password"]}
                }
            ]
        }
        
        plugin = TransformerPlugin(config)
        plugin.initialize()
        
        data = [{"user_id": 123, "name": "John", "password": "secret"}]
        result = plugin.transform_data(data)
        
        assert result[0]["customer_id"] == "123"  # Mapped and converted
        assert result[0]["name"] == "John"
        assert "password" not in result[0]  # Filtered out
        assert "user_id" in result[0]  # Original preserved
        
        plugin.cleanup()

    def test_unknown_transformer_type(self):
        """Test handling of unknown transformer types."""
        config = {
            "transformers": [
                {
                    "type": "unknown_transformer",
                    "params": {}
                }
            ]
        }
        
        plugin = TransformerPlugin(config)
        plugin.initialize()
        
        # Should handle unknown transformer gracefully
        assert len(plugin.transformers) == 0
        
        plugin.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
