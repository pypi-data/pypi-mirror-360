"""
Tests for middleware plugins.
"""

import pytest
import tempfile
import os
import time
from unittest.mock import Mock, patch

from evolvishub_data_handler.plugins.middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    ValidationMiddleware,
    RateLimiterMiddleware,
    DataQualityMiddleware,
    AuditMiddleware,
    MiddlewarePlugin
)


class TestLoggingMiddleware:
    """Test logging middleware."""

    def test_logging_middleware_basic(self):
        """Test basic logging middleware functionality."""
        middleware = LoggingMiddleware({"level": "INFO", "log_data": False})
        
        config = {"type": "postgresql"}
        data = [{"id": 1, "name": "test"}]
        
        # Test all middleware methods
        result_config = middleware.process_before_read(config)
        assert result_config == config
        
        result_data = middleware.process_after_read(data)
        assert result_data == data
        
        result_data = middleware.process_before_write(data)
        assert result_data == data
        
        middleware.process_after_write(data, None)
        
        assert middleware.get_name() == "LoggingMiddleware"

    def test_logging_middleware_with_data_logging(self):
        """Test logging middleware with data logging enabled."""
        middleware = LoggingMiddleware({"level": "DEBUG", "log_data": True})
        
        data = [{"id": 1, "name": "test", "sensitive": "data"}]
        result = middleware.process_after_read(data)
        
        assert result == data


class TestMetricsMiddleware:
    """Test metrics middleware."""

    def test_metrics_collection(self):
        """Test metrics collection functionality."""
        middleware = MetricsMiddleware({})
        
        config = {"type": "postgresql"}
        data = [{"id": i, "name": f"test{i}"} for i in range(100)]
        
        # Simulate processing pipeline
        middleware.process_before_read(config)
        time.sleep(0.01)  # Small delay to measure
        middleware.process_after_read(data)
        middleware.process_before_write(data)
        time.sleep(0.01)  # Small delay to measure
        middleware.process_after_write(data, None)
        
        # Check metrics were collected
        assert "read_time" in middleware.metrics
        assert "records_read" in middleware.metrics
        assert "write_time" in middleware.metrics
        assert "records_written" in middleware.metrics
        assert middleware.metrics["records_read"] == 100
        assert middleware.metrics["records_written"] == 100
        assert middleware.metrics["read_time"] > 0
        assert middleware.metrics["write_time"] > 0

    def test_metrics_rates(self):
        """Test metrics rate calculations."""
        middleware = MetricsMiddleware({})
        
        data = [{"id": i} for i in range(50)]
        
        middleware.process_before_read({})
        time.sleep(0.01)
        middleware.process_after_read(data)
        
        assert "read_rate" in middleware.metrics
        assert middleware.metrics["read_rate"] > 0


class TestValidationMiddleware:
    """Test validation middleware."""

    def test_validation_rules(self):
        """Test data validation with rules."""
        rules = {
            "email": {"required": True, "type": "string"},
            "age": {"type": "number", "min": 0, "max": 150}
        }
        middleware = ValidationMiddleware({"rules": rules, "strict": False})
        
        data = [
            {"email": "john@example.com", "age": 30, "name": "John"},
            {"email": "", "age": 25, "name": "Jane"},  # Invalid email
            {"email": "bob@example.com", "age": 200, "name": "Bob"},  # Invalid age
            {"email": "alice@example.com", "age": "thirty", "name": "Alice"}  # Invalid age type
        ]
        
        result = middleware.process_after_read(data)
        
        # Should filter out invalid records
        assert len(result) == 1
        assert result[0]["name"] == "John"

    def test_validation_strict_mode(self):
        """Test validation in strict mode."""
        rules = {
            "email": {"required": True, "type": "string"}
        }
        middleware = ValidationMiddleware({"rules": rules, "strict": True})
        
        data = [{"email": "", "name": "Invalid"}]
        
        with pytest.raises(ValueError):
            middleware.process_after_read(data)

    def test_validation_type_checks(self):
        """Test different type validations."""
        rules = {
            "name": {"type": "string"},
            "age": {"type": "number"},
            "active": {"type": "boolean"}
        }
        middleware = ValidationMiddleware({"rules": rules, "strict": False})
        
        data = [
            {"name": "John", "age": 30, "active": True},  # Valid
            {"name": 123, "age": "thirty", "active": "yes"}  # Invalid types
        ]
        
        result = middleware.process_after_read(data)
        assert len(result) == 1
        assert result[0]["name"] == "John"


class TestRateLimiterMiddleware:
    """Test rate limiter middleware."""

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Set very low rate limit for testing
        middleware = RateLimiterMiddleware({"max_records_per_second": 10})
        
        data = [{"id": i} for i in range(20)]
        
        start_time = time.time()
        middleware.process_after_read(data)
        end_time = time.time()
        
        # Should take at least 2 seconds for 20 records at 10/sec
        elapsed = end_time - start_time
        assert elapsed >= 1.0  # Allow some tolerance

    def test_rate_limiting_small_batches(self):
        """Test rate limiting with small batches."""
        middleware = RateLimiterMiddleware({"max_records_per_second": 1000})
        
        data = [{"id": 1}]
        
        start_time = time.time()
        middleware.process_after_read(data)
        end_time = time.time()
        
        # Should be very fast for small batches
        elapsed = end_time - start_time
        assert elapsed < 0.1


class TestDataQualityMiddleware:
    """Test data quality middleware."""

    def test_null_value_detection(self):
        """Test null value detection."""
        middleware = DataQualityMiddleware({"checks": {}})
        
        data = [
            {"name": "John", "email": "john@example.com"},
            {"name": None, "email": "jane@example.com"},
            {"name": "Bob", "email": ""}
        ]
        
        middleware.process_before_read({})
        result = middleware.process_after_read(data)
        
        assert middleware.quality_metrics["total_records"] == 3
        assert middleware.quality_metrics["null_values"] == 2  # None and empty string

    def test_duplicate_detection(self):
        """Test duplicate record detection."""
        middleware = DataQualityMiddleware({"checks": {}})
        
        data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"},
            {"name": "John", "email": "john@example.com"}  # Duplicate
        ]
        
        middleware.process_before_read({})
        result = middleware.process_after_read(data)
        
        assert len(result) == 2  # Duplicate removed
        assert middleware.quality_metrics["duplicate_records"] == 1

    def test_quality_metrics_logging(self):
        """Test quality metrics are logged."""
        middleware = DataQualityMiddleware({"checks": {}})
        
        data = [{"name": "John", "email": None}]
        
        middleware.process_before_read({})
        middleware.process_after_read(data)
        middleware.process_after_write(data, None)
        
        # Should have collected metrics
        assert "total_records" in middleware.quality_metrics
        assert "null_values" in middleware.quality_metrics


class TestAuditMiddleware:
    """Test audit middleware."""

    def test_audit_logging(self):
        """Test audit logging functionality."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            audit_file = f.name
        
        try:
            middleware = AuditMiddleware({"audit_file": audit_file})
            
            config = {"type": "postgresql"}
            data = [{"id": 1, "name": "test"}]
            
            # Simulate full pipeline
            middleware.process_before_read(config)
            middleware.process_after_read(data)
            middleware.process_before_write(data)
            middleware.process_after_write(data, None)
            
            # Check audit file was created and contains expected entries
            assert os.path.exists(audit_file)
            
            with open(audit_file, 'r') as f:
                content = f.read()
                assert "SYNC_START" in content
                assert "READ_COMPLETE" in content
                assert "WRITE_START" in content
                assert "WRITE_COMPLETE" in content
                assert "SYNC_END" in content
                
        finally:
            if os.path.exists(audit_file):
                os.remove(audit_file)

    def test_audit_session_id(self):
        """Test audit session ID consistency."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            audit_file = f.name
        
        try:
            middleware = AuditMiddleware({"audit_file": audit_file})
            
            # Get session ID
            session_id = middleware.session_id
            assert session_id is not None
            assert len(session_id) > 0
            
            # Process some data
            middleware.process_before_read({})
            middleware.process_after_read([])
            
            # Check session ID is consistent in log
            with open(audit_file, 'r') as f:
                content = f.read()
                assert session_id in content
                
        finally:
            if os.path.exists(audit_file):
                os.remove(audit_file)


class TestMiddlewarePlugin:
    """Test middleware plugin integration."""

    def test_middleware_plugin_initialization(self):
        """Test middleware plugin initialization."""
        config = {
            "middleware": [
                {
                    "type": "logging",
                    "params": {"level": "INFO"}
                },
                {
                    "type": "metrics",
                    "params": {}
                }
            ]
        }
        
        plugin = MiddlewarePlugin(config)
        plugin.initialize()
        
        assert len(plugin.middleware_stack) == 2
        assert plugin.middleware_stack[0].get_name() == "LoggingMiddleware"
        assert plugin.middleware_stack[1].get_name() == "MetricsMiddleware"
        
        plugin.cleanup()

    def test_middleware_pipeline(self):
        """Test complete middleware pipeline."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            audit_file = f.name
        
        try:
            config = {
                "middleware": [
                    {
                        "type": "logging",
                        "params": {"level": "INFO"}
                    },
                    {
                        "type": "validation",
                        "params": {
                            "rules": {"email": {"required": True}},
                            "strict": False
                        }
                    },
                    {
                        "type": "audit",
                        "params": {"audit_file": audit_file}
                    }
                ]
            }
            
            plugin = MiddlewarePlugin(config)
            plugin.initialize()
            
            # Test pipeline
            config_data = {"type": "test"}
            test_data = [
                {"email": "john@example.com", "name": "John"},
                {"email": "", "name": "Invalid"}  # Should be filtered
            ]
            
            result_config = plugin.process_before_read(config_data)
            assert result_config == config_data
            
            result_data = plugin.process_after_read(test_data)
            assert len(result_data) == 1  # Validation filtered one record
            assert result_data[0]["name"] == "John"
            
            result_data = plugin.process_before_write(result_data)
            assert len(result_data) == 1
            
            plugin.process_after_write(result_data, None)
            
            # Check audit log was created
            assert os.path.exists(audit_file)
            
            plugin.cleanup()
            
        finally:
            if os.path.exists(audit_file):
                os.remove(audit_file)

    def test_unknown_middleware_type(self):
        """Test handling of unknown middleware types."""
        config = {
            "middleware": [
                {
                    "type": "unknown_middleware",
                    "params": {}
                }
            ]
        }
        
        plugin = MiddlewarePlugin(config)
        plugin.initialize()
        
        # Should handle unknown middleware gracefully
        assert len(plugin.middleware_stack) == 0
        
        plugin.cleanup()

    def test_middleware_error_handling(self):
        """Test middleware error handling."""
        # Create a mock middleware that raises an exception
        class FailingMiddleware:
            def get_name(self):
                return "FailingMiddleware"
            
            def process_before_read(self, config):
                raise Exception("Middleware failed")
            
            def process_after_read(self, data):
                return data
            
            def process_before_write(self, data):
                return data
            
            def process_after_write(self, data, result):
                pass
        
        plugin = MiddlewarePlugin({})
        plugin.middleware_stack = [FailingMiddleware()]
        
        # Should raise exception when middleware fails
        with pytest.raises(Exception):
            plugin.process_before_read({})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
