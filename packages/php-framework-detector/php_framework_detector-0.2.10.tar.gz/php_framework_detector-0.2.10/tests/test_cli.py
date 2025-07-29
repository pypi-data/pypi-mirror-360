"""
Tests for CLI interface.

This module tests the command-line interface functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typer.testing import CliRunner

from php_framework_detector.cli import app, detect_frameworks_async, display_results
from php_framework_detector.core.models import DetectionResult, FrameworkType
from php_framework_detector.core.exceptions import InvalidPathError, DetectionError


class TestCLICommands:
    """Test CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_detect_command_help(self):
        """Test detect command help."""
        result = self.runner.invoke(app, ["detect", "--help"])
        assert result.exit_code == 0
        assert "Detect PHP frameworks" in result.output
    
    def test_list_frameworks_command_help(self):
        """Test list-frameworks command help."""
        result = self.runner.invoke(app, ["list-frameworks", "--help"])
        assert result.exit_code == 0
        assert "List all supported PHP frameworks" in result.output
    
    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "PHP Framework Detector" in result.output
    
    @patch('php_framework_detector.cli.detect_frameworks_async')
    def test_detect_command_success(self, mock_detect):
        """Test successful detect command."""
        # Mock detection result
        mock_result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 20},
            project_path="/test/path"
        )
        mock_detect.return_value = mock_result
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                result = self.runner.invoke(app, ["detect", "/test/path"])
                
                assert result.exit_code == 0
                assert "Laravel" in result.output
                # Note: Rich table output might not show exact score in simple text check
    
    @patch('php_framework_detector.cli.detect_frameworks_async')
    def test_detect_command_json_output(self, mock_detect):
        """Test detect command with JSON output."""
        # Mock detection result
        mock_result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95},
            project_path="/test/path"
        )
        mock_detect.return_value = mock_result
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                result = self.runner.invoke(app, ["detect", "/test/path", "--json"])
                
                assert result.exit_code == 0
                # Should contain JSON output
                try:
                    json.loads(result.output)
                except json.JSONDecodeError:
                    pytest.fail("Output should be valid JSON")
    
    @patch('php_framework_detector.cli.detect_frameworks_async')
    def test_detect_command_show_all(self, mock_detect):
        """Test detect command with show-all flag."""
        # Mock detection result
        mock_result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 0},
            project_path="/test/path"
        )
        mock_detect.return_value = mock_result
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                result = self.runner.invoke(app, ["detect", "/test/path", "--all"])
                
                assert result.exit_code == 0
                # Should show both frameworks even with zero score
                assert "Laravel" in result.output
                assert "Symfony" in result.output
    
    def test_detect_command_invalid_path(self):
        """Test detect command with invalid path."""
        result = self.runner.invoke(app, ["detect", "/nonexistent/path"])
        
        assert result.exit_code == 1
        assert "Detection failed" in result.output
    
    @patch('php_framework_detector.cli.detect_frameworks_async')
    def test_detect_command_detection_error(self, mock_detect):
        """Test detect command with detection error."""
        mock_detect.side_effect = DetectionError("Test detection error")
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                result = self.runner.invoke(app, ["detect", "/test/path"])
                
                assert result.exit_code == 1
                assert "Detection failed" in result.output
    
    @patch('php_framework_detector.cli.FrameworkDetectorFactory.get_all_detectors')
    def test_list_frameworks_command(self, mock_get_detectors):
        """Test list-frameworks command."""
        # Mock detectors
        mock_detector1 = MagicMock()
        mock_detector1.name = "laravel"
        mock_detector1.display_name = "Laravel"
        mock_detector1.description = "Modern PHP framework"
        
        mock_detector2 = MagicMock()
        mock_detector2.name = "symfony"
        mock_detector2.display_name = "Symfony"
        mock_detector2.description = "High-performance framework"
        
        mock_get_detectors.return_value = [mock_detector1, mock_detector2]
        
        result = self.runner.invoke(app, ["list-frameworks"])
        
        assert result.exit_code == 0
        assert "Laravel" in result.output
        assert "Symfony" in result.output
        assert "Modern PHP framework" in result.output


class TestDetectionAsync:
    """Test async detection functionality."""
    
    @pytest.mark.asyncio
    async def test_detect_frameworks_async_success(self, temp_project_dir: Path):
        """Test successful async framework detection."""
        # Create a simple project structure
        (temp_project_dir / "composer.json").write_text('{"name": "test/project"}')
        
        with patch('php_framework_detector.cli.FrameworkDetectorFactory.get_all_detectors') as mock_get_detectors:
            with patch('php_framework_detector.cli.FrameworkDetectorFactory.get_framework_names') as mock_get_names:
                # Mock detectors
                mock_detector1 = MagicMock()
                mock_detector1.name = FrameworkType.LARAVEL
                mock_detector1.display_name = "Laravel"
                mock_detector1.detect_async = AsyncMock(return_value=100)  # Perfect score to trigger detection
                
                mock_detector2 = MagicMock()
                mock_detector2.name = FrameworkType.SYMFONY
                mock_detector2.display_name = "Symfony"
                mock_detector2.detect_async = AsyncMock(return_value=20)
                
                mock_get_detectors.return_value = [mock_detector1, mock_detector2]
                mock_get_names.return_value = {FrameworkType.LARAVEL: "Laravel", FrameworkType.SYMFONY: "Symfony"}
                
                result = await detect_frameworks_async(temp_project_dir)
                
                assert result.detected_framework == FrameworkType.LARAVEL
                assert result.scores[FrameworkType.LARAVEL] == 100
                assert result.scores[FrameworkType.SYMFONY] == 20
                assert result.project_path == str(temp_project_dir)
    
    @pytest.mark.asyncio
    async def test_detect_frameworks_async_path_not_exists(self):
        """Test async detection with non-existent path."""
        non_existent_path = Path("/nonexistent/path")
        
        with pytest.raises(DetectionError) as exc_info:
            await detect_frameworks_async(non_existent_path)
        
        assert "does not exist" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_detect_frameworks_async_path_not_directory(self, temp_project_dir: Path):
        """Test async detection with path that is not a directory."""
        # Create a file instead of directory
        file_path = temp_project_dir / "test.txt"
        file_path.write_text("test")
        
        with pytest.raises(DetectionError) as exc_info:
            await detect_frameworks_async(file_path)
        
        assert "not a directory" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_detect_frameworks_async_detector_exception(self, temp_project_dir: Path):
        """Test async detection with detector exception."""
        with patch('php_framework_detector.cli.FrameworkDetectorFactory.get_all_detectors') as mock_get_detectors:
            with patch('php_framework_detector.cli.FrameworkDetectorFactory.get_framework_names') as mock_get_names:
                # Mock detector that raises exception
                mock_detector = MagicMock()
                mock_detector.name = FrameworkType.LARAVEL
                mock_detector.display_name = "Laravel"
                mock_detector.detect_async = AsyncMock(side_effect=Exception("Test error"))
                
                mock_get_detectors.return_value = [mock_detector]
                mock_get_names.return_value = {FrameworkType.LARAVEL: "Laravel"}
                
                result = await detect_frameworks_async(temp_project_dir)
                
                # Should handle exception gracefully and return 0 score
                assert result.scores[FrameworkType.LARAVEL] == 0
    
    @pytest.mark.asyncio
    async def test_detect_frameworks_async_no_framework_detected(self, temp_project_dir: Path):
        """Test async detection when no framework is detected."""
        with patch('php_framework_detector.cli.FrameworkDetectorFactory.get_all_detectors') as mock_get_detectors:
            with patch('php_framework_detector.cli.FrameworkDetectorFactory.get_framework_names') as mock_get_names:
                # Mock detectors with low scores
                mock_detector1 = MagicMock()
                mock_detector1.name = FrameworkType.LARAVEL
                mock_detector1.display_name = "Laravel"
                mock_detector1.detect_async = AsyncMock(return_value=5)
                
                mock_detector2 = MagicMock()
                mock_detector2.name = FrameworkType.SYMFONY
                mock_detector2.display_name = "Symfony"
                mock_detector2.detect_async = AsyncMock(return_value=10)
                
                mock_get_detectors.return_value = [mock_detector1, mock_detector2]
                mock_get_names.return_value = {FrameworkType.LARAVEL: "Laravel", FrameworkType.SYMFONY: "Symfony"}
                
                result = await detect_frameworks_async(temp_project_dir)
                
                # Should return "na" for unknown framework
                assert result.detected_framework == FrameworkType.UNKNOWN
                assert result.detected_name == "Unknown"


class TestDisplayResults:
    """Test result display functionality."""
    
    def test_display_results_table(self):
        """Test displaying results in table format."""
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 20},
            project_path="/test/path"
        )
        
        # This test mainly checks that display_results doesn't raise exceptions
        # The actual output formatting is handled by Rich library
        try:
            display_results(result, show_all=False, json_output=False)
        except Exception as e:
            pytest.fail(f"display_results raised exception: {e}")
    
    def test_display_results_json(self):
        """Test displaying results in JSON format."""
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 20},
            project_path="/test/path"
        )
        
        # This test mainly checks that display_results doesn't raise exceptions
        try:
            display_results(result, show_all=False, json_output=True)
        except Exception as e:
            pytest.fail(f"display_results raised exception: {e}")
    
    def test_display_results_show_all(self):
        """Test displaying results with show_all flag."""
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 0},
            project_path="/test/path"
        )
        
        # This test mainly checks that display_results doesn't raise exceptions
        try:
            display_results(result, show_all=True, json_output=False)
        except Exception as e:
            pytest.fail(f"display_results raised exception: {e}")
    
    def test_display_results_unknown_framework(self):
        """Test displaying results with unknown framework."""
        result = DetectionResult(
            detected_framework=FrameworkType.UNKNOWN,
            scores={FrameworkType.LARAVEL: 5, FrameworkType.SYMFONY: 10},
            project_path="/test/path"
        )
        
        # This test mainly checks that display_results doesn't raise exceptions
        try:
            display_results(result, show_all=False, json_output=False)
        except Exception as e:
            pytest.fail(f"display_results raised exception: {e}")


class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('php_framework_detector.cli.detect_frameworks_async')
    def test_cli_with_verbose_logging(self, mock_detect):
        """Test CLI with verbose logging enabled."""
        mock_result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95},
            project_path="/test/path"
        )
        mock_detect.return_value = mock_result
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                with patch('structlog.stdlib.get_logger') as mock_logger:
                    result = self.runner.invoke(app, ["detect", "/test/path", "--verbose"])
                    
                    assert result.exit_code == 0
                    mock_logger.return_value.setLevel.assert_called_with("DEBUG")
    
    def test_cli_keyboard_interrupt(self):
        """Test CLI handling of keyboard interrupt."""
        with patch('php_framework_detector.cli.detect_frameworks_async') as mock_detect:
            mock_detect.side_effect = KeyboardInterrupt()
            
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    result = self.runner.invoke(app, ["detect", "/test/path"])
                    
                    assert result.exit_code == 1
                    assert "cancelled" in result.output.lower()
    
    def test_cli_unexpected_error(self):
        """Test CLI handling of unexpected errors."""
        with patch('php_framework_detector.cli.detect_frameworks_async') as mock_detect:
            mock_detect.side_effect = Exception("Unexpected error")
            
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    result = self.runner.invoke(app, ["detect", "/test/path"])
                    
                    assert result.exit_code == 1
                    assert "Unexpected error" in result.output 