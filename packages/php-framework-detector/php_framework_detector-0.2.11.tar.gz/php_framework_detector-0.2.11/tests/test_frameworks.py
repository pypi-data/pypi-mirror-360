"""
Tests for specific framework detectors.

This module tests individual framework detectors like Laravel, Symfony, etc.
"""

import json
import pytest
from pathlib import Path

from php_framework_detector.frameworks.laravel import LaravelDetector
from php_framework_detector.frameworks.symfony import SymfonyDetector
from php_framework_detector.core.models import DetectionConfig, FrameworkType


class TestLaravelDetector:
    """Test Laravel framework detector."""
    
    def test_laravel_detector_properties(self, temp_project_dir: Path):
        """Test Laravel detector properties."""
        detector = LaravelDetector(str(temp_project_dir))
        
        assert detector.name == "laravel"
        assert detector.display_name == "Laravel"
        assert "elegant syntax" in detector.description
    
    def test_laravel_metadata(self, temp_project_dir: Path):
        """Test Laravel detector metadata."""
        detector = LaravelDetector(str(temp_project_dir))
        metadata = detector.metadata
        
        assert metadata.framework_type == FrameworkType.LARAVEL
        assert "artisan" in metadata.file_patterns
        assert "laravel/framework" in metadata.composer_packages
        assert "Laravel Framework" in metadata.content_patterns
    
    @pytest.mark.asyncio
    async def test_laravel_detection_with_artisan(self, laravel_project_files: Path):
        """Test Laravel detection with artisan file."""
        detector = LaravelDetector(str(laravel_project_files))
        
        score = await detector.detect_async()
        
        # Should detect Laravel with high confidence due to artisan file
        assert score >= 100
    
    @pytest.mark.asyncio
    async def test_laravel_detection_with_composer(self, temp_project_dir: Path):
        """Test Laravel detection with composer dependency."""
        detector = LaravelDetector(str(temp_project_dir))
        
        # Create composer.json with Laravel dependency
        composer_data = {
            "require": {
                "laravel/framework": "^10.0"
            }
        }
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_text(json.dumps(composer_data))
        
        score = await detector.detect_async()
        
        # Should detect Laravel with medium confidence
        assert score >= 20
    
    @pytest.mark.asyncio
    async def test_laravel_detection_with_content_patterns(self, temp_project_dir: Path):
        """Test Laravel detection with content patterns."""
        detector = LaravelDetector(str(temp_project_dir))
        
        # Create artisan file with Laravel content
        artisan_file = temp_project_dir / "artisan"
        artisan_content = """#!/usr/bin/env php
<?php

require_once __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';

$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);

$status = $kernel->handle(
    $input = new Symfony\\Component\\Console\\Input\\ArgvInput,
    new Symfony\\Component\\Console\\Output\\ConsoleOutput
);

$kernel->terminate($input, $status);

exit($status);
"""
        artisan_file.write_text(artisan_content)
        
        score = await detector.detect_async()
        
        # Should detect Laravel with high confidence
        assert score >= 120  # artisan file + content patterns
    
    @pytest.mark.asyncio
    async def test_laravel_detection_with_env_file(self, temp_project_dir: Path):
        """Test Laravel detection with .env file."""
        detector = LaravelDetector(str(temp_project_dir))
        
        # Create .env file
        env_file = temp_project_dir / ".env"
        env_file.write_text("APP_NAME=Laravel\nAPP_ENV=local")
        
        score = await detector.detect_async()
        
        # Should detect Laravel with low confidence
        assert score >= 10
    
    @pytest.mark.asyncio
    async def test_laravel_detection_no_framework(self, empty_project_dir: Path):
        """Test Laravel detection with no Laravel files."""
        detector = LaravelDetector(str(empty_project_dir))
        
        score = await detector.detect_async()
        
        # Should not detect Laravel
        assert score == 0
    
    @pytest.mark.asyncio
    async def test_laravel_detection_combined_indicators(self, temp_project_dir: Path):
        """Test Laravel detection with multiple indicators."""
        detector = LaravelDetector(str(temp_project_dir))
        
        # Create multiple Laravel indicators
        # 1. Composer dependency
        composer_data = {
            "require": {
                "laravel/framework": "^10.0"
            }
        }
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_text(json.dumps(composer_data))
        
        # 2. .env file
        env_file = temp_project_dir / ".env"
        env_file.write_text("APP_NAME=Laravel")
        
        # 3. Artisan file with Laravel content
        artisan_file = temp_project_dir / "artisan"
        artisan_content = "<?php\n\n// Laravel Framework\n// Artisan Console Application"
        artisan_file.write_text(artisan_content)
        
        score = await detector.detect_async()
        
        # Should detect Laravel with very high confidence
        assert score >= 130  # composer + env + artisan + content patterns
    
    def test_laravel_file_patterns(self, temp_project_dir: Path):
        """Test Laravel file patterns."""
        detector = LaravelDetector(str(temp_project_dir))
        patterns = detector._get_file_patterns()
        
        expected_patterns = [
            "artisan",
            "app",
            "bootstrap",
            "config",
            ".env",
            "resources/views",
            "routes/web.php"
        ]
        
        for pattern in expected_patterns:
            assert pattern in patterns
    
    def test_laravel_composer_packages(self, temp_project_dir: Path):
        """Test Laravel composer packages."""
        detector = LaravelDetector(str(temp_project_dir))
        packages = detector._get_composer_packages()
        
        expected_packages = [
            "laravel/framework",
            "laravel/laravel"
        ]
        
        for package in expected_packages:
            assert package in packages
    
    def test_laravel_content_patterns(self, temp_project_dir: Path):
        """Test Laravel content patterns."""
        detector = LaravelDetector(str(temp_project_dir))
        patterns = detector._get_content_patterns()
        
        expected_patterns = [
            "Laravel Framework",
            "Artisan Console Application",
            "Illuminate\\",
            "Route::",
            "DB::",
            "Auth::"
        ]
        
        for pattern in expected_patterns:
            assert pattern in patterns


class TestSymfonyDetector:
    """Test Symfony framework detector."""
    
    def test_symfony_detector_properties(self, temp_project_dir: Path):
        """Test Symfony detector properties."""
        detector = SymfonyDetector(str(temp_project_dir))
        
        assert detector.name == "symfony"
        assert detector.display_name == "Symfony"
        assert "High-performance" in detector.description
    
    def test_symfony_metadata(self, temp_project_dir: Path):
        """Test Symfony detector metadata."""
        detector = SymfonyDetector(str(temp_project_dir))
        metadata = detector.metadata
        
        assert metadata.framework_type == FrameworkType.SYMFONY
        assert "bin/console" in metadata.file_patterns
        assert "symfony/framework-bundle" in metadata.composer_packages
        assert "Symfony\\Bundle" in metadata.content_patterns
    
    @pytest.mark.asyncio
    async def test_symfony_detection_with_console(self, symfony_project_files: Path):
        """Test Symfony detection with bin/console file."""
        detector = SymfonyDetector(str(symfony_project_files))
        
        score = await detector.detect_async()
        
        # Should detect Symfony with high confidence due to bin/console file
        assert score >= 100
    
    @pytest.mark.asyncio
    async def test_symfony_detection_with_composer(self, temp_project_dir: Path):
        """Test Symfony detection with composer dependency."""
        detector = SymfonyDetector(str(temp_project_dir))
        
        # Create composer.json with Symfony dependency
        composer_data = {
            "require": {
                "symfony/framework-bundle": "^6.0"
            }
        }
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_text(json.dumps(composer_data))
        
        score = await detector.detect_async()
        
        # Should detect Symfony with medium confidence
        assert score >= 20
    
    @pytest.mark.asyncio
    async def test_symfony_detection_with_content_patterns(self, temp_project_dir: Path):
        """Test Symfony detection with content patterns."""
        detector = SymfonyDetector(str(temp_project_dir))
        
        # Create bin/console file with Symfony content
        console_file = temp_project_dir / "bin" / "console"
        console_file.parent.mkdir()
        console_content = """#!/usr/bin/env php
<?php

use App\\Kernel;

require_once dirname(__DIR__).'/vendor/autoload_runtime.php';

return function (array $context) {
    return new Kernel($context['APP_ENV'], (bool) $context['APP_DEBUG']);
};
"""
        console_file.write_text(console_content)
        
        score = await detector.detect_async()
        
        # Should detect Symfony with high confidence
        assert score >= 120  # bin/console + content patterns
    
    @pytest.mark.asyncio
    async def test_symfony_detection_with_app_kernel(self, temp_project_dir: Path):
        """Test Symfony detection with app/Kernel.php."""
        detector = SymfonyDetector(str(temp_project_dir))
        
        # Create app/Kernel.php
        app_dir = temp_project_dir / "app"
        app_dir.mkdir()
        kernel_file = app_dir / "Kernel.php"
        kernel_content = """<?php

namespace App;

use Symfony\\Bundle\\FrameworkBundle\\Kernel\\MicroKernelTrait;
use Symfony\\Component\\HttpKernel\\Kernel as BaseKernel;

class Kernel extends BaseKernel
{
    use MicroKernelTrait;
}
"""
        kernel_file.write_text(kernel_content)
        
        score = await detector.detect_async()
        
        # Should detect Symfony with medium confidence
        assert score >= 20
    
    @pytest.mark.asyncio
    async def test_symfony_detection_with_public_index(self, temp_project_dir: Path):
        """Test Symfony detection with public/index.php."""
        detector = SymfonyDetector(str(temp_project_dir))
        
        # Create public/index.php
        public_dir = temp_project_dir / "public"
        public_dir.mkdir()
        index_file = public_dir / "index.php"
        index_content = """<?php

use App\\Kernel;

require_once dirname(__DIR__).'/vendor/autoload_runtime.php';

return function (array $context) {
    return new Kernel($context['APP_ENV'], (bool) $context['APP_DEBUG']);
};
"""
        index_file.write_text(index_content)
        
        score = await detector.detect_async()
        
        # Should detect Symfony with medium confidence
        assert score >= 20
    
    @pytest.mark.asyncio
    async def test_symfony_detection_no_framework(self, empty_project_dir: Path):
        """Test Symfony detection with no Symfony files."""
        detector = SymfonyDetector(str(empty_project_dir))
        
        score = await detector.detect_async()
        
        # Should not detect Symfony
        assert score == 0
    
    @pytest.mark.asyncio
    async def test_symfony_detection_combined_indicators(self, temp_project_dir: Path):
        """Test Symfony detection with multiple indicators."""
        detector = SymfonyDetector(str(temp_project_dir))
        
        # Create multiple Symfony indicators
        # 1. Composer dependency
        composer_data = {
            "require": {
                "symfony/framework-bundle": "^6.0"
            }
        }
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_text(json.dumps(composer_data))
        
        # 2. bin/console file
        bin_dir = temp_project_dir / "bin"
        bin_dir.mkdir()
        console_file = bin_dir / "console"
        console_file.write_text("#!/usr/bin/env php\n<?php\n\n// Symfony Console")
        
        # 3. app/Kernel.php
        app_dir = temp_project_dir / "app"
        app_dir.mkdir()
        kernel_file = app_dir / "Kernel.php"
        kernel_file.write_text("<?php\n\nnamespace App;\n\nuse Symfony\\Bundle\\FrameworkBundle\\Kernel\\MicroKernelTrait;")
        
        score = await detector.detect_async()
        
        # Should detect Symfony with very high confidence
        assert score >= 140  # composer + bin/console + app/Kernel.php + content patterns
    
    def test_symfony_file_patterns(self, temp_project_dir: Path):
        """Test Symfony file patterns."""
        detector = SymfonyDetector(str(temp_project_dir))
        patterns = detector._get_file_patterns()
        
        expected_patterns = [
            "bin/console",
            "app/Kernel.php",
            "public/index.php",
            "config/packages",
            "src/Controller",
            "var/cache",
            "var/log"
        ]
        
        for pattern in expected_patterns:
            assert pattern in patterns
    
    def test_symfony_composer_packages(self, temp_project_dir: Path):
        """Test Symfony composer packages."""
        detector = SymfonyDetector(str(temp_project_dir))
        packages = detector._get_composer_packages()
        
        expected_packages = [
            "symfony/framework-bundle",
            "symfony/symfony"
        ]
        
        for package in expected_packages:
            assert package in packages
    
    def test_symfony_content_patterns(self, temp_project_dir: Path):
        """Test Symfony content patterns."""
        detector = SymfonyDetector(str(temp_project_dir))
        patterns = detector._get_content_patterns()
        
        expected_patterns = [
            "Symfony\\Bundle",
            "Symfony\\Component",
            "use Symfony\\",
            "extends BaseKernel",
            "MicroKernelTrait"
        ]
        
        for pattern in expected_patterns:
            assert pattern in patterns


class TestFrameworkDetectionIntegration:
    """Test integration between different framework detectors."""
    
    @pytest.mark.asyncio
    async def test_multiple_frameworks_same_project(self, temp_project_dir: Path):
        """Test detecting multiple frameworks in the same project."""
        # Create a project with both Laravel and Symfony indicators
        # This could happen in a mixed project or during migration
        
        # Laravel indicators
        artisan_file = temp_project_dir / "artisan"
        artisan_file.write_text("<?php\n\n// Laravel Framework")
        
        # Symfony indicators
        bin_dir = temp_project_dir / "bin"
        bin_dir.mkdir()
        console_file = bin_dir / "console"
        console_file.write_text("#!/usr/bin/env php\n<?php\n\n// Symfony Console")
        
        # Test Laravel detection
        laravel_detector = LaravelDetector(str(temp_project_dir))
        laravel_score = await laravel_detector.detect_async()
        
        # Test Symfony detection
        symfony_detector = SymfonyDetector(str(temp_project_dir))
        symfony_score = await symfony_detector.detect_async()
        
        # Both should be detected
        assert laravel_score > 0
        assert symfony_score > 0
    
    @pytest.mark.asyncio
    async def test_framework_detection_with_config(self, temp_project_dir: Path):
        """Test framework detection with custom configuration."""
        # Create Laravel project
        artisan_file = temp_project_dir / "artisan"
        artisan_file.write_text("<?php\n\n// Laravel Framework")
        
        # Test with different configs
        config_fast = DetectionConfig(timeout=5, max_file_size=1024)
        config_verbose = DetectionConfig(verbose=True, timeout=30)
        
        # Test Laravel with fast config
        detector_fast = LaravelDetector(str(temp_project_dir), config_fast)
        score_fast = await detector_fast.detect_async()
        
        # Test Laravel with verbose config
        detector_verbose = LaravelDetector(str(temp_project_dir), config_verbose)
        score_verbose = await detector_verbose.detect_async()
        
        # Both should detect Laravel
        assert score_fast > 0
        assert score_verbose > 0
        assert score_fast == score_verbose  # Same detection logic 