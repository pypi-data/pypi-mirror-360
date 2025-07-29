"""
Pytest configuration and fixtures for PHP Framework Detector tests.

This module provides common fixtures and configuration for all tests.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from php_framework_detector.core.models import DetectionConfig, FrameworkType
from php_framework_detector.core.factory import FrameworkDetectorFactory


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing project files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_composer_json() -> Dict[str, any]:
    """Sample composer.json content for testing."""
    return {
        "name": "test/project",
        "description": "Test project",
        "type": "project",
        "require": {
            "php": ">=8.0",
            "laravel/framework": "^10.0"
        },
        "require-dev": {
            "phpunit/phpunit": "^10.0"
        },
        "autoload": {
            "psr-4": {
                "App\\": "app/"
            }
        }
    }


@pytest.fixture
def sample_composer_lock() -> Dict[str, any]:
    """Sample composer.lock content for testing."""
    return {
        "packages": [
            {
                "name": "laravel/framework",
                "version": "10.0.0",
                "description": "The Laravel framework."
            }
        ],
        "packages-dev": [
            {
                "name": "phpunit/phpunit",
                "version": "10.0.0",
                "description": "The PHP Unit Testing framework."
            }
        ]
    }


@pytest.fixture
def detection_config() -> DetectionConfig:
    """Default detection configuration for testing."""
    return DetectionConfig(
        check_composer=True,
        check_files=True,
        check_dependencies=True,
        max_file_size=1024 * 1024,
        timeout=30,
        verbose=False
    )


@pytest.fixture
def mock_detector() -> MagicMock:
    """Mock framework detector for testing."""
    mock = MagicMock()
    mock.name = "test_framework"
    mock.display_name = "Test Framework"
    mock.description = "A test framework"
    mock.detect_async = AsyncMock(return_value=85)
    mock.detect = MagicMock(return_value=True)
    return mock


@pytest.fixture
def framework_scores() -> Dict[FrameworkType, int]:
    """Sample framework detection scores for testing."""
    return {
        FrameworkType.LARAVEL: 95,
        FrameworkType.SYMFONY: 20,
        FrameworkType.CODEIGNITER: 5,
        FrameworkType.CAKEPHP: 0,
        FrameworkType.UNKNOWN: 0
    }


@pytest.fixture
def laravel_project_files(temp_project_dir: Path) -> Path:
    """Create a Laravel project structure for testing."""
    # Create Laravel-specific files
    (temp_project_dir / "artisan").write_text("#!/usr/bin/env php\n<?php\n\nrequire_once __DIR__.'/vendor/autoload.php';\n\n$app = require_once __DIR__.'/bootstrap/app.php';\n\n$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);\n\n$status = $kernel->handle(\n    $input = new Symfony\\Component\\Console\\Input\\ArgvInput,\n    new Symfony\\Component\\Console\\Output\\ConsoleOutput\n);\n\n$kernel->terminate($input, $status);\n\nexit($status);")
    
    # Create app directory
    (temp_project_dir / "app").mkdir()
    (temp_project_dir / "app" / "Http").mkdir()
    (temp_project_dir / "app" / "Http" / "Controllers").mkdir()
    (temp_project_dir / "app" / "Http" / "Controllers" / "Controller.php").write_text("<?php\n\nnamespace App\\Http\\Controllers;\n\nuse Illuminate\\Foundation\\Auth\\Access\\AuthorizesRequests;\nuse Illuminate\\Foundation\\Validation\\ValidatesRequests;\nuse Illuminate\\Routing\\Controller as BaseController;\n\nclass Controller extends BaseController\n{\n    use AuthorizesRequests, ValidatesRequests;\n}")
    
    # Create bootstrap directory
    (temp_project_dir / "bootstrap").mkdir()
    (temp_project_dir / "bootstrap" / "app.php").write_text("<?php\n\nuse Illuminate\\Foundation\\Application;\nuse Illuminate\\Foundation\\Configuration\\Exceptions;\nuse Illuminate\\Foundation\\Configuration\\Middleware;\n\nreturn Application::configure(basePath: dirname(__DIR__))\n    ->withRouting(\n        web: __DIR__.'/../routes/web.php',\n        commands: __DIR__.'/../routes/console.php',\n        health: '/up',\n    )\n    ->withMiddleware(function (Middleware $middleware) {\n        //\n    })\n    ->withExceptions(function (Exceptions $exceptions) {\n        //\n    })->create();")
    
    # Create config directory
    (temp_project_dir / "config").mkdir()
    (temp_project_dir / "config" / "app.php").write_text("<?php\n\nreturn [\n    'name' => env('APP_NAME', 'Laravel'),\n    'env' => env('APP_ENV', 'production'),\n    'debug' => (bool) env('APP_DEBUG', false),\n    'url' => env('APP_URL', 'http://localhost'),\n    'timezone' => 'UTC',\n    'locale' => 'en',\n    'fallback_locale' => 'en',\n    'faker_locale' => 'en_US',\n    'key' => env('APP_KEY'),\n    'cipher' => 'AES-256-CBC',\n];")
    
    # Create routes directory
    (temp_project_dir / "routes").mkdir()
    (temp_project_dir / "routes" / "web.php").write_text("<?php\n\nuse Illuminate\\Support\\Facades\\Route;\n\nRoute::get('/', function () {\n    return view('welcome');\n});")
    
    # Create resources directory
    (temp_project_dir / "resources").mkdir()
    (temp_project_dir / "resources" / "views").mkdir()
    (temp_project_dir / "resources" / "views" / "welcome.blade.php").write_text("<!DOCTYPE html>\n<html>\n<head>\n    <title>Laravel</title>\n</head>\n<body>\n    <h1>Welcome to Laravel</h1>\n</body>\n</html>")
    
    # Create .env file
    (temp_project_dir / ".env").write_text("APP_NAME=Laravel\nAPP_ENV=local\nAPP_KEY=\nAPP_DEBUG=true\nAPP_URL=http://localhost")
    
    return temp_project_dir


@pytest.fixture
def symfony_project_files(temp_project_dir: Path) -> Path:
    """Create a Symfony project structure for testing."""
    # Create Symfony-specific files
    (temp_project_dir / "bin").mkdir()
    (temp_project_dir / "bin" / "console").write_text("#!/usr/bin/env php\n<?php\n\nuse App\\Kernel;\n\nrequire_once dirname(__DIR__).'/vendor/autoload_runtime.php';\n\nreturn function (array $context) {\n    return new Kernel($context['APP_ENV'], (bool) $context['APP_DEBUG']);\n};")
    
    # Create app directory
    (temp_project_dir / "app").mkdir()
    (temp_project_dir / "app" / "Kernel.php").write_text("<?php\n\nnamespace App;\n\nuse Symfony\\Bundle\\FrameworkBundle\\Kernel\\MicroKernelTrait;\nuse Symfony\\Component\\HttpKernel\\Kernel as BaseKernel;\n\nclass Kernel extends BaseKernel\n{\n    use MicroKernelTrait;\n}")
    
    # Create config directory
    (temp_project_dir / "config").mkdir()
    (temp_project_dir / "config" / "packages").mkdir()
    (temp_project_dir / "config" / "packages" / "framework.yaml").write_text("framework:\n    secret: '%env(APP_SECRET)%'\n    http_method_override: false\n    handle_all_throwables: true\n    session:\n        handler_id: null\n        cookie_secure: auto\n        cookie_samesite: lax\n        storage_factory_id: session.storage.factory.native\n    php_errors:\n        log: true")
    
    # Create public directory
    (temp_project_dir / "public").mkdir()
    (temp_project_dir / "public" / "index.php").write_text("<?php\n\nuse App\\Kernel;\n\nrequire_once dirname(__DIR__).'/vendor/autoload_runtime.php';\n\nreturn function (array $context) {\n    return new Kernel($context['APP_ENV'], (bool) $context['APP_DEBUG']);\n};")
    
    # Create src directory
    (temp_project_dir / "src").mkdir()
    (temp_project_dir / "src" / "Controller").mkdir()
    (temp_project_dir / "src" / "Controller" / "DefaultController.php").write_text("<?php\n\nnamespace App\\Controller;\n\nuse Symfony\\Bundle\\FrameworkBundle\\Controller\\AbstractController;\nuse Symfony\\Component\\HttpFoundation\\Response;\nuse Symfony\\Component\\Routing\\Annotation\\Route;\n\nclass DefaultController extends AbstractController\n{\n    /**\n     * @Route(\"/\", name=\"homepage\")\n     */\n    public function index(): Response\n    {\n        return $this->render('default/index.html.twig');\n    }\n}")
    
    # Create var directory
    (temp_project_dir / "var").mkdir()
    (temp_project_dir / "var" / "cache").mkdir()
    (temp_project_dir / "var" / "log").mkdir()
    
    return temp_project_dir


@pytest.fixture
def empty_project_dir(temp_project_dir: Path) -> Path:
    """Create an empty project directory for testing."""
    # Just return the empty temp directory
    return temp_project_dir


class AsyncTestCase:
    """Base class for async test cases."""
    
    @pytest.fixture(autouse=True)
    def setup_event_loop(self, event_loop: asyncio.AbstractEventLoop) -> None:
        """Set up event loop for async tests."""
        self.loop = event_loop
        asyncio.set_event_loop(self.loop)
    
    async def run_async_test(self, coro) -> any:
        """Helper method to run async tests."""
        return await self.loop.run_until_complete(coro)


# Pytest markers
pytest_plugins = ["pytest_asyncio"] 