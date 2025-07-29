#!/usr/bin/env python3
"""
Simple test for FrameworkType enum functionality.

This script tests the FrameworkType enum without requiring pytest.
"""

import sys
import traceback
from php_framework_detector.core.models import (
    FrameworkType, FrameworkInfo, DetectionResult, FrameworkMetadata
)


def test_enum_basics():
    """Test basic enum functionality."""
    print("Testing enum basics...")
    
    # Test enum creation
    laravel = FrameworkType.LARAVEL
    assert laravel.value == "laravel"
    assert laravel.display_name == "Laravel"
    assert "elegant syntax" in laravel.description
    
    unknown = FrameworkType.UNKNOWN
    assert unknown.value == "na"
    assert unknown.display_name == "Unknown"
    
    print("✓ Enum basics passed")


def test_from_string():
    """Test creating enum from string."""
    print("Testing from_string...")
    
    # Valid frameworks
    assert FrameworkType.from_string("laravel") == FrameworkType.LARAVEL
    assert FrameworkType.from_string("LARAVEL") == FrameworkType.LARAVEL
    assert FrameworkType.from_string("  laravel  ") == FrameworkType.LARAVEL
    
    # Unknown frameworks
    assert FrameworkType.from_string("unknown_framework") == FrameworkType.UNKNOWN
    assert FrameworkType.from_string("") == FrameworkType.UNKNOWN
    assert FrameworkType.from_string("   ") == FrameworkType.UNKNOWN
    
    print("✓ from_string passed")


def test_framework_categories():
    """Test framework categorization."""
    print("Testing framework categories...")
    
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
    
    print("✓ Framework categories passed")


def test_framework_info():
    """Test FrameworkInfo with enum."""
    print("Testing FrameworkInfo...")
    
    # Test auto-generation
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
    
    # Test custom values
    custom_info = FrameworkInfo(
        framework_type=FrameworkType.SYMFONY,
        name="Custom Symfony",
        description="Custom description",
        confidence=88
    )
    
    assert custom_info.framework_type == FrameworkType.SYMFONY
    assert custom_info.name == "Custom Symfony"  # Custom value used
    assert custom_info.description == "Custom description"  # Custom value used
    assert custom_info.code == "symfony"  # Backward compatibility
    
    print("✓ FrameworkInfo passed")


def test_detection_result():
    """Test DetectionResult with enum."""
    print("Testing DetectionResult...")
    
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
    
    # Test unknown framework
    unknown_result = DetectionResult(
        detected_framework=FrameworkType.UNKNOWN,
        scores={FrameworkType.UNKNOWN: 0},
        project_path="/path/to/project"
    )
    
    assert unknown_result.detected_framework == FrameworkType.UNKNOWN
    assert unknown_result.detected_name == "Unknown"
    assert unknown_result.detected_framework_code == "na"
    assert unknown_result.is_framework_detected is False
    assert unknown_result.confidence_score == 0
    
    print("✓ DetectionResult passed")


def test_framework_metadata():
    """Test FrameworkMetadata with enum."""
    print("Testing FrameworkMetadata...")
    
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
    
    print("✓ FrameworkMetadata passed")


def test_enum_integration():
    """Test enum integration features."""
    print("Testing enum integration...")
    
    # Test comparison
    laravel1 = FrameworkType.LARAVEL
    laravel2 = FrameworkType.from_string("laravel")
    symfony = FrameworkType.SYMFONY
    
    assert laravel1 == laravel2
    assert laravel1 != symfony
    assert laravel1 in [FrameworkType.LARAVEL, FrameworkType.SYMFONY]
    
    # Test as dictionary keys
    scores = {
        FrameworkType.LARAVEL: 95,
        FrameworkType.SYMFONY: 20
    }
    
    assert scores[FrameworkType.LARAVEL] == 95
    assert scores[FrameworkType.SYMFONY] == 20
    assert FrameworkType.CODEIGNITER not in scores
    
    # Test sorting
    frameworks = [
        FrameworkType.SYMFONY,
        FrameworkType.LARAVEL,
        FrameworkType.CODEIGNITER
    ]
    
    sorted_frameworks = sorted(frameworks, key=lambda x: x.value)
    assert sorted_frameworks[0] == FrameworkType.CODEIGNITER
    assert sorted_frameworks[1] == FrameworkType.LARAVEL
    assert sorted_frameworks[2] == FrameworkType.SYMFONY
    
    print("✓ Enum integration passed")


def main():
    """Run all tests."""
    print("FrameworkType Enum Tests")
    print("=" * 40)
    
    tests = [
        test_enum_basics,
        test_from_string,
        test_framework_categories,
        test_framework_info,
        test_detection_result,
        test_framework_metadata,
        test_enum_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 