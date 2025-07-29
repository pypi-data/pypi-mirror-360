"""
Custom exceptions for PHP Framework Detector.

This module defines application-specific exceptions for better error handling
and more informative error messages.
"""

from typing import Optional


class FrameworkDetectorError(Exception):
    """Base exception for all framework detector errors."""
    
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


class InvalidPathError(FrameworkDetectorError):
    """Raised when the provided project path is invalid."""
    
    def __init__(self, path: str, reason: Optional[str] = None) -> None:
        message = f"Invalid project path: {path}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, details=reason)


class DetectionError(FrameworkDetectorError):
    """Raised when framework detection fails."""
    
    def __init__(self, message: str, framework: Optional[str] = None) -> None:
        self.framework = framework
        if framework:
            message = f"Detection failed for {framework}: {message}"
        super().__init__(message, details=framework)


class ConfigurationError(FrameworkDetectorError):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        self.config_key = config_key
        if config_key:
            message = f"Configuration error for '{config_key}': {message}"
        super().__init__(message, details=config_key)


class FileReadError(FrameworkDetectorError):
    """Raised when a file cannot be read."""
    
    def __init__(self, file_path: str, reason: Optional[str] = None) -> None:
        self.file_path = file_path
        message = f"Cannot read file: {file_path}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, details=reason)


class TimeoutError(FrameworkDetectorError):
    """Raised when detection operation times out."""
    
    def __init__(self, operation: str, timeout_seconds: int) -> None:
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, details=f"timeout={timeout_seconds}s")


class UnsupportedFrameworkError(FrameworkDetectorError):
    """Raised when an unsupported framework is requested."""
    
    def __init__(self, framework: str, available_frameworks: Optional[list[str]] = None) -> None:
        self.framework = framework
        self.available_frameworks = available_frameworks
        message = f"Unsupported framework: {framework}"
        if available_frameworks:
            message += f". Available frameworks: {', '.join(available_frameworks)}"
        super().__init__(message, details=framework) 