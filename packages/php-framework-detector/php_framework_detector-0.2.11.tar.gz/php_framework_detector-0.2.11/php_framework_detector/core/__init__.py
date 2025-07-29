"""
Core module for PHP Framework Detector.

This module provides the core functionality for detecting PHP frameworks,
including the base detector class, factory, models, and exceptions.
"""

from .detector import FrameworkDetector
from .factory import FrameworkDetectorFactory
from .models import (
    DetectionConfig,
    DetectionResult,
    FrameworkInfo,
    FrameworkMetadata
)
from .exceptions import (
    FrameworkDetectorError,
    InvalidPathError,
    DetectionError,
    ConfigurationError,
    FileReadError,
    TimeoutError,
    UnsupportedFrameworkError
)

__all__ = [
    # Core classes
    "FrameworkDetector",
    "FrameworkDetectorFactory",
    
    # Models
    "DetectionConfig",
    "DetectionResult", 
    "FrameworkInfo",
    "FrameworkMetadata",
    
    # Exceptions
    "FrameworkDetectorError",
    "InvalidPathError",
    "DetectionError",
    "ConfigurationError",
    "FileReadError",
    "TimeoutError",
    "UnsupportedFrameworkError",
] 