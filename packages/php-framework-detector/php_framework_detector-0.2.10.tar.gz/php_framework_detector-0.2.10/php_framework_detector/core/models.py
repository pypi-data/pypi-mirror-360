"""
Data models for PHP Framework Detector.

This module defines Pydantic models for type safety, data validation,
and structured data handling throughout the application.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field, validator


class FrameworkType(Enum):
    """
    Enumeration of supported PHP frameworks.
    
    This enum defines all the PHP frameworks that can be detected
    by the framework detector, providing type safety and consistency.
    """
    # Major PHP Frameworks
    LARAVEL = "laravel"
    SYMFONY = "symfony"
    CODEIGNITER = "codeigniter"
    CAKEPHP = "cakephp"
    YII = "yii"
    THINKPHP = "thinkphp"
    
    # Micro-frameworks
    SLIM = "slim"
    FATFREE = "fatfree"
    FASTROUTE = "fastroute"
    
    # Full-stack frameworks
    FUEL = "fuel"
    PHALCON = "phalcon"
    PHPIXIE = "phpixie"
    POPPHP = "popphp"
    
    # Enterprise frameworks
    LAMINAS = "laminas"
    ZENDFRAMEWORK = "zendframework"
    
    # CMS frameworks
    DRUPAL = "drupal"
    DRUSH = "drush"
    
    # Unknown/No framework detected
    UNKNOWN = "na"
    
    @property
    def display_name(self) -> str:
        """Get human-readable framework name."""
        display_names = {
            FrameworkType.LARAVEL: "Laravel",
            FrameworkType.SYMFONY: "Symfony",
            FrameworkType.CODEIGNITER: "CodeIgniter",
            FrameworkType.CAKEPHP: "CakePHP",
            FrameworkType.YII: "Yii",
            FrameworkType.THINKPHP: "ThinkPHP",
            FrameworkType.SLIM: "Slim",
            FrameworkType.FATFREE: "Fat-Free Framework",
            FrameworkType.FASTROUTE: "FastRoute",
            FrameworkType.FUEL: "FuelPHP",
            FrameworkType.PHALCON: "Phalcon",
            FrameworkType.PHPIXIE: "PHPixie",
            FrameworkType.POPPHP: "PopPHP",
            FrameworkType.LAMINAS: "Laminas",
            FrameworkType.ZENDFRAMEWORK: "Zend Framework",
            FrameworkType.DRUPAL: "Drupal",
            FrameworkType.DRUSH: "Drush",
            FrameworkType.UNKNOWN: "Unknown"
        }
        return display_names.get(self, "Unknown")
    
    @property
    def description(self) -> str:
        """Get framework description."""
        descriptions = {
            FrameworkType.LARAVEL: "Modern PHP web application framework with elegant syntax",
            FrameworkType.SYMFONY: "High-performance PHP framework for web development",
            FrameworkType.CODEIGNITER: "Lightweight PHP framework for rapid development",
            FrameworkType.CAKEPHP: "Rapid development framework for PHP",
            FrameworkType.YII: "High-performance PHP framework for web applications",
            FrameworkType.THINKPHP: "Fast, simple and elegant PHP framework",
            FrameworkType.SLIM: "Lightweight micro-framework for PHP",
            FrameworkType.FATFREE: "Powerful yet easy-to-use PHP micro-framework",
            FrameworkType.FASTROUTE: "Fast request router for PHP",
            FrameworkType.FUEL: "Simple, flexible, community driven PHP framework",
            FrameworkType.PHALCON: "Full-stack PHP framework delivered as a C-extension",
            FrameworkType.PHPIXIE: "Lightweight PHP framework",
            FrameworkType.POPPHP: "Simple and lightweight PHP framework",
            FrameworkType.LAMINAS: "Enterprise-ready PHP framework",
            FrameworkType.ZENDFRAMEWORK: "Enterprise PHP framework",
            FrameworkType.DRUPAL: "Content management framework",
            FrameworkType.DRUSH: "Command-line shell and scripting interface for Drupal",
            FrameworkType.UNKNOWN: "No framework detected or unknown framework"
        }
        return descriptions.get(self, "No framework detected or unknown framework")
    
    @classmethod
    def from_string(cls, value: str) -> "FrameworkType":
        """Create FrameworkType from string value."""
        try:
            return cls(value.lower().strip())
        except ValueError:
            return cls.UNKNOWN
    
    @classmethod
    def get_all_frameworks(cls) -> list["FrameworkType"]:
        """Get all framework types except UNKNOWN."""
        return [ft for ft in cls if ft != cls.UNKNOWN]
    
    @classmethod
    def get_major_frameworks(cls) -> list["FrameworkType"]:
        """Get major PHP frameworks."""
        return [
            cls.LARAVEL,
            cls.SYMFONY,
            cls.CODEIGNITER,
            cls.CAKEPHP,
            cls.YII,
            cls.THINKPHP
        ]
    
    @classmethod
    def get_micro_frameworks(cls) -> list["FrameworkType"]:
        """Get micro-frameworks."""
        return [
            cls.SLIM,
            cls.FATFREE,
            cls.FASTROUTE
        ]
    
    @classmethod
    def get_enterprise_frameworks(cls) -> list["FrameworkType"]:
        """Get enterprise frameworks."""
        return [
            cls.LAMINAS,
            cls.ZENDFRAMEWORK
        ]
    
    @classmethod
    def get_cms_frameworks(cls) -> list["FrameworkType"]:
        """Get CMS frameworks."""
        return [
            cls.DRUPAL,
            cls.DRUSH
        ]


class FrameworkInfo(BaseModel):
    """
    Information about a PHP framework.
    
    Attributes:
        framework_type: Framework type enum
        name: Human-readable name of the framework
        description: Brief description of the framework
        version: Detected version (if available)
        confidence: Detection confidence score (0-100)
    """
    framework_type: FrameworkType = Field(..., description="Framework type enum")
    name: Optional[str] = Field(None, description="Human-readable framework name")
    description: Optional[str] = Field(None, description="Framework description")
    version: Optional[str] = Field(None, description="Detected framework version")
    confidence: int = Field(100, ge=0, le=100, description="Detection confidence score")
    
    @validator('confidence')
    def validate_confidence(cls, v: int) -> int:
        """Ensure confidence is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError('Confidence must be between 0 and 100')
        return v
    
    @validator('name', pre=True, always=True)
    def set_name_from_framework_type(cls, v: Optional[str], values: Dict) -> str:
        """Set name from framework type if not provided."""
        if v is not None:
            return v
        framework_type = values.get('framework_type')
        if framework_type:
            return framework_type.display_name
        return "Unknown"
    
    @validator('description', pre=True, always=True)
    def set_description_from_framework_type(cls, v: Optional[str], values: Dict) -> str:
        """Set description from framework type if not provided."""
        if v is not None:
            return v
        framework_type = values.get('framework_type')
        if framework_type:
            return framework_type.description
        return "No framework detected or unknown framework"
    
    @property
    def code(self) -> str:
        """Get framework code for backward compatibility."""
        return self.framework_type.value


class DetectionResult(BaseModel):
    """
    Result of framework detection analysis.
    
    Attributes:
        detected_framework: Framework type enum of the detected framework
        detected_name: Human-readable name of detected framework
        scores: Dictionary mapping framework types to detection scores
        project_path: Path to the analyzed project
        detection_time: Timestamp of when detection was performed
        total_frameworks: Total number of frameworks checked
    """
    detected_framework: FrameworkType = Field(..., description="Framework type enum of detected framework")
    detected_name: Optional[str] = Field(None, description="Name of detected framework")
    scores: Dict[FrameworkType, int] = Field(..., description="Detection scores for all frameworks")
    project_path: str = Field(..., description="Path to analyzed project")
    detection_time: datetime = Field(default_factory=datetime.now, description="Detection timestamp")
    total_frameworks: Optional[int] = Field(None, description="Total frameworks checked")
    
    @validator('detected_name', pre=True, always=True)
    def set_detected_name_from_framework_type(cls, v: Optional[str], values: Dict) -> str:
        """Set detected name from framework type if not provided."""
        if v is not None:
            return v
        detected_framework = values.get('detected_framework')
        if detected_framework:
            return detected_framework.display_name
        return "Unknown"
    
    @property
    def is_framework_detected(self) -> bool:
        """Check if a framework was detected."""
        return self.detected_framework != FrameworkType.UNKNOWN
    
    @property
    def confidence_score(self) -> int:
        """Get confidence score for detected framework."""
        return self.scores.get(self.detected_framework, 0)
    
    @property
    def top_frameworks(self, limit: int = 5) -> Dict[FrameworkType, int]:
        """Get top N frameworks by score."""
        sorted_scores = sorted(
            self.scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return dict(sorted_scores[:limit])
    
    @property
    def detected_framework_code(self) -> str:
        """Get framework code for backward compatibility."""
        return self.detected_framework.value


class DetectionConfig(BaseModel):
    """
    Configuration for framework detection.
    
    Attributes:
        check_composer: Whether to check composer files
        check_files: Whether to check file patterns
        check_dependencies: Whether to check dependencies
        max_file_size: Maximum file size to read (in bytes)
        timeout: Detection timeout in seconds
        verbose: Enable verbose logging
    """
    check_composer: bool = Field(True, description="Check composer files")
    check_files: bool = Field(True, description="Check file patterns")
    check_dependencies: bool = Field(True, description="Check dependencies")
    max_file_size: int = Field(1024 * 1024, ge=1024, description="Max file size to read")
    timeout: int = Field(30, ge=1, le=300, description="Detection timeout in seconds")
    verbose: bool = Field(False, description="Enable verbose logging")
    
    @validator('max_file_size')
    def validate_max_file_size(cls, v: int) -> int:
        """Ensure max file size is reasonable."""
        if v < 1024:
            raise ValueError('Max file size must be at least 1KB')
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError('Max file size cannot exceed 100MB')
        return v


class FrameworkMetadata(BaseModel):
    """
    Metadata about framework detection capabilities.
    
    Attributes:
        framework_type: Framework type enum
        detection_methods: List of detection methods used
        file_patterns: File patterns to check
        composer_packages: Composer package names to check
        content_patterns: Content patterns to search for
    """
    framework_type: FrameworkType = Field(..., description="Framework type enum")
    detection_methods: list[str] = Field(default_factory=list, description="Detection methods")
    file_patterns: list[str] = Field(default_factory=list, description="File patterns to check")
    composer_packages: list[str] = Field(default_factory=list, description="Composer packages")
    content_patterns: list[str] = Field(default_factory=list, description="Content patterns")
    
    @property
    def framework_code(self) -> str:
        """Get framework code for backward compatibility."""
        return self.framework_type.value 