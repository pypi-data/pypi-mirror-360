"""
Tests for core models.

This module tests the core data models including DetectionConfig,
FrameworkMetadata, and related validation logic.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from php_framework_detector.core.models import (
    DetectionConfig,
    FrameworkMetadata,
    FrameworkInfo,
    DetectionResult,
    FrameworkType
)


class TestDetectionConfig:
    """Test DetectionConfig model."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DetectionConfig()
        
        assert config.check_composer is True
        assert config.check_files is True
        assert config.check_dependencies is True
        assert config.max_file_size == 1024 * 1024
        assert config.timeout == 30
        assert config.verbose is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = DetectionConfig(
            check_composer=False,
            check_files=False,
            check_dependencies=False,
            max_file_size=2048,
            timeout=60,
            verbose=True
        )
        
        assert config.check_composer is False
        assert config.check_files is False
        assert config.check_dependencies is False
        assert config.max_file_size == 2048
        assert config.timeout == 60
        assert config.verbose is True
    
    def test_max_file_size_validation(self):
        """Test max_file_size validation."""
        # Should accept valid values
        config = DetectionConfig(max_file_size=1024)
        assert config.max_file_size == 1024
        
        # Should reject values below minimum
        with pytest.raises(ValidationError):
            DetectionConfig(max_file_size=512)
        
        # Should accept values at minimum
        config = DetectionConfig(max_file_size=1024)
        assert config.max_file_size == 1024
    
    def test_timeout_validation(self):
        """Test timeout validation."""
        # Should accept valid values
        config = DetectionConfig(timeout=15)
        assert config.timeout == 15
        
        # Should reject values below minimum
        with pytest.raises(ValidationError):
            DetectionConfig(timeout=0)
        
        # Should reject values above maximum
        with pytest.raises(ValidationError):
            DetectionConfig(timeout=301)
        
        # Should accept boundary values
        config = DetectionConfig(timeout=1)
        assert config.timeout == 1
        
        config = DetectionConfig(timeout=300)
        assert config.timeout == 300


class TestFrameworkMetadata:
    """Test FrameworkMetadata model."""
    
    def test_framework_metadata_creation(self):
        """Test creating FrameworkMetadata."""
        metadata = FrameworkMetadata(
            framework_type=FrameworkType.LARAVEL,
            detection_methods=["file_patterns", "composer_packages"],
            file_patterns=["artisan", "app/"],
            composer_packages=["laravel/framework"],
            content_patterns=["Laravel Framework", "Illuminate\\"]
        )
        
        assert metadata.framework_type == FrameworkType.LARAVEL
        assert metadata.framework_code == "laravel"
        assert metadata.detection_methods == ["file_patterns", "composer_packages"]
        assert metadata.file_patterns == ["artisan", "app/"]
        assert metadata.composer_packages == ["laravel/framework"]
        assert metadata.content_patterns == ["Laravel Framework", "Illuminate\\"]
    
    def test_framework_metadata_defaults(self):
        """Test FrameworkMetadata with default values."""
        metadata = FrameworkMetadata(framework_type=FrameworkType.SYMFONY)
        
        assert metadata.framework_type == FrameworkType.SYMFONY
        assert metadata.framework_code == "symfony"
        assert metadata.detection_methods == []
        assert metadata.file_patterns == []
        assert metadata.composer_packages == []
        assert metadata.content_patterns == []
    
    def test_framework_code_property(self):
        """Test framework_code property for different frameworks."""
        laravel_metadata = FrameworkMetadata(framework_type=FrameworkType.LARAVEL)
        assert laravel_metadata.framework_code == "laravel"
        
        symfony_metadata = FrameworkMetadata(framework_type=FrameworkType.SYMFONY)
        assert symfony_metadata.framework_code == "symfony"
        
        unknown_metadata = FrameworkMetadata(framework_type=FrameworkType.UNKNOWN)
        assert unknown_metadata.framework_code == "na"


class TestFrameworkInfo:
    """Test FrameworkInfo model."""
    
    def test_framework_info_creation(self):
        """Test creating FrameworkInfo."""
        info = FrameworkInfo(
            framework_type=FrameworkType.LARAVEL,
            version="10.0.0",
            confidence=95
        )
        
        assert info.framework_type == FrameworkType.LARAVEL
        assert info.name == "Laravel"  # Auto-generated from enum
        assert info.description == "Modern PHP web application framework with elegant syntax"
        assert info.version == "10.0.0"
        assert info.confidence == 95
        assert info.code == "laravel"
    
    def test_framework_info_custom_values(self):
        """Test FrameworkInfo with custom name and description."""
        info = FrameworkInfo(
            framework_type=FrameworkType.SYMFONY,
            name="Custom Symfony",
            description="Custom description",
            version="6.0.0",
            confidence=88
        )
        
        assert info.framework_type == FrameworkType.SYMFONY
        assert info.name == "Custom Symfony"
        assert info.description == "Custom description"
        assert info.version == "6.0.0"
        assert info.confidence == 88
        assert info.code == "symfony"
    
    def test_confidence_validation(self):
        """Test confidence score validation."""
        # Should accept valid values
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=50)
        assert info.confidence == 50
        
        # Should reject values below 0
        with pytest.raises(ValidationError):
            FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=-1)
        
        # Should reject values above 100
        with pytest.raises(ValidationError):
            FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=101)
        
        # Should accept boundary values
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=0)
        assert info.confidence == 0
        
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=100)
        assert info.confidence == 100
    
    def test_auto_generated_values(self):
        """Test auto-generated name and description."""
        # Test with unknown framework
        info = FrameworkInfo(framework_type=FrameworkType.UNKNOWN)
        assert info.name == "Unknown"
        assert info.description == "No framework detected or unknown framework"
        assert info.code == "na"
        
        # Test with known framework
        info = FrameworkInfo(framework_type=FrameworkType.CODEIGNITER)
        assert info.name == "CodeIgniter"
        assert "Lightweight PHP framework" in info.description
        assert info.code == "codeigniter"


class TestDetectionResult:
    """Test DetectionResult model."""
    
    def test_detection_result_creation(self):
        """Test creating DetectionResult."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20,
            FrameworkType.UNKNOWN: 0
        }
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        assert result.detected_framework == FrameworkType.LARAVEL
        assert result.detected_name == "Laravel"
        assert result.detected_framework_code == "laravel"
        assert result.scores == scores
        assert result.project_path == "/path/to/project"
        assert result.is_framework_detected is True
        assert result.confidence_score == 95
        assert isinstance(result.detection_time, datetime)
        assert result.total_frameworks is None
    
    def test_detection_result_unknown(self):
        """Test DetectionResult with unknown framework."""
        scores = {FrameworkType.UNKNOWN: 0}
        
        result = DetectionResult(
            detected_framework=FrameworkType.UNKNOWN,
            scores=scores,
            project_path="/path/to/project"
        )
        
        assert result.detected_framework == FrameworkType.UNKNOWN
        assert result.detected_name == "Unknown"
        assert result.detected_framework_code == "na"
        assert result.is_framework_detected is False
        assert result.confidence_score == 0
    
    def test_top_frameworks_property(self):
        """Test top_frameworks property."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20,
            FrameworkType.CODEIGNITER: 5,
            FrameworkType.CAKEPHP: 0
        }
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        top_frameworks = result.top_frameworks
        # Should return all frameworks sorted by score (descending)
        assert len(top_frameworks) == 4
        framework_list = list(top_frameworks.keys())
        assert framework_list[0] == FrameworkType.LARAVEL
        assert framework_list[1] == FrameworkType.SYMFONY
        assert framework_list[2] == FrameworkType.CODEIGNITER
        assert framework_list[3] == FrameworkType.CAKEPHP
        
        assert top_frameworks[FrameworkType.LARAVEL] == 95
        assert top_frameworks[FrameworkType.SYMFONY] == 20
        assert top_frameworks[FrameworkType.CODEIGNITER] == 5
        assert top_frameworks[FrameworkType.CAKEPHP] == 0
    
    def test_top_frameworks_with_limit(self):
        """Test top_frameworks property with custom limit."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20,
            FrameworkType.CODEIGNITER: 5,
            FrameworkType.CAKEPHP: 0
        }
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        # Test with limit=2
        top_frameworks = result.top_frameworks(limit=2)
        assert len(top_frameworks) == 2
        framework_list = list(top_frameworks.keys())
        assert framework_list[0] == FrameworkType.LARAVEL
        assert framework_list[1] == FrameworkType.SYMFONY
    
    def test_custom_detection_time(self):
        """Test DetectionResult with custom detection time."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        scores = {FrameworkType.LARAVEL: 95}
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project",
            detection_time=custom_time
        )
        
        assert result.detection_time == custom_time
    
    def test_total_frameworks(self):
        """Test DetectionResult with total_frameworks."""
        scores = {FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 20}
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project",
            total_frameworks=15
        )
        
        assert result.total_frameworks == 15


class TestModelIntegration:
    """Test integration between different models."""
    
    def test_framework_info_from_detection_result(self):
        """Test creating FrameworkInfo from DetectionResult."""
        scores = {FrameworkType.LARAVEL: 95}
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        info = FrameworkInfo(
            framework_type=result.detected_framework,
            confidence=result.confidence_score
        )
        
        assert info.framework_type == FrameworkType.LARAVEL
        assert info.confidence == 95
        assert info.name == "Laravel"
    
    def test_metadata_from_framework_info(self):
        """Test creating FrameworkMetadata from FrameworkInfo."""
        info = FrameworkInfo(
            framework_type=FrameworkType.LARAVEL,
            version="10.0.0",
            confidence=95
        )
        
        metadata = FrameworkMetadata(
            framework_type=info.framework_type,
            detection_methods=["file_patterns"],
            file_patterns=["artisan"]
        )
        
        assert metadata.framework_type == info.framework_type
        assert metadata.framework_code == info.code 