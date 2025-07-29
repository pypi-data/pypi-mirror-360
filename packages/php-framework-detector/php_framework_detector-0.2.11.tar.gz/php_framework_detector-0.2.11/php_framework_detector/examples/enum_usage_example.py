#!/usr/bin/env python3
"""
Example demonstrating the usage of FrameworkType enum.

This example shows how to use the new FrameworkType enum for
type-safe framework detection and categorization.
"""

import asyncio
from pathlib import Path
from typing import Dict

from php_framework_detector.core.models import FrameworkType, DetectionResult, FrameworkInfo
from php_framework_detector.core.factory import FrameworkDetectorFactory
from php_framework_detector.core.detector import FrameworkDetector


def demonstrate_enum_basics():
    """Demonstrate basic enum usage."""
    print("=== FrameworkType Enum Basics ===\n")
    
    # Create enum from string
    laravel = FrameworkType.from_string("laravel")
    print(f"Laravel enum: {laravel}")
    print(f"Laravel value: {laravel.value}")
    print(f"Laravel display name: {laravel.display_name}")
    print(f"Laravel description: {laravel.description}")
    print()
    
    # Handle unknown framework
    unknown = FrameworkType.from_string("unknown_framework")
    print(f"Unknown framework: {unknown}")
    print(f"Unknown display name: {unknown.display_name}")
    print()
    
    # Get framework categories
    print("Major frameworks:")
    for framework in FrameworkType.get_major_frameworks():
        print(f"  - {framework.display_name} ({framework.value})")
    print()
    
    print("Micro-frameworks:")
    for framework in FrameworkType.get_micro_frameworks():
        print(f"  - {framework.display_name} ({framework.value})")
    print()
    
    print("Enterprise frameworks:")
    for framework in FrameworkType.get_enterprise_frameworks():
        print(f"  - {framework.display_name} ({framework.value})")
    print()
    
    print("CMS frameworks:")
    for framework in FrameworkType.get_cms_frameworks():
        print(f"  - {framework.display_name} ({framework.value})")
    print()


def demonstrate_framework_info():
    """Demonstrate FrameworkInfo with enum."""
    print("=== FrameworkInfo with Enum ===\n")
    
    # Create FrameworkInfo with enum
    laravel_info = FrameworkInfo(
        framework_type=FrameworkType.LARAVEL,
        version="10.0.0",
        confidence=95
    )
    
    print(f"Framework: {laravel_info.name}")
    print(f"Code: {laravel_info.code}")
    print(f"Type: {laravel_info.framework_type}")
    print(f"Description: {laravel_info.description}")
    print(f"Version: {laravel_info.version}")
    print(f"Confidence: {laravel_info.confidence}")
    print()
    
    # Create with custom name and description
    custom_info = FrameworkInfo(
        framework_type=FrameworkType.SYMFONY,
        name="Custom Symfony Name",
        description="Custom description",
        confidence=88
    )
    
    print(f"Custom Framework: {custom_info.name}")
    print(f"Custom Description: {custom_info.description}")
    print()


def demonstrate_detection_result():
    """Demonstrate DetectionResult with enum."""
    print("=== DetectionResult with Enum ===\n")
    
    # Create sample detection scores
    scores = {
        FrameworkType.LARAVEL: 95,
        FrameworkType.SYMFONY: 20,
        FrameworkType.CODEIGNITER: 5,
        FrameworkType.CAKEPHP: 0,
        FrameworkType.YII: 0,
        FrameworkType.THINKPHP: 0,
        FrameworkType.SLIM: 0,
        FrameworkType.FATFREE: 0,
        FrameworkType.FASTROUTE: 0,
        FrameworkType.FUEL: 0,
        FrameworkType.PHALCON: 0,
        FrameworkType.PHPIXIE: 0,
        FrameworkType.POPPHP: 0,
        FrameworkType.LAMINAS: 0,
        FrameworkType.ZENDFRAMEWORK: 0,
        FrameworkType.DRUPAL: 0,
        FrameworkType.DRUSH: 0,
        FrameworkType.UNKNOWN: 0
    }
    
    # Create DetectionResult
    result = DetectionResult(
        detected_framework=FrameworkType.LARAVEL,
        scores=scores,
        project_path="/path/to/laravel/project"
    )
    
    print(f"Detected Framework: {result.detected_name}")
    print(f"Framework Type: {result.detected_framework}")
    print(f"Framework Code: {result.detected_framework_code}")
    print(f"Is Framework Detected: {result.is_framework_detected}")
    print(f"Confidence Score: {result.confidence_score}")
    print()
    
    print("Top 3 frameworks:")
    top_frameworks = result.top_frameworks
    # Get top 3 by sorting and taking first 3
    sorted_frameworks = sorted(top_frameworks.items(), key=lambda x: x[1], reverse=True)[:3]
    for framework, score in sorted_frameworks:
        print(f"  - {framework.display_name}: {score}")
    print()


async def demonstrate_async_detection():
    """Demonstrate async detection with enum results."""
    print("=== Async Detection with Enum ===\n")
    
    # Create a temporary project path for demonstration
    project_path = Path("/tmp/demo_project")
    project_path.mkdir(exist_ok=True)
    
    try:
        # Get detection results
        scores = await FrameworkDetectorFactory.detect_all_frameworks_async(
            str(project_path)
        )
        
        print("Detection results by framework type:")
        for framework_type, score in scores.items():
            print(f"  - {framework_type.display_name}: {score}")
        print()
        
        # Find the highest scoring framework
        if scores:
            best_framework = max(scores.items(), key=lambda x: x[1])
            print(f"Best match: {best_framework[0].display_name} (score: {best_framework[1]})")
        
    except Exception as e:
        print(f"Detection failed: {e}")
    finally:
        # Clean up
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)


def demonstrate_framework_categorization():
    """Demonstrate framework categorization."""
    print("=== Framework Categorization ===\n")
    
    # Categorize frameworks by type
    categories = {
        "Major Frameworks": FrameworkType.get_major_frameworks(),
        "Micro-frameworks": FrameworkType.get_micro_frameworks(),
        "Enterprise": FrameworkType.get_enterprise_frameworks(),
        "CMS": FrameworkType.get_cms_frameworks(),
        "Full-stack": [
            FrameworkType.FUEL,
            FrameworkType.PHALCON,
            FrameworkType.PHPIXIE,
            FrameworkType.POPPHP
        ]
    }
    
    for category_name, frameworks in categories.items():
        print(f"{category_name}:")
        for framework in frameworks:
            print(f"  - {framework.display_name}")
        print()


def main():
    """Run all demonstrations."""
    print("FrameworkType Enum Usage Examples\n")
    print("=" * 50)
    
    # Run demonstrations
    demonstrate_enum_basics()
    demonstrate_framework_info()
    demonstrate_detection_result()
    demonstrate_framework_categorization()
    
    # Run async demonstration
    print("Running async detection demonstration...")
    asyncio.run(demonstrate_async_detection())
    
    print("\n" + "=" * 50)
    print("All demonstrations completed!")


if __name__ == "__main__":
    main() 