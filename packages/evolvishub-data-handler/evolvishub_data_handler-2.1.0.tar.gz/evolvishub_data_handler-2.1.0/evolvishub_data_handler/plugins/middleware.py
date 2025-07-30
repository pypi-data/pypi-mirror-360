"""
Middleware plugins for processing data flow between source and destination.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import time
from .base import BasePlugin, PluginMetadata, PluginType
from loguru import logger


class BaseMiddleware(ABC):
    """Base class for middleware components."""
    
    @abstractmethod
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process before reading from source."""
        pass
    
    @abstractmethod
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process after reading from source."""
        pass
    
    @abstractmethod
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process before writing to destination."""
        pass
    
    @abstractmethod
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """Process after writing to destination."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get middleware name."""
        pass


class MiddlewarePlugin(BasePlugin):
    """Plugin for middleware pipeline."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.middleware_stack: List[BaseMiddleware] = []
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return middleware plugin metadata."""
        return PluginMetadata(
            name="MiddlewarePlugin",
            version="1.0.0",
            description="Middleware pipeline plugin",
            author="Evolvishub",
            plugin_type=PluginType.MIDDLEWARE
        )
    
    def initialize(self) -> None:
        """Initialize middleware stack."""
        middleware_config = self.config.get('middleware', [])
        
        for mw_config in middleware_config:
            middleware_type = mw_config.get('type')
            middleware_params = mw_config.get('params', {})
            
            middleware = self._create_middleware(middleware_type, middleware_params)
            if middleware:
                self.middleware_stack.append(middleware)
                logger.info(f"Added middleware: {middleware.get_name()}")
    
    def cleanup(self) -> None:
        """Cleanup middleware resources."""
        self.middleware_stack.clear()
    
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process config before reading."""
        result = config
        
        for middleware in self.middleware_stack:
            try:
                result = middleware.process_before_read(result)
            except Exception as e:
                logger.error(f"Middleware {middleware.get_name()} before_read failed: {e}")
                raise
        
        return result
    
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data after reading."""
        result = data
        
        for middleware in self.middleware_stack:
            try:
                result = middleware.process_after_read(result)
            except Exception as e:
                logger.error(f"Middleware {middleware.get_name()} after_read failed: {e}")
                raise
        
        return result
    
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data before writing."""
        result = data
        
        for middleware in self.middleware_stack:
            try:
                result = middleware.process_before_write(result)
            except Exception as e:
                logger.error(f"Middleware {middleware.get_name()} before_write failed: {e}")
                raise
        
        return result
    
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """Process after writing."""
        for middleware in self.middleware_stack:
            try:
                middleware.process_after_write(data, result)
            except Exception as e:
                logger.error(f"Middleware {middleware.get_name()} after_write failed: {e}")
                # Don't raise here as write is already complete
    
    def add_middleware(self, middleware: BaseMiddleware) -> None:
        """Add middleware to the stack."""
        self.middleware_stack.append(middleware)
    
    def _create_middleware(self, middleware_type: str, params: Dict[str, Any]) -> Optional[BaseMiddleware]:
        """Create middleware instance based on type."""
        middleware_map = {
            'logging': LoggingMiddleware,
            'metrics': MetricsMiddleware,
            'validation': ValidationMiddleware,
            'rate_limiter': RateLimiterMiddleware,
            'data_quality': DataQualityMiddleware,
            'audit': AuditMiddleware,
        }
        
        middleware_class = middleware_map.get(middleware_type)
        if middleware_class:
            return middleware_class(params)
        
        logger.warning(f"Unknown middleware type: {middleware_type}")
        return None


class LoggingMiddleware(BaseMiddleware):
    """Middleware for detailed logging."""
    
    def __init__(self, params: Dict[str, Any]):
        self.log_level = params.get('level', 'INFO')
        self.log_data = params.get('log_data', False)
    
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Log before read."""
        logger.log(self.log_level, f"Starting read from {config.get('type', 'unknown')}")
        return config
    
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Log after read."""
        logger.log(self.log_level, f"Read {len(data)} records")
        if self.log_data and data:
            logger.debug(f"Sample record: {data[0]}")
        return data
    
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Log before write."""
        logger.log(self.log_level, f"Writing {len(data)} records")
        return data
    
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """Log after write."""
        logger.log(self.log_level, f"Successfully wrote {len(data)} records")
    
    def get_name(self) -> str:
        return "LoggingMiddleware"


class MetricsMiddleware(BaseMiddleware):
    """Middleware for collecting metrics."""
    
    def __init__(self, params: Dict[str, Any]):
        self.metrics = {}
        self.start_time = None
    
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start timing."""
        self.start_time = time.time()
        return config
    
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Record read metrics."""
        if self.start_time:
            read_time = time.time() - self.start_time
            self.metrics['read_time'] = read_time
            self.metrics['records_read'] = len(data)
            self.metrics['read_rate'] = len(data) / read_time if read_time > 0 else 0
        return data
    
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Start write timing."""
        self.metrics['write_start'] = time.time()
        return data
    
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """Record write metrics."""
        if 'write_start' in self.metrics:
            write_time = time.time() - self.metrics['write_start']
            self.metrics['write_time'] = write_time
            self.metrics['records_written'] = len(data)
            self.metrics['write_rate'] = len(data) / write_time if write_time > 0 else 0
            
            # Log metrics
            logger.info(f"Sync metrics: {self.metrics}")
    
    def get_name(self) -> str:
        return "MetricsMiddleware"


class ValidationMiddleware(BaseMiddleware):
    """Middleware for data validation."""
    
    def __init__(self, params: Dict[str, Any]):
        self.validation_rules = params.get('rules', {})
        self.strict_mode = params.get('strict', False)
    
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """No validation before read."""
        return config
    
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate read data."""
        return self._validate_data(data)
    
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate data before write."""
        return self._validate_data(data)
    
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """No validation after write."""
        pass
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate data against rules."""
        valid_records = []
        invalid_count = 0
        
        for record in data:
            is_valid = True
            
            for field, rules in self.validation_rules.items():
                if field in record:
                    value = record[field]
                    
                    # Required field check
                    if rules.get('required', False) and (value is None or value == ''):
                        logger.warning(f"Required field {field} is empty")
                        is_valid = False
                    
                    # Type check
                    expected_type = rules.get('type')
                    if expected_type and value is not None:
                        if expected_type == 'string' and not isinstance(value, str):
                            is_valid = False
                        elif expected_type == 'number' and not isinstance(value, (int, float)):
                            is_valid = False
                        elif expected_type == 'boolean' and not isinstance(value, bool):
                            is_valid = False
                    
                    # Range check for numbers
                    if isinstance(value, (int, float)):
                        min_val = rules.get('min')
                        max_val = rules.get('max')
                        if min_val is not None and value < min_val:
                            is_valid = False
                        if max_val is not None and value > max_val:
                            is_valid = False
            
            if is_valid:
                valid_records.append(record)
            else:
                invalid_count += 1
                if self.strict_mode:
                    raise ValueError(f"Data validation failed for record: {record}")
        
        if invalid_count > 0:
            logger.warning(f"Filtered out {invalid_count} invalid records")
        
        return valid_records
    
    def get_name(self) -> str:
        return "ValidationMiddleware"


class RateLimiterMiddleware(BaseMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, params: Dict[str, Any]):
        self.max_records_per_second = params.get('max_records_per_second', 1000)
        self.last_process_time = 0
    
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """No rate limiting before read."""
        return config
    
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply rate limiting after read."""
        return self._apply_rate_limit(data)
    
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply rate limiting before write."""
        return self._apply_rate_limit(data)
    
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """No rate limiting after write."""
        pass
    
    def _apply_rate_limit(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply rate limiting."""
        current_time = time.time()
        records_count = len(data)
        
        if records_count > 0:
            required_time = records_count / self.max_records_per_second
            elapsed_time = current_time - self.last_process_time
            
            if elapsed_time < required_time:
                sleep_time = required_time - elapsed_time
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_process_time = time.time()
        
        return data
    
    def get_name(self) -> str:
        return "RateLimiterMiddleware"


class DataQualityMiddleware(BaseMiddleware):
    """Middleware for data quality checks."""
    
    def __init__(self, params: Dict[str, Any]):
        self.quality_checks = params.get('checks', {})
        self.quality_metrics = {}
    
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize quality metrics."""
        self.quality_metrics = {
            'total_records': 0,
            'null_values': 0,
            'duplicate_records': 0,
            'data_type_errors': 0
        }
        return config
    
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check data quality after read."""
        return self._check_quality(data)
    
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Final quality check before write."""
        return data
    
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """Log quality metrics."""
        logger.info(f"Data quality metrics: {self.quality_metrics}")
    
    def _check_quality(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform data quality checks."""
        self.quality_metrics['total_records'] = len(data)
        
        # Check for null values
        for record in data:
            for field, value in record.items():
                if value is None or value == '':
                    self.quality_metrics['null_values'] += 1
        
        # Check for duplicates (simple implementation)
        seen_records = set()
        unique_data = []
        
        for record in data:
            record_hash = hash(str(sorted(record.items())))
            if record_hash not in seen_records:
                seen_records.add(record_hash)
                unique_data.append(record)
            else:
                self.quality_metrics['duplicate_records'] += 1
        
        return unique_data
    
    def get_name(self) -> str:
        return "DataQualityMiddleware"


class AuditMiddleware(BaseMiddleware):
    """Middleware for audit logging."""
    
    def __init__(self, params: Dict[str, Any]):
        self.audit_file = params.get('audit_file', 'sync_audit.log')
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def process_before_read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Log audit start."""
        self._write_audit(f"SYNC_START: {self.session_id} - Source: {config.get('type')}")
        return config
    
    def process_after_read(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Log read audit."""
        self._write_audit(f"READ_COMPLETE: {self.session_id} - Records: {len(data)}")
        return data
    
    def process_before_write(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Log write start."""
        self._write_audit(f"WRITE_START: {self.session_id} - Records: {len(data)}")
        return data
    
    def process_after_write(self, data: List[Dict[str, Any]], result: Any) -> None:
        """Log write complete."""
        self._write_audit(f"WRITE_COMPLETE: {self.session_id} - Records: {len(data)}")
        self._write_audit(f"SYNC_END: {self.session_id}")
    
    def _write_audit(self, message: str) -> None:
        """Write audit message."""
        timestamp = datetime.now().isoformat()
        audit_entry = f"{timestamp} - {message}\n"
        
        try:
            with open(self.audit_file, 'a') as f:
                f.write(audit_entry)
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_name(self) -> str:
        return "AuditMiddleware"
