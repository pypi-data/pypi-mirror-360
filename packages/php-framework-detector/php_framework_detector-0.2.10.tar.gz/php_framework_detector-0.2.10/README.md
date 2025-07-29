# PHP Framework Detector

Detect PHP frameworks in any project directory with a modern, async Python tool. Supports 17+ frameworks, structured logging, and a user-friendly CLI.

## Features

- **Async detection** for high performance
- **17+ frameworks** supported
- **Structured logging** (structlog)
- **Type safety** (Pydantic)
- **Modern CLI** (Rich)
- **Configurable & extensible**

## Supported Frameworks

Laravel, Symfony, CodeIgniter, CakePHP, Yii, ThinkPHP, Slim, Fuel, Phalcon, Laminas, Zend Framework, Drupal, Drush, Fat-Free, PHPixie, PopPHP, FastRoute

## Installation

```bash
# Recommended (uv)
uv add php-framework-detector

# Or pip
pip install php-framework-detector
```

## Usage

### CLI

```bash
php-framework-detector /path/to/php/project [--json] [--all] [--verbose]
php-framework-detector list-frameworks
php-framework-detector version
```

### Docker

```bash
docker run --rm -it -v /path/to/php/project:/var/www/html ghcr.io/wangyihang/php-framework-detector:main detect /var/www/html
```

### Python API

```python
import asyncio
from php_framework_detector import FrameworkDetectorFactory, DetectionConfig

async def main():
    config = DetectionConfig(timeout=30, max_file_size=1024*1024, verbose=True)
    result = await FrameworkDetectorFactory.detect_all_frameworks_async("/path/to/php/project", config)
    print(result)

asyncio.run(main())
```

## Configuration Example

```python
from php_framework_detector import DetectionConfig
config = DetectionConfig(
    check_composer=True,
    check_files=True,
    check_dependencies=True,
    max_file_size=1024*1024,
    timeout=30,
    verbose=False
)
```

## Architecture

- **FrameworkDetector**: Base class for detectors
- **FrameworkDetectorFactory**: Detector management
- **DetectionConfig**: Config model
- **DetectionResult**: Structured results
- **Custom Exceptions**: Error handling

Detection strategies:
- File pattern matching
- Composer dependency analysis
- Content pattern matching
- Priority-based scoring

## Add a New Framework

1. Create a detector in `frameworks/`:

```python
from ..core.detector import FrameworkDetector
class MyFrameworkDetector(FrameworkDetector):
    name = "myframework"
    display_name = "My Framework"
    def detect(self):
        return self._check_path_patterns(["myframework.php"])
    async def _detect_async_impl(self):
        return 50 if await self._check_path_patterns_async(["myframework.php"]) else 0
```

2. Register it in `frameworks/__init__.py`:

```python
from .myframework import MyFrameworkDetector
FrameworkDetectorFactory.register_detector(MyFrameworkDetector)
```

## Development

```bash
git clone https://github.com/your-username/php-framework-detector.git
cd php-framework-detector
uv sync
uv sync --extra dev
pytest
black .
isort .
mypy .
ruff check .
```

## Testing

```bash
pytest
pytest --cov=php_framework_detector
pytest --asyncio-mode=auto
```

## Contributing

- Fork & branch
- Add features/tests
- Ensure all tests pass
- Submit a pull request

## License

MIT License. See LICENSE.

## Changelog

### v0.2.0
- Refactored, async, structured logging, type safety, improved CLI, error handling, better detection

### v0.1.0
- Initial release
