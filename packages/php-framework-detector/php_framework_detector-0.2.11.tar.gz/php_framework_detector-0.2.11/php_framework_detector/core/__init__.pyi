"""
Type stubs for php_framework_detector.core module.

This file provides type annotations for the core module components.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class FrameworkType(Enum):
    """Enumeration of supported PHP frameworks."""
    
    LARAVEL: str
    SYMFONY: str
    CODEIGNITER: str
    CAKEPHP: str
    YII: str
    THINKPHP: str
    SLIM: str
    FATFREE: str
    FASTROUTE: str
    FUEL: str
    PHALCON: str
    PHPIXIE: str
    POPPHP: str
    LAMINAS: str
    ZENDFRAMEWORK: str
    DRUPAL: str
    DRUSH: str
    UNKNOWN: str
    
    @property
    def display_name(self) -> str:
        """Get human-readable framework name."""
        ...
    
    @property
    def description(self) -> str:
        """Get framework description."""
        ...
    
    @classmethod
    def from_string(cls, value: str) -> FrameworkType:
        """Create FrameworkType from string value."""
        ...
    
    @classmethod
    def get_all_frameworks(cls) -> List[FrameworkType]:
        """Get all framework types except UNKNOWN."""
        ...
    
    @classmethod
    def get_major_frameworks(cls) -> List[FrameworkType]:
        """Get major PHP frameworks."""
        ...
    
    @classmethod
    def get_micro_frameworks(cls) -> List[FrameworkType]:
        """Get micro-frameworks."""
        ...
    
    @classmethod
    def get_enterprise_frameworks(cls) -> List[FrameworkType]:
        """Get enterprise frameworks."""
        ...
    
    @classmethod
    def get_cms_frameworks(cls) -> List[FrameworkType]:
        """Get CMS frameworks."""
        ...


class DetectionConfig(BaseModel):
    """Configuration for framework detection."""
    
    check_composer: bool = Field(True, description="Check composer files")
    check_files: bool = Field(True, description="Check file patterns")
    check_dependencies: bool = Field(True, description="Check dependencies")
    max_file_size: int = Field(1024 * 1024, ge=1024, description="Max file size to read")
    timeout: int = Field(30, ge=1, le=300, description="Detection timeout in seconds")
    verbose: bool = Field(False, description="Enable verbose logging")


class FrameworkInfo(BaseModel):
    """Information about a PHP framework."""
    
    framework_type: FrameworkType = Field(..., description="Framework type enum")
    name: Optional[str] = Field(None, description="Human-readable framework name")
    description: Optional[str] = Field(None, description="Framework description")
    version: Optional[str] = Field(None, description="Detected framework version")
    confidence: int = Field(100, ge=0, le=100, description="Detection confidence score")
    
    @property
    def code(self) -> str:
        """Get framework code for backward compatibility."""
        ...


class DetectionResult(BaseModel):
    """Result of framework detection analysis."""
    
    detected_framework: FrameworkType = Field(..., description="Framework type enum of detected framework")
    detected_name: Optional[str] = Field(None, description="Name of detected framework")
    scores: Dict[FrameworkType, int] = Field(..., description="Detection scores for all frameworks")
    project_path: str = Field(..., description="Path to analyzed project")
    detection_time: datetime = Field(default_factory=datetime.now, description="Detection timestamp")
    total_frameworks: Optional[int] = Field(None, description="Total frameworks checked")
    
    @property
    def is_framework_detected(self) -> bool:
        """Check if a framework was detected."""
        ...
    
    @property
    def confidence_score(self) -> int:
        """Get confidence score of detected framework."""
        ...
    
    @property
    def top_frameworks(self, limit: int = 5) -> Dict[FrameworkType, int]:
        """Get top frameworks by score."""
        ...
    
    @property
    def detected_framework_code(self) -> str:
        """Get framework code for backward compatibility."""
        ...


class FrameworkMetadata(BaseModel):
    """Metadata about framework detection capabilities."""
    
    framework_type: FrameworkType = Field(..., description="Framework type enum")
    detection_methods: List[str] = Field(default_factory=list, description="Detection methods")
    file_patterns: List[str] = Field(default_factory=list, description="File patterns to check")
    composer_packages: List[str] = Field(default_factory=list, description="Composer packages")
    content_patterns: List[str] = Field(default_factory=list, description="Content patterns")
    
    @property
    def framework_code(self) -> str:
        """Get framework code for backward compatibility."""
        ...


class FrameworkDetectorError(Exception):
    """Base exception for all framework detector errors."""
    
    message: str
    details: Optional[str]
    
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        ...


class InvalidPathError(FrameworkDetectorError):
    """Raised when the provided project path is invalid."""
    
    def __init__(self, path: str, reason: Optional[str] = None) -> None:
        ...


class DetectionError(FrameworkDetectorError):
    """Raised when framework detection fails."""
    
    framework: Optional[str]
    
    def __init__(self, message: str, framework: Optional[str] = None) -> None:
        ...


class ConfigurationError(FrameworkDetectorError):
    """Raised when there's a configuration issue."""
    
    config_key: Optional[str]
    
    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        ...


class FileReadError(FrameworkDetectorError):
    """Raised when a file cannot be read."""
    
    file_path: str
    
    def __init__(self, file_path: str, reason: Optional[str] = None) -> None:
        ...


class TimeoutError(FrameworkDetectorError):
    """Raised when detection operation times out."""
    
    operation: str
    timeout_seconds: int
    
    def __init__(self, operation: str, timeout_seconds: int) -> None:
        ...


class UnsupportedFrameworkError(FrameworkDetectorError):
    """Raised when an unsupported framework is requested."""
    
    framework: str
    available_frameworks: Optional[List[str]]
    
    def __init__(self, framework: str, available_frameworks: Optional[List[str]] = None) -> None:
        ...


class FrameworkDetector(ABC):
    """Abstract base class for all framework detectors."""
    
    project_path: Path
    config: DetectionConfig
    _composer_data: Optional[Dict[str, Any]]
    _file_cache: Dict[str, str]
    
    def __init__(self, project_path: str, config: Optional[DetectionConfig] = None) -> None:
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the framework identifier code."""
        ...
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        ...
    
    @property
    def description(self) -> str:
        """Return framework description."""
        ...
    
    @property
    def metadata(self) -> FrameworkMetadata:
        """Return framework detection metadata."""
        ...
    
    async def detect_async(self) -> int:
        """Asynchronous detection method with scoring."""
        ...
    
    async def _detect_async_impl(self) -> int:
        """Internal async detection implementation."""
        ...
    
    async def _load_composer_json_async(self) -> Dict[str, Any]:
        """Asynchronously load composer.json or composer.lock file."""
        ...
    
    async def _check_path_patterns_async(self, patterns: List[str]) -> bool:
        """Asynchronously check if any of the path patterns exist."""
        ...
    
    async def _check_composer_dependency_async(self, package_name: str) -> bool:
        """Asynchronously check if a package is listed in composer dependencies."""
        ...
    
    async def _check_file_content_async(
        self,
        file_path: Union[str, Path],
        content_patterns: List[str],
        max_size: Optional[int] = None
    ) -> bool:
        """Asynchronously check if a file contains specific content patterns."""
        ...
    
    async def _check_regex_patterns_async(
        self,
        file_path: Union[str, Path],
        regex_patterns: List[str],
        max_size: Optional[int] = None
    ) -> bool:
        """Asynchronously check if a file matches regex patterns."""
        ...
    
    def _get_detection_methods(self) -> List[str]:
        """Get list of detection methods used by this detector."""
        ...
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for this framework."""
        ...
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for this framework."""
        ...
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in files."""
        ...
    
    def _load_composer_json(self) -> Dict[str, Any]:
        """Load composer.json file synchronously for backward compatibility."""
        ...


class FrameworkDetectorFactory:
    """Factory class for creating and managing framework detectors."""
    
    _detectors: Dict[str, type[FrameworkDetector]]
    _initialized: bool
    
    @classmethod
    def register_detector(cls, detector_class: type[FrameworkDetector]) -> None:
        """Register a framework detector class."""
        ...
    
    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure all detectors are registered."""
        ...
    
    @classmethod
    def get_detector(
        cls,
        framework_name: str,
        project_path: str,
        config: Optional[DetectionConfig] = None
    ) -> FrameworkDetector:
        """Get a detector instance for the specified framework."""
        ...
    
    @classmethod
    def get_all_detectors(
        cls,
        project_path: str,
        config: Optional[DetectionConfig] = None
    ) -> List[FrameworkDetector]:
        """Get all detector instances."""
        ...
    
    @classmethod
    def get_available_frameworks(cls) -> List[str]:
        """Get list of available framework names."""
        ...
    
    @classmethod
    def get_framework_names(cls) -> Dict[str, str]:
        """Get mapping of framework codes to display names."""
        ...
    
    @classmethod
    def get_framework_types(cls) -> Dict[str, FrameworkType]:
        """Get mapping of framework codes to FrameworkType enums."""
        ...
    
    @classmethod
    def get_framework_metadata(cls) -> Dict[str, FrameworkMetadata]:
        """Get metadata for all available frameworks."""
        ...
    
    @classmethod
    async def detect_all_frameworks_async(
        cls,
        project_path: str,
        config: Optional[DetectionConfig] = None
    ) -> Dict[FrameworkType, int]:
        """Detect all frameworks asynchronously."""
        ...


__all__ = [
    "FrameworkType",
    "DetectionConfig",
    "FrameworkInfo",
    "DetectionResult",
    "FrameworkMetadata",
    "FrameworkDetectorError",
    "InvalidPathError",
    "DetectionError",
    "ConfigurationError",
    "FileReadError",
    "TimeoutError",
    "UnsupportedFrameworkError",
    "FrameworkDetector",
    "FrameworkDetectorFactory",
] 