"""
Tests for FrameworkDetector base class.

This module tests the abstract base class for all framework detectors.
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from php_framework_detector.core.detector import FrameworkDetector
from php_framework_detector.core.models import DetectionConfig, FrameworkType
from php_framework_detector.core.exceptions import TimeoutError, FileReadError


class MockDetector(FrameworkDetector):
    """Mock detector for testing the base class."""
    
    @property
    def name(self) -> str:
        return "mock_framework"
    
    @property
    def display_name(self) -> str:
        return "Mock Framework"
    
    def detect(self) -> bool:
        return True
    
    async def _detect_async_impl(self) -> int:
        return 85


class TestFrameworkDetector:
    """Test FrameworkDetector base class."""
    
    def test_detector_initialization(self, temp_project_dir: Path):
        """Test detector initialization."""
        detector = MockDetector(str(temp_project_dir))
        
        assert detector.project_path == temp_project_dir.resolve()
        assert isinstance(detector.config, DetectionConfig)
        assert detector._composer_data is None
        assert detector._file_cache == {}
    
    def test_detector_initialization_with_config(self, temp_project_dir: Path):
        """Test detector initialization with custom config."""
        config = DetectionConfig(timeout=60, verbose=True)
        detector = MockDetector(str(temp_project_dir), config)
        
        assert detector.project_path == temp_project_dir.resolve()
        assert detector.config == config
        assert detector.config.timeout == 60
        assert detector.config.verbose is True
    
    def test_detector_properties(self, temp_project_dir: Path):
        """Test detector properties."""
        detector = MockDetector(str(temp_project_dir))
        
        assert detector.name == "mock_framework"
        assert detector.display_name == "Mock Framework"
        assert "Mock Framework" in detector.description
    
    def test_metadata_property(self, temp_project_dir: Path):
        """Test metadata property."""
        detector = MockDetector(str(temp_project_dir))
        metadata = detector.metadata
        
        assert metadata.framework_type == FrameworkType.UNKNOWN  # mock_framework not in enum
        assert metadata.detection_methods == []
        assert metadata.file_patterns == []
        assert metadata.composer_packages == []
        assert metadata.content_patterns == []
    
    @pytest.mark.asyncio
    async def test_detect_async_success(self, temp_project_dir: Path):
        """Test successful async detection."""
        detector = MockDetector(str(temp_project_dir))
        
        result = await detector.detect_async()
        
        assert result == 85
    
    @pytest.mark.asyncio
    async def test_detect_async_timeout(self, temp_project_dir: Path):
        """Test async detection timeout."""
        config = DetectionConfig(timeout=0.1)  # Very short timeout
        detector = MockDetector(str(temp_project_dir), config)
        
        # Mock the async implementation to be slow
        async def slow_detection():
            await asyncio.sleep(1)
            return 100
        
        detector._detect_async_impl = slow_detection
        
        with pytest.raises(TimeoutError) as exc_info:
            await detector.detect_async()
        
        assert "framework detection" in str(exc_info.value)
        assert exc_info.value.timeout_seconds == 0.1
    
    @pytest.mark.asyncio
    async def test_detect_async_exception(self, temp_project_dir: Path):
        """Test async detection with exception."""
        detector = MockDetector(str(temp_project_dir))
        
        # Mock the async implementation to raise an exception
        async def failing_detection():
            raise ValueError("Test error")
        
        detector._detect_async_impl = failing_detection
        
        result = await detector.detect_async()
        
        # Should return 0 on exception
        assert result == 0
    
    @pytest.mark.asyncio
    async def test_load_composer_json_async_success(self, temp_project_dir: Path, sample_composer_json: dict):
        """Test successful composer.json loading."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create composer.json file
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_text(json.dumps(sample_composer_json))
        
        result = await detector._load_composer_json_async()
        
        assert result == sample_composer_json
        assert detector._composer_data == sample_composer_json
    
    @pytest.mark.asyncio
    async def test_load_composer_lock_async_fallback(self, temp_project_dir: Path, sample_composer_lock: dict):
        """Test composer.lock fallback when composer.json doesn't exist."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create composer.lock file (no composer.json)
        lock_file = temp_project_dir / "composer.lock"
        lock_file.write_text(json.dumps(sample_composer_lock))
        
        result = await detector._load_composer_json_async()
        
        assert result == sample_composer_lock
        assert detector._composer_data == sample_composer_lock
    
    @pytest.mark.asyncio
    async def test_load_composer_json_async_no_files(self, temp_project_dir: Path):
        """Test composer loading when no files exist."""
        detector = MockDetector(str(temp_project_dir))
        
        result = await detector._load_composer_json_async()
        
        assert result == {}
        assert detector._composer_data == {}
    
    @pytest.mark.asyncio
    async def test_load_composer_json_async_invalid_json(self, temp_project_dir: Path):
        """Test composer loading with invalid JSON."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create invalid composer.json
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_text("invalid json content")
        
        result = await detector._load_composer_json_async()
        
        # Should return empty dict on JSON error
        assert result == {}
        assert detector._composer_data == {}
    
    @pytest.mark.asyncio
    async def test_load_composer_json_async_cached(self, temp_project_dir: Path, sample_composer_json: dict):
        """Test that composer data is cached after first load."""
        detector = MockDetector(str(temp_project_dir))
        
        # Set cached data
        detector._composer_data = sample_composer_json
        
        result = await detector._load_composer_json_async()
        
        assert result == sample_composer_json
        # Should not read file again
    
    @pytest.mark.asyncio
    async def test_check_path_patterns_async_success(self, temp_project_dir: Path):
        """Test successful path pattern checking."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create a file that matches pattern
        test_file = temp_project_dir / "test_file.txt"
        test_file.write_text("test content")
        
        patterns = ["test_file.txt", "nonexistent.txt"]
        result = await detector._check_path_patterns_async(patterns)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_path_patterns_async_not_found(self, temp_project_dir: Path):
        """Test path pattern checking when no patterns match."""
        detector = MockDetector(str(temp_project_dir))
        
        patterns = ["nonexistent1.txt", "nonexistent2.txt"]
        result = await detector._check_path_patterns_async(patterns)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_composer_dependency_async_found(self, temp_project_dir: Path):
        """Test composer dependency checking when package is found."""
        detector = MockDetector(str(temp_project_dir))
        
        # Mock composer data
        detector._composer_data = {
            "require": {
                "laravel/framework": "^10.0",
                "php": ">=8.0"
            },
            "require-dev": {
                "phpunit/phpunit": "^10.0"
            }
        }
        
        # Test require section
        result = await detector._check_composer_dependency_async("laravel/framework")
        assert result is True
        
        # Test require-dev section
        result = await detector._check_composer_dependency_async("phpunit/phpunit")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_composer_dependency_async_not_found(self, temp_project_dir: Path):
        """Test composer dependency checking when package is not found."""
        detector = MockDetector(str(temp_project_dir))
        
        # Mock composer data
        detector._composer_data = {
            "require": {
                "laravel/framework": "^10.0"
            }
        }
        
        result = await detector._check_composer_dependency_async("symfony/framework-bundle")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_composer_dependency_async_no_composer_data(self, temp_project_dir: Path):
        """Test composer dependency checking with no composer data."""
        detector = MockDetector(str(temp_project_dir))
        
        result = await detector._check_composer_dependency_async("laravel/framework")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_file_content_async_success(self, temp_project_dir: Path):
        """Test successful file content checking."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create test file
        test_file = temp_project_dir / "test.php"
        test_file.write_text("<?php\n\n// Laravel Framework\n// Illuminate\\Support\\Facades\\Route\n")
        
        patterns = ["Laravel Framework", "Illuminate\\"]
        result = await detector._check_file_content_async("test.php", patterns)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_file_content_async_not_found(self, temp_project_dir: Path):
        """Test file content checking when patterns are not found."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create test file
        test_file = temp_project_dir / "test.php"
        test_file.write_text("<?php\n\n// Some other content\n")
        
        patterns = ["Laravel Framework", "Illuminate\\"]
        result = await detector._check_file_content_async("test.php", patterns)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_file_content_async_file_not_found(self, temp_project_dir: Path):
        """Test file content checking when file doesn't exist."""
        detector = MockDetector(str(temp_project_dir))
        
        patterns = ["Laravel Framework"]
        result = await detector._check_file_content_async("nonexistent.php", patterns)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_file_content_async_with_max_size(self, temp_project_dir: Path):
        """Test file content checking with max size limit."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create large test file
        test_file = temp_project_dir / "large.php"
        large_content = "<?php\n" + "// " + "x" * 1000  # Large content
        test_file.write_text(large_content)
        
        patterns = ["Laravel"]
        result = await detector._check_file_content_async("large.php", patterns, max_size=100)
        
        # Should not find pattern due to size limit
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_regex_patterns_async_success(self, temp_project_dir: Path):
        """Test successful regex pattern checking."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create test file
        test_file = temp_project_dir / "test.php"
        test_file.write_text("<?php\n\nnamespace App\\Http\\Controllers;\n\nclass Controller\n{\n}\n")
        
        patterns = [r"namespace\s+App\\", r"class\s+Controller"]
        result = await detector._check_regex_patterns_async("test.php", patterns)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_regex_patterns_async_not_found(self, temp_project_dir: Path):
        """Test regex pattern checking when patterns are not found."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create test file
        test_file = temp_project_dir / "test.php"
        test_file.write_text("<?php\n\n// Some other content\n")
        
        patterns = [r"namespace\s+App\\", r"class\s+Controller"]
        result = await detector._check_regex_patterns_async("test.php", patterns)
        
        assert result is False
    
    def test_get_detection_methods(self, temp_project_dir: Path):
        """Test getting detection methods."""
        detector = MockDetector(str(temp_project_dir))
        
        methods = detector._get_detection_methods()
        
        assert isinstance(methods, list)
    
    def test_get_file_patterns(self, temp_project_dir: Path):
        """Test getting file patterns."""
        detector = MockDetector(str(temp_project_dir))
        
        patterns = detector._get_file_patterns()
        
        assert isinstance(patterns, list)
    
    def test_get_composer_packages(self, temp_project_dir: Path):
        """Test getting composer packages."""
        detector = MockDetector(str(temp_project_dir))
        
        packages = detector._get_composer_packages()
        
        assert isinstance(packages, list)
    
    def test_get_content_patterns(self, temp_project_dir: Path):
        """Test getting content patterns."""
        detector = MockDetector(str(temp_project_dir))
        
        patterns = detector._get_content_patterns()
        
        assert isinstance(patterns, list)
    
    def test_load_composer_json_sync(self, temp_project_dir: Path, sample_composer_json: dict):
        """Test synchronous composer.json loading."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create composer.json file
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_text(json.dumps(sample_composer_json))
        
        result = detector._load_composer_json()
        
        assert result == sample_composer_json


class TestDetectorErrorHandling:
    """Test error handling in FrameworkDetector."""
    
    @pytest.mark.asyncio
    async def test_file_read_error_handling(self, temp_project_dir: Path):
        """Test handling of file read errors."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create a file that can't be read (directory)
        test_dir = temp_project_dir / "test_dir"
        test_dir.mkdir()
        
        # Try to read directory as file
        result = await detector._check_file_content_async("test_dir", ["pattern"])
        
        # Should handle error gracefully
        assert result is False
    
    @pytest.mark.asyncio
    async def test_composer_json_encoding_error(self, temp_project_dir: Path):
        """Test handling of composer.json encoding errors."""
        detector = MockDetector(str(temp_project_dir))
        
        # Create composer.json with invalid encoding
        composer_file = temp_project_dir / "composer.json"
        composer_file.write_bytes(b'\xff\xfe\x00\x00')  # Invalid UTF-8
        
        result = await detector._load_composer_json_async()
        
        # Should return empty dict on encoding error
        assert result == {}
    
    def test_detector_abstract_methods(self):
        """Test that abstract methods are properly defined."""
        # Should not be able to instantiate abstract class directly
        with pytest.raises(TypeError):
            FrameworkDetector("/test/path") 