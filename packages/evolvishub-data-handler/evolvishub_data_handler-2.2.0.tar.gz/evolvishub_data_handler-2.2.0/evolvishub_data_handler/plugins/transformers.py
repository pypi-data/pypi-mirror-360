"""
Data transformation plugins for processing data between source and destination.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
import json
import re
from datetime import datetime
from .base import BasePlugin, PluginMetadata, PluginType
from loguru import logger


class DataTransformer(ABC):
    """Base class for data transformers."""
    
    @abstractmethod
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform data records."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get transformer name."""
        pass


class TransformerPlugin(BasePlugin):
    """Plugin for data transformation pipeline."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.transformers: List[DataTransformer] = []
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return transformer plugin metadata."""
        return PluginMetadata(
            name="TransformerPlugin",
            version="1.0.0",
            description="Data transformation pipeline plugin",
            author="Evolvishub",
            plugin_type=PluginType.TRANSFORMER
        )
    
    def initialize(self) -> None:
        """Initialize transformer pipeline."""
        transformers_config = self.config.get('transformers', [])
        
        for transformer_config in transformers_config:
            transformer_type = transformer_config.get('type')
            transformer_params = transformer_config.get('params', {})
            
            transformer = self._create_transformer(transformer_type, transformer_params)
            if transformer:
                self.transformers.append(transformer)
                logger.info(f"Added transformer: {transformer.get_name()}")
    
    def cleanup(self) -> None:
        """Cleanup transformer resources."""
        self.transformers.clear()
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all transformers to data."""
        result = data
        
        for transformer in self.transformers:
            try:
                result = transformer.transform(result)
                logger.debug(f"Applied transformer: {transformer.get_name()}")
            except Exception as e:
                logger.error(f"Transformer {transformer.get_name()} failed: {e}")
                raise
        
        return result
    
    def add_transformer(self, transformer: DataTransformer) -> None:
        """Add a transformer to the pipeline."""
        self.transformers.append(transformer)
    
    def _create_transformer(self, transformer_type: str, params: Dict[str, Any]) -> Optional[DataTransformer]:
        """Create transformer instance based on type."""
        transformer_map = {
            'field_mapper': FieldMapperTransformer,
            'data_type_converter': DataTypeConverterTransformer,
            'field_filter': FieldFilterTransformer,
            'value_replacer': ValueReplacerTransformer,
            'date_formatter': DateFormatterTransformer,
            'json_flattener': JsonFlattenerTransformer,
            'custom_function': CustomFunctionTransformer,
        }
        
        transformer_class = transformer_map.get(transformer_type)
        if transformer_class:
            return transformer_class(params)
        
        logger.warning(f"Unknown transformer type: {transformer_type}")
        return None


class FieldMapperTransformer(DataTransformer):
    """Transform field names according to mapping."""
    
    def __init__(self, params: Dict[str, Any]):
        self.field_mapping = params.get('mapping', {})
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map field names."""
        result = []
        
        for record in data:
            mapped_record = {}
            for old_field, new_field in self.field_mapping.items():
                if old_field in record:
                    mapped_record[new_field] = record[old_field]
            
            # Keep unmapped fields
            for field, value in record.items():
                if field not in self.field_mapping:
                    mapped_record[field] = value
            
            result.append(mapped_record)
        
        return result
    
    def get_name(self) -> str:
        return "FieldMapper"


class DataTypeConverterTransformer(DataTransformer):
    """Convert data types for specified fields."""
    
    def __init__(self, params: Dict[str, Any]):
        self.type_conversions = params.get('conversions', {})
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert data types."""
        result = []
        
        for record in data:
            converted_record = record.copy()
            
            for field, target_type in self.type_conversions.items():
                if field in record:
                    try:
                        if target_type == 'int':
                            converted_record[field] = int(record[field])
                        elif target_type == 'float':
                            converted_record[field] = float(record[field])
                        elif target_type == 'str':
                            converted_record[field] = str(record[field])
                        elif target_type == 'bool':
                            converted_record[field] = bool(record[field])
                        elif target_type == 'datetime':
                            if isinstance(record[field], str):
                                converted_record[field] = datetime.fromisoformat(record[field])
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to convert {field} to {target_type}: {e}")
            
            result.append(converted_record)
        
        return result
    
    def get_name(self) -> str:
        return "DataTypeConverter"


class FieldFilterTransformer(DataTransformer):
    """Filter fields to include/exclude."""
    
    def __init__(self, params: Dict[str, Any]):
        self.include_fields = params.get('include', [])
        self.exclude_fields = params.get('exclude', [])
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter fields."""
        result = []
        
        for record in data:
            filtered_record = {}
            
            for field, value in record.items():
                # Include logic
                if self.include_fields and field not in self.include_fields:
                    continue
                
                # Exclude logic
                if self.exclude_fields and field in self.exclude_fields:
                    continue
                
                filtered_record[field] = value
            
            result.append(filtered_record)
        
        return result
    
    def get_name(self) -> str:
        return "FieldFilter"


class ValueReplacerTransformer(DataTransformer):
    """Replace values based on rules."""
    
    def __init__(self, params: Dict[str, Any]):
        self.replacement_rules = params.get('rules', {})
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Replace values."""
        result = []
        
        for record in data:
            replaced_record = record.copy()
            
            for field, rules in self.replacement_rules.items():
                if field in record:
                    value = record[field]
                    
                    for rule in rules:
                        if rule['type'] == 'exact':
                            if value == rule['from']:
                                replaced_record[field] = rule['to']
                        elif rule['type'] == 'regex':
                            pattern = rule['from']
                            replacement = rule['to']
                            if isinstance(value, str):
                                replaced_record[field] = re.sub(pattern, replacement, value)
            
            result.append(replaced_record)
        
        return result
    
    def get_name(self) -> str:
        return "ValueReplacer"


class DateFormatterTransformer(DataTransformer):
    """Format date fields."""
    
    def __init__(self, params: Dict[str, Any]):
        self.date_formats = params.get('formats', {})
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format dates."""
        result = []
        
        for record in data:
            formatted_record = record.copy()
            
            for field, format_config in self.date_formats.items():
                if field in record:
                    try:
                        value = record[field]
                        input_format = format_config.get('input_format')
                        output_format = format_config.get('output_format')
                        
                        if isinstance(value, str) and input_format:
                            dt = datetime.strptime(value, input_format)
                        elif isinstance(value, datetime):
                            dt = value
                        else:
                            continue
                        
                        if output_format:
                            formatted_record[field] = dt.strftime(output_format)
                        else:
                            formatted_record[field] = dt.isoformat()
                            
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to format date {field}: {e}")
            
            result.append(formatted_record)
        
        return result
    
    def get_name(self) -> str:
        return "DateFormatter"


class JsonFlattenerTransformer(DataTransformer):
    """Flatten JSON fields."""
    
    def __init__(self, params: Dict[str, Any]):
        self.json_fields = params.get('fields', [])
        self.separator = params.get('separator', '_')
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flatten JSON fields."""
        result = []
        
        for record in data:
            flattened_record = record.copy()
            
            for field in self.json_fields:
                if field in record:
                    try:
                        json_value = record[field]
                        if isinstance(json_value, str):
                            json_value = json.loads(json_value)
                        
                        if isinstance(json_value, dict):
                            # Remove original field
                            del flattened_record[field]
                            
                            # Add flattened fields
                            for key, value in json_value.items():
                                new_field = f"{field}{self.separator}{key}"
                                flattened_record[new_field] = value
                                
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Failed to flatten JSON field {field}: {e}")
            
            result.append(flattened_record)
        
        return result
    
    def get_name(self) -> str:
        return "JsonFlattener"


class CustomFunctionTransformer(DataTransformer):
    """Apply custom function to data."""
    
    def __init__(self, params: Dict[str, Any]):
        self.function_code = params.get('function')
        self.function: Optional[Callable] = None
        
        if self.function_code:
            try:
                # Create function from code string
                exec(f"def custom_transform(data):\n{self.function_code}", globals())
                self.function = globals()['custom_transform']
            except Exception as e:
                logger.error(f"Failed to create custom function: {e}")
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply custom function."""
        if not self.function:
            return data
        
        try:
            return self.function(data)
        except Exception as e:
            logger.error(f"Custom function failed: {e}")
            return data
    
    def get_name(self) -> str:
        return "CustomFunction"
