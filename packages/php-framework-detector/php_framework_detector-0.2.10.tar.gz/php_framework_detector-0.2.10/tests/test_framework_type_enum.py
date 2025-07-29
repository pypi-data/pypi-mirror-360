#!/usr/bin/env python3
"""
Tests for FrameworkType enum functionality.

This module tests the FrameworkType enum and its integration
with the detection models.
"""

import pytest
from php_framework_detector.core.models import (
    FrameworkType, FrameworkInfo, DetectionResult, FrameworkMetadata
)


class TestFrameworkType:
    """Test FrameworkType enum functionality."""
    
    def test_enum_creation(self):
        """Test creating FrameworkType enums."""
        laravel = FrameworkType.LARAVEL
        assert laravel.value == "laravel"
        assert laravel.display_name == "Laravel"
        assert "elegant syntax" in laravel.description
        
        unknown = FrameworkType.UNKNOWN
        assert unknown.value == "na"
        assert unknown.display_name == "Unknown"
    
    def test_from_string(self):
        """Test creating FrameworkType from string."""
        # Valid frameworks
        assert FrameworkType.from_string("laravel") == FrameworkType.LARAVEL
        assert FrameworkType.from_string("LARAVEL") == FrameworkType.LARAVEL
        assert FrameworkType.from_string("  laravel  ") == FrameworkType.LARAVEL
        
        # Unknown frameworks
        assert FrameworkType.from_string("unknown_framework") == FrameworkType.UNKNOWN
        assert FrameworkType.from_string("") == FrameworkType.UNKNOWN
        assert FrameworkType.from_string("   ") == FrameworkType.UNKNOWN
    
    def test_framework_categories(self):
        """Test framework categorization methods."""
        major_frameworks = FrameworkType.get_major_frameworks()
        assert FrameworkType.LARAVEL in major_frameworks
        assert FrameworkType.SYMFONY in major_frameworks
        assert FrameworkType.UNKNOWN not in major_frameworks
        
        micro_frameworks = FrameworkType.get_micro_frameworks()
        assert FrameworkType.SLIM in micro_frameworks
        assert FrameworkType.FATFREE in micro_frameworks
        assert FrameworkType.LARAVEL not in micro_frameworks
        
        enterprise_frameworks = FrameworkType.get_enterprise_frameworks()
        assert FrameworkType.LAMINAS in enterprise_frameworks
        assert FrameworkType.ZENDFRAMEWORK in enterprise_frameworks
        
        cms_frameworks = FrameworkType.get_cms_frameworks()
        assert FrameworkType.DRUPAL in cms_frameworks
        assert FrameworkType.DRUSH in cms_frameworks
        
        all_frameworks = FrameworkType.get_all_frameworks()
        assert FrameworkType.UNKNOWN not in all_frameworks
        assert len(all_frameworks) == len(FrameworkType) - 1  # Excluding UNKNOWN


class TestFrameworkInfo:
    """Test FrameworkInfo with FrameworkType enum."""
    
    def test_framework_info_creation(self):
        """Test creating FrameworkInfo with enum."""
        info = FrameworkInfo(
            framework_type=FrameworkType.LARAVEL,
            version="10.0.0",
            confidence=95
        )
        
        assert info.framework_type == FrameworkType.LARAVEL
        assert info.name == "Laravel"  # Auto-generated from enum
        assert info.code == "laravel"  # Backward compatibility
        assert "elegant syntax" in info.description  # Auto-generated from enum
        assert info.version == "10.0.0"
        assert info.confidence == 95
    
    def test_framework_info_custom_values(self):
        """Test FrameworkInfo with custom name and description."""
        info = FrameworkInfo(
            framework_type=FrameworkType.SYMFONY,
            name="Custom Symfony",
            description="Custom description",
            confidence=88
        )
        
        assert info.framework_type == FrameworkType.SYMFONY
        assert info.name == "Custom Symfony"  # Custom value used
        assert info.description == "Custom description"  # Custom value used
        assert info.code == "symfony"  # Backward compatibility


class TestDetectionResult:
    """Test DetectionResult with FrameworkType enum."""
    
    def test_detection_result_creation(self):
        """Test creating DetectionResult with enum."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20,
            FrameworkType.CODEIGNITER: 5,
            FrameworkType.UNKNOWN: 0
        }
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        assert result.detected_framework == FrameworkType.LARAVEL
        assert result.detected_name == "Laravel"  # Auto-generated from enum
        assert result.detected_framework_code == "laravel"  # Backward compatibility
        assert result.is_framework_detected is True
        assert result.confidence_score == 95
        assert result.scores == scores
    
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
    
    def test_top_frameworks(self):
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
        # Should return all frameworks sorted by score
        assert len(top_frameworks) == 4
        assert list(top_frameworks.keys())[0] == FrameworkType.LARAVEL
        assert top_frameworks[FrameworkType.LARAVEL] == 95


class TestFrameworkMetadata:
    """Test FrameworkMetadata with FrameworkType enum."""
    
    def test_framework_metadata_creation(self):
        """Test creating FrameworkMetadata with enum."""
        metadata = FrameworkMetadata(
            framework_type=FrameworkType.LARAVEL,
            detection_methods=["file_patterns", "composer_packages"],
            file_patterns=["artisan", "app/"],
            composer_packages=["laravel/framework"],
            content_patterns=["Laravel Framework"]
        )
        
        assert metadata.framework_type == FrameworkType.LARAVEL
        assert metadata.framework_code == "laravel"  # Backward compatibility
        assert metadata.detection_methods == ["file_patterns", "composer_packages"]
        assert metadata.file_patterns == ["artisan", "app/"]
        assert metadata.composer_packages == ["laravel/framework"]
        assert metadata.content_patterns == ["Laravel Framework"]


class TestEnumIntegration:
    """Test integration between enum and other components."""
    
    def test_enum_comparison(self):
        """Test enum comparison operations."""
        laravel1 = FrameworkType.LARAVEL
        laravel2 = FrameworkType.from_string("laravel")
        symfony = FrameworkType.SYMFONY
        
        assert laravel1 == laravel2
        assert laravel1 != symfony
        assert laravel1 in [FrameworkType.LARAVEL, FrameworkType.SYMFONY]
    
    def test_enum_in_dict(self):
        """Test using enum as dictionary keys."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20
        }
        
        assert scores[FrameworkType.LARAVEL] == 95
        assert scores[FrameworkType.SYMFONY] == 20
        assert FrameworkType.CODEIGNITER not in scores
    
    def test_enum_sorting(self):
        """Test sorting frameworks by enum."""
        frameworks = [
            FrameworkType.SYMFONY,
            FrameworkType.LARAVEL,
            FrameworkType.CODEIGNITER
        ]
        
        sorted_frameworks = sorted(frameworks, key=lambda x: x.value)
        assert sorted_frameworks[0] == FrameworkType.CODEIGNITER
        assert sorted_frameworks[1] == FrameworkType.LARAVEL
        assert sorted_frameworks[2] == FrameworkType.SYMFONY


if __name__ == "__main__":
    pytest.main([__file__]) 