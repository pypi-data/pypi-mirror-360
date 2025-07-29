"""
Tests for custom exceptions.

This module tests all custom exceptions defined in the application.
"""

import pytest

from php_framework_detector.core.exceptions import (
    FrameworkDetectorError,
    InvalidPathError,
    DetectionError,
    ConfigurationError,
    FileReadError,
    TimeoutError,
    UnsupportedFrameworkError
)


class TestFrameworkDetectorError:
    """Test base FrameworkDetectorError."""
    
    def test_base_error_creation(self):
        """Test creating base FrameworkDetectorError."""
        error = FrameworkDetectorError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details is None
    
    def test_base_error_with_details(self):
        """Test creating FrameworkDetectorError with details."""
        error = FrameworkDetectorError("Test error", "Additional details")
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == "Additional details"
    
    def test_error_inheritance(self):
        """Test that FrameworkDetectorError is a proper exception."""
        error = FrameworkDetectorError("Test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, FrameworkDetectorError)


class TestInvalidPathError:
    """Test InvalidPathError."""
    
    def test_invalid_path_error_creation(self):
        """Test creating InvalidPathError."""
        error = InvalidPathError("/invalid/path")
        
        assert str(error) == "Invalid project path: /invalid/path"
        assert error.message == "Invalid project path: /invalid/path"
        assert error.details is None
    
    def test_invalid_path_error_with_reason(self):
        """Test creating InvalidPathError with reason."""
        error = InvalidPathError("/invalid/path", "Directory does not exist")
        
        assert str(error) == "Invalid project path: /invalid/path - Directory does not exist"
        assert error.message == "Invalid project path: /invalid/path - Directory does not exist"
        assert error.details == "Directory does not exist"
    
    def test_invalid_path_error_inheritance(self):
        """Test InvalidPathError inheritance."""
        error = InvalidPathError("/test/path")
        
        assert isinstance(error, FrameworkDetectorError)
        assert isinstance(error, InvalidPathError)


class TestDetectionError:
    """Test DetectionError."""
    
    def test_detection_error_creation(self):
        """Test creating DetectionError."""
        error = DetectionError("Detection failed")
        
        assert str(error) == "Detection failed"
        assert error.message == "Detection failed"
        assert error.details is None
        assert error.framework is None
    
    def test_detection_error_with_framework(self):
        """Test creating DetectionError with framework."""
        error = DetectionError("Detection failed", "laravel")
        
        assert str(error) == "Detection failed for laravel: Detection failed"
        assert error.message == "Detection failed for laravel: Detection failed"
        assert error.details == "laravel"
        assert error.framework == "laravel"
    
    def test_detection_error_inheritance(self):
        """Test DetectionError inheritance."""
        error = DetectionError("Test")
        
        assert isinstance(error, FrameworkDetectorError)
        assert isinstance(error, DetectionError)


class TestConfigurationError:
    """Test ConfigurationError."""
    
    def test_configuration_error_creation(self):
        """Test creating ConfigurationError."""
        error = ConfigurationError("Invalid configuration")
        
        assert str(error) == "Invalid configuration"
        assert error.message == "Invalid configuration"
        assert error.details is None
        assert error.config_key is None
    
    def test_configuration_error_with_key(self):
        """Test creating ConfigurationError with config key."""
        error = ConfigurationError("Invalid value", "timeout")
        
        assert str(error) == "Configuration error for 'timeout': Invalid value"
        assert error.message == "Configuration error for 'timeout': Invalid value"
        assert error.details == "timeout"
        assert error.config_key == "timeout"
    
    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inheritance."""
        error = ConfigurationError("Test")
        
        assert isinstance(error, FrameworkDetectorError)
        assert isinstance(error, ConfigurationError)


class TestFileReadError:
    """Test FileReadError."""
    
    def test_file_read_error_creation(self):
        """Test creating FileReadError."""
        error = FileReadError("/path/to/file.txt")
        
        assert str(error) == "Cannot read file: /path/to/file.txt"
        assert error.message == "Cannot read file: /path/to/file.txt"
        assert error.details is None
        assert error.file_path == "/path/to/file.txt"
    
    def test_file_read_error_with_reason(self):
        """Test creating FileReadError with reason."""
        error = FileReadError("/path/to/file.txt", "Permission denied")
        
        assert str(error) == "Cannot read file: /path/to/file.txt - Permission denied"
        assert error.message == "Cannot read file: /path/to/file.txt - Permission denied"
        assert error.details == "Permission denied"
        assert error.file_path == "/path/to/file.txt"
    
    def test_file_read_error_inheritance(self):
        """Test FileReadError inheritance."""
        error = FileReadError("/test/file")
        
        assert isinstance(error, FrameworkDetectorError)
        assert isinstance(error, FileReadError)


class TestTimeoutError:
    """Test TimeoutError."""
    
    def test_timeout_error_creation(self):
        """Test creating TimeoutError."""
        error = TimeoutError("framework detection", 30)
        
        assert str(error) == "Operation 'framework detection' timed out after 30 seconds"
        assert error.message == "Operation 'framework detection' timed out after 30 seconds"
        assert error.details == "timeout=30s"
        assert error.operation == "framework detection"
        assert error.timeout_seconds == 30
    
    def test_timeout_error_different_operation(self):
        """Test creating TimeoutError with different operation."""
        error = TimeoutError("file reading", 60)
        
        assert str(error) == "Operation 'file reading' timed out after 60 seconds"
        assert error.message == "Operation 'file reading' timed out after 60 seconds"
        assert error.details == "timeout=60s"
        assert error.operation == "file reading"
        assert error.timeout_seconds == 60
    
    def test_timeout_error_inheritance(self):
        """Test TimeoutError inheritance."""
        error = TimeoutError("test", 10)
        
        assert isinstance(error, FrameworkDetectorError)
        assert isinstance(error, TimeoutError)


class TestUnsupportedFrameworkError:
    """Test UnsupportedFrameworkError."""
    
    def test_unsupported_framework_error_creation(self):
        """Test creating UnsupportedFrameworkError."""
        error = UnsupportedFrameworkError("unknown_framework")
        
        assert str(error) == "Unsupported framework: unknown_framework"
        assert error.message == "Unsupported framework: unknown_framework"
        assert error.details == "unknown_framework"
        assert error.framework == "unknown_framework"
        assert error.available_frameworks is None
    
    def test_unsupported_framework_error_with_available(self):
        """Test creating UnsupportedFrameworkError with available frameworks."""
        available = ["laravel", "symfony", "codeigniter"]
        error = UnsupportedFrameworkError("unknown_framework", available)
        
        assert str(error) == "Unsupported framework: unknown_framework. Available frameworks: laravel, symfony, codeigniter"
        assert error.message == "Unsupported framework: unknown_framework. Available frameworks: laravel, symfony, codeigniter"
        assert error.details == "unknown_framework"
        assert error.framework == "unknown_framework"
        assert error.available_frameworks == available
    
    def test_unsupported_framework_error_inheritance(self):
        """Test UnsupportedFrameworkError inheritance."""
        error = UnsupportedFrameworkError("test")
        
        assert isinstance(error, FrameworkDetectorError)
        assert isinstance(error, UnsupportedFrameworkError)


class TestExceptionUsage:
    """Test how exceptions are used in practice."""
    
    def test_exception_chaining(self):
        """Test that exceptions can be chained properly."""
        try:
            raise InvalidPathError("/test/path", "Not found")
        except InvalidPathError as e:
            assert str(e) == "Invalid project path: /test/path - Not found"
            assert e.details == "Not found"
    
    def test_exception_catching(self):
        """Test catching different exception types."""
        exceptions = [
            InvalidPathError("/test", "reason"),
            DetectionError("failed", "laravel"),
            ConfigurationError("invalid", "key"),
            FileReadError("/file.txt", "permission"),
            TimeoutError("operation", 30),
            UnsupportedFrameworkError("framework", ["laravel"])
        ]
        
        for exc in exceptions:
            assert isinstance(exc, FrameworkDetectorError)
            assert str(exc) != ""
            assert exc.message != ""
    
    def test_exception_attributes(self):
        """Test that all exceptions have the expected attributes."""
        # Test base error
        base_error = FrameworkDetectorError("test", "details")
        assert hasattr(base_error, 'message')
        assert hasattr(base_error, 'details')
        
        # Test specific errors
        path_error = InvalidPathError("/test", "reason")
        assert hasattr(path_error, 'message')
        assert hasattr(path_error, 'details')
        
        detection_error = DetectionError("test", "framework")
        assert hasattr(detection_error, 'framework')
        
        config_error = ConfigurationError("test", "key")
        assert hasattr(config_error, 'config_key')
        
        file_error = FileReadError("/test", "reason")
        assert hasattr(file_error, 'file_path')
        
        timeout_error = TimeoutError("operation", 30)
        assert hasattr(timeout_error, 'operation')
        assert hasattr(timeout_error, 'timeout_seconds')
        
        unsupported_error = UnsupportedFrameworkError("test", ["laravel"])
        assert hasattr(unsupported_error, 'framework')
        assert hasattr(unsupported_error, 'available_frameworks') 