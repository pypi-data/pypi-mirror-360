# FrameworkType Enum

The `FrameworkType` enum provides type-safe framework identification and categorization for the PHP Framework Detector.

## Overview

The `FrameworkType` enum defines all supported PHP frameworks with their identifiers, display names, and descriptions. This provides better type safety, consistency, and easier framework categorization.

## Available Framework Types

### Major PHP Frameworks
- `LARAVEL` - Laravel
- `SYMFONY` - Symfony  
- `CODEIGNITER` - CodeIgniter
- `CAKEPHP` - CakePHP
- `YII` - Yii
- `THINKPHP` - ThinkPHP

### Micro-frameworks
- `SLIM` - Slim
- `FATFREE` - Fat-Free Framework
- `FASTROUTE` - FastRoute

### Full-stack Frameworks
- `FUEL` - FuelPHP
- `PHALCON` - Phalcon
- `PHPIXIE` - PHPixie
- `POPPHP` - PopPHP

### Enterprise Frameworks
- `LAMINAS` - Laminas
- `ZENDFRAMEWORK` - Zend Framework

### CMS Frameworks
- `DRUPAL` - Drupal
- `DRUSH` - Drush

### Special Values
- `UNKNOWN` - No framework detected or unknown framework

## Basic Usage

### Creating FrameworkType from String

```python
from php_framework_detector.core.models import FrameworkType

# Create from string
laravel = FrameworkType.from_string("laravel")
print(laravel)  # FrameworkType.LARAVEL

# Handle unknown frameworks
unknown = FrameworkType.from_string("unknown_framework")
print(unknown)  # FrameworkType.UNKNOWN
```

### Accessing Properties

```python
laravel = FrameworkType.LARAVEL

print(laravel.value)           # "laravel"
print(laravel.display_name)    # "Laravel"
print(laravel.description)     # "Modern PHP web application framework with elegant syntax"
```

### Framework Categorization

```python
# Get all frameworks by category
major_frameworks = FrameworkType.get_major_frameworks()
micro_frameworks = FrameworkType.get_micro_frameworks()
enterprise_frameworks = FrameworkType.get_enterprise_frameworks()
cms_frameworks = FrameworkType.get_cms_frameworks()

# Get all frameworks (excluding UNKNOWN)
all_frameworks = FrameworkType.get_all_frameworks()
```

## Integration with Models

### FrameworkInfo

```python
from php_framework_detector.core.models import FrameworkInfo, FrameworkType

# Create FrameworkInfo with enum
info = FrameworkInfo(
    framework_type=FrameworkType.LARAVEL,
    version="10.0.0",
    confidence=95
)

print(info.name)        # "Laravel" (auto-generated from enum)
print(info.code)        # "laravel" (backward compatibility)
print(info.description) # Auto-generated from enum
```

### DetectionResult

```python
from php_framework_detector.core.models import DetectionResult, FrameworkType

# Create detection scores
scores = {
    FrameworkType.LARAVEL: 95,
    FrameworkType.SYMFONY: 20,
    FrameworkType.CODEIGNITER: 5,
    # ... other frameworks
}

# Create DetectionResult
result = DetectionResult(
    detected_framework=FrameworkType.LARAVEL,
    scores=scores,
    project_path="/path/to/project"
)

print(result.detected_name)           # "Laravel"
print(result.detected_framework)      # FrameworkType.LARAVEL
print(result.detected_framework_code) # "laravel" (backward compatibility)
print(result.is_framework_detected)   # True
```

### FrameworkMetadata

```python
from php_framework_detector.core.models import FrameworkMetadata, FrameworkType

metadata = FrameworkMetadata(
    framework_type=FrameworkType.LARAVEL,
    detection_methods=["file_patterns", "composer_packages"],
    file_patterns=["artisan", "app/"],
    composer_packages=["laravel/framework"],
    content_patterns=["Laravel Framework"]
)

print(metadata.framework_code)  # "laravel" (backward compatibility)
```

## Async Detection

The async detection methods now return results with `FrameworkType` keys:

```python
from php_framework_detector.core.factory import FrameworkDetectorFactory

# Async detection returns FrameworkType -> score mapping
scores = await FrameworkDetectorFactory.detect_all_frameworks_async("/path/to/project")

for framework_type, score in scores.items():
    print(f"{framework_type.display_name}: {score}")
```

## Backward Compatibility

All models maintain backward compatibility by providing properties that return string values:

- `FrameworkInfo.code` - Returns the framework code string
- `DetectionResult.detected_framework_code` - Returns the detected framework code string
- `FrameworkMetadata.framework_code` - Returns the framework code string

## Benefits

1. **Type Safety**: Compile-time checking for framework types
2. **Consistency**: Centralized framework definitions
3. **Categorization**: Easy framework grouping by type
4. **Maintainability**: Single source of truth for framework information
5. **IDE Support**: Better autocomplete and error detection
6. **Documentation**: Self-documenting code with clear framework types

## Migration Guide

### From String-based to Enum-based

**Before:**
```python
detected_framework = "laravel"
if detected_framework == "laravel":
    # handle Laravel
```

**After:**
```python
detected_framework = FrameworkType.LARAVEL
if detected_framework == FrameworkType.LARAVEL:
    # handle Laravel
```

### From String Dictionaries to Enum Dictionaries

**Before:**
```python
scores = {"laravel": 95, "symfony": 20}
```

**After:**
```python
scores = {FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 20}
```

## Example Usage

See `examples/enum_usage_example.py` for a comprehensive demonstration of all enum features. 