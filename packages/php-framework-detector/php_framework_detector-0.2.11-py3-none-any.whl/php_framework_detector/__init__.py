"""
PHP Framework Detector

A modern Python tool for detecting PHP frameworks in project directories.
Provides async-aware detection with comprehensive framework support.
"""

from .core import (
    FrameworkDetector,
    FrameworkDetectorFactory,
    DetectionConfig,
    DetectionResult,
    FrameworkInfo,
    FrameworkMetadata
)
from .core.exceptions import (
    FrameworkDetectorError,
    InvalidPathError,
    DetectionError,
    ConfigurationError,
    FileReadError,
    TimeoutError,
    UnsupportedFrameworkError
)

def get_framework_names() -> dict:
    """
    Get mapping of framework codes to display names.
    
    Returns:
        Dictionary mapping framework codes to display names
    """
    from .core.factory import FrameworkDetectorFactory
    return FrameworkDetectorFactory.get_framework_names()


def get_available_frameworks() -> list:
    """
    Get list of available framework names.
    
    Returns:
        List of available framework codes
    """
    from .core.factory import FrameworkDetectorFactory
    return FrameworkDetectorFactory.get_available_frameworks()


def detect_framework(project_path: str) -> DetectionResult:
    """
    Detect the PHP framework used in the specified directory (synchronous interface, implemented via async under the hood).
    Returns a DetectionResult instance.
    """
    import asyncio
    from pathlib import Path
    from .cli import detect_frameworks_async
    return asyncio.run(detect_frameworks_async(Path(project_path)))


__version__ = "0.2.0"
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
    
    # API
    "get_framework_names",
    "get_available_frameworks",
    "detect_framework",
] 