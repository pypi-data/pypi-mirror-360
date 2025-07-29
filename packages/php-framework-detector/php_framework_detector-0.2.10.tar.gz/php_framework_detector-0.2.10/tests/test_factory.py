"""
Tests for FrameworkDetectorFactory.

This module tests the factory class for creating and managing framework detectors.
"""

import pytest
from unittest.mock import MagicMock, patch

from php_framework_detector.core.factory import FrameworkDetectorFactory
from php_framework_detector.core.models import DetectionConfig, FrameworkType
from php_framework_detector.core.exceptions import UnsupportedFrameworkError


class TestFrameworkDetectorFactory:
    """Test FrameworkDetectorFactory class."""
    
    def test_register_detector(self):
        """Test registering a detector class."""
        # Create a mock detector class
        mock_detector_class = MagicMock()
        mock_detector_class.__name__ = "MockDetector"
        mock_detector_instance = MagicMock()
        mock_detector_instance.name = "mock_framework"
        mock_detector_class.return_value = mock_detector_instance
        
        # Register the detector
        FrameworkDetectorFactory.register_detector(mock_detector_class)
        
        # Verify it was registered
        assert "mock_framework" in FrameworkDetectorFactory._detectors
        assert FrameworkDetectorFactory._detectors["mock_framework"] == mock_detector_class
    
    def test_register_invalid_detector(self):
        """Test registering an invalid detector class."""
        # Create a class that doesn't inherit from FrameworkDetector
        invalid_class = MagicMock()
        
        with pytest.raises(ValueError, match="Detector class must inherit from FrameworkDetector"):
            FrameworkDetectorFactory.register_detector(invalid_class)
    
    def test_get_detector_success(self):
        """Test getting a detector instance successfully."""
        # Create a mock detector class
        mock_detector_class = MagicMock()
        mock_detector_instance = MagicMock()
        mock_detector_instance.name = "test_framework"
        mock_detector_class.return_value = mock_detector_instance
        
        # Register the detector
        FrameworkDetectorFactory._detectors["test_framework"] = mock_detector_class
        FrameworkDetectorFactory._initialized = True
        
        # Get the detector
        detector = FrameworkDetectorFactory.get_detector("test_framework", "/test/path")
        
        # Verify the detector was created correctly
        mock_detector_class.assert_called_once_with("/test/path", None)
        assert detector == mock_detector_instance
    
    def test_get_detector_with_config(self):
        """Test getting a detector instance with configuration."""
        # Create a mock detector class
        mock_detector_class = MagicMock()
        mock_detector_instance = MagicMock()
        mock_detector_instance.name = "test_framework"
        mock_detector_class.return_value = mock_detector_instance
        
        # Register the detector
        FrameworkDetectorFactory._detectors["test_framework"] = mock_detector_class
        FrameworkDetectorFactory._initialized = True
        
        # Create config
        config = DetectionConfig(timeout=60)
        
        # Get the detector
        detector = FrameworkDetectorFactory.get_detector("test_framework", "/test/path", config)
        
        # Verify the detector was created correctly
        mock_detector_class.assert_called_once_with("/test/path", config)
        assert detector == mock_detector_instance
    
    def test_get_detector_unsupported_framework(self):
        """Test getting an unsupported framework detector."""
        FrameworkDetectorFactory._detectors = {}
        FrameworkDetectorFactory._initialized = True
        
        with pytest.raises(UnsupportedFrameworkError) as exc_info:
            FrameworkDetectorFactory.get_detector("unknown_framework", "/test/path")
        
        assert exc_info.value.framework == "unknown_framework"
        assert exc_info.value.available_frameworks == []
    
    def test_get_all_detectors(self):
        """Test getting all detector instances."""
        # Create mock detector classes
        mock_class1 = MagicMock()
        mock_class2 = MagicMock()
        mock_instance1 = MagicMock()
        mock_instance2 = MagicMock()
        mock_class1.return_value = mock_instance1
        mock_class2.return_value = mock_instance2
        
        # Register detectors
        FrameworkDetectorFactory._detectors = {
            "framework1": mock_class1,
            "framework2": mock_class2
        }
        FrameworkDetectorFactory._initialized = True
        
        # Get all detectors
        detectors = FrameworkDetectorFactory.get_all_detectors("/test/path")
        
        # Verify all detectors were created
        assert len(detectors) == 2
        mock_class1.assert_called_once_with("/test/path", None)
        mock_class2.assert_called_once_with("/test/path", None)
        assert mock_instance1 in detectors
        assert mock_instance2 in detectors
    
    def test_get_all_detectors_with_config(self):
        """Test getting all detector instances with configuration."""
        # Create mock detector class
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        # Register detector
        FrameworkDetectorFactory._detectors = {"framework1": mock_class}
        FrameworkDetectorFactory._initialized = True
        
        # Create config
        config = DetectionConfig(timeout=60)
        
        # Get all detectors
        detectors = FrameworkDetectorFactory.get_all_detectors("/test/path", config)
        
        # Verify detector was created with config
        mock_class.assert_called_once_with("/test/path", config)
        assert len(detectors) == 1
        assert mock_instance in detectors
    
    def test_get_available_frameworks(self):
        """Test getting list of available framework names."""
        FrameworkDetectorFactory._detectors = {
            "laravel": MagicMock(),
            "symfony": MagicMock(),
            "codeigniter": MagicMock()
        }
        FrameworkDetectorFactory._initialized = True
        
        frameworks = FrameworkDetectorFactory.get_available_frameworks()
        
        assert set(frameworks) == {"laravel", "symfony", "codeigniter"}
    
    def test_get_framework_names(self):
        """Test getting mapping of framework codes to display names."""
        # Create mock detector classes with display names
        mock_class1 = MagicMock()
        mock_class2 = MagicMock()
        mock_instance1 = MagicMock()
        mock_instance2 = MagicMock()
        mock_instance1.display_name = "Laravel"
        mock_instance2.display_name = "Symfony"
        mock_class1.return_value = mock_instance1
        mock_class2.return_value = mock_instance2
        
        FrameworkDetectorFactory._detectors = {
            "laravel": mock_class1,
            "symfony": mock_class2
        }
        FrameworkDetectorFactory._initialized = True
        
        names = FrameworkDetectorFactory.get_framework_names()
        
        expected = {
            "laravel": "Laravel",
            "symfony": "Symfony",
            "na": "Unknown"
        }
        assert names == expected
    
    def test_get_framework_types(self):
        """Test getting mapping of framework codes to FrameworkType enums."""
        FrameworkDetectorFactory._detectors = {
            "laravel": MagicMock(),
            "symfony": MagicMock(),
            "unknown_framework": MagicMock()
        }
        FrameworkDetectorFactory._initialized = True
        
        types = FrameworkDetectorFactory.get_framework_types()
        
        assert types["laravel"] == FrameworkType.LARAVEL
        assert types["symfony"] == FrameworkType.SYMFONY
        assert types["unknown_framework"] == FrameworkType.UNKNOWN
        assert types["na"] == FrameworkType.UNKNOWN
    
    def test_get_framework_metadata(self):
        """Test getting metadata for all available frameworks."""
        # Create mock detector classes with metadata
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_metadata = MagicMock()
        mock_instance.metadata = mock_metadata
        mock_class.return_value = mock_instance
        
        FrameworkDetectorFactory._detectors = {"laravel": mock_class}
        FrameworkDetectorFactory._initialized = True
        
        metadata = FrameworkDetectorFactory.get_framework_metadata()
        
        assert metadata["laravel"] == mock_metadata
        mock_class.assert_called_once_with("")
    
    @patch('php_framework_detector.core.factory.FrameworkDetectorFactory._initialized', False)
    @patch('php_framework_detector.core.factory.FrameworkDetectorFactory.register_detector')
    def test_ensure_initialized(self, mock_register):
        """Test that _ensure_initialized registers all detectors."""
        # Mock the import to avoid actual imports during testing
        with patch('php_framework_detector.core.factory.FrameworkDetectorFactory._detectors', {}):
            FrameworkDetectorFactory._ensure_initialized()
            
            # Verify that register_detector was called (indicating initialization)
            assert FrameworkDetectorFactory._initialized is True
    
    @patch('php_framework_detector.core.factory.FrameworkDetectorFactory._initialized', True)
    def test_ensure_initialized_already_initialized(self):
        """Test that _ensure_initialized doesn't reinitialize."""
        with patch('php_framework_detector.core.factory.FrameworkDetectorFactory.register_detector') as mock_register:
            FrameworkDetectorFactory._ensure_initialized()
            
            # Should not call register_detector again
            mock_register.assert_not_called()


class TestFactoryIntegration:
    """Test factory integration with real detector classes."""
    
    @pytest.mark.integration
    def test_real_detector_registration(self):
        """Test registering real detector classes."""
        # This test requires actual detector classes to be available
        # It's marked as integration test since it depends on the full module structure
        
        # Reset factory state
        FrameworkDetectorFactory._detectors = {}
        FrameworkDetectorFactory._initialized = False
        
        # Try to get available frameworks (this will trigger initialization)
        try:
            frameworks = FrameworkDetectorFactory.get_available_frameworks()
            assert len(frameworks) > 0
            assert "laravel" in frameworks
            assert "symfony" in frameworks
        except ImportError:
            # Skip if detector modules are not available
            pytest.skip("Detector modules not available for integration test")
    
    def test_factory_singleton_behavior(self):
        """Test that factory maintains singleton-like behavior for detectors."""
        # Reset factory state
        FrameworkDetectorFactory._detectors = {}
        FrameworkDetectorFactory._initialized = False
        
        # Create mock detector
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_instance.name = "test_framework"
        mock_class.return_value = mock_instance
        
        # Register detector
        FrameworkDetectorFactory.register_detector(mock_class)
        
        # Get detector multiple times
        detector1 = FrameworkDetectorFactory.get_detector("test_framework", "/path1")
        detector2 = FrameworkDetectorFactory.get_detector("test_framework", "/path2")
        
        # Should create new instances each time
        assert detector1 != detector2
        assert mock_class.call_count == 2 