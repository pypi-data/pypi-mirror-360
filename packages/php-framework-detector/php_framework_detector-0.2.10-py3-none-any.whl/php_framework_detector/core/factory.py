"""
Factory for creating framework detectors.

This module provides a factory class for managing and creating framework detectors,
with support for async operations and improved error handling.
"""

import asyncio
from typing import Dict, List, Optional, Type
import structlog

from .detector import FrameworkDetector
from .exceptions import UnsupportedFrameworkError
from .models import DetectionConfig, FrameworkMetadata, FrameworkType

logger = structlog.get_logger()


class FrameworkDetectorFactory:
    """
    Factory class for creating and managing framework detectors.
    
    This class provides a centralized way to create detector instances,
    manage available frameworks, and perform batch detection operations.
    """
    
    _detectors: Dict[str, Type[FrameworkDetector]] = {}
    _initialized = False
    
    @classmethod
    def register_detector(cls, detector_class: Type[FrameworkDetector]) -> None:
        """
        Register a framework detector class.
        
        Args:
            detector_class: The detector class to register
        """
        if not issubclass(detector_class, FrameworkDetector):
            raise ValueError(f"Detector class must inherit from FrameworkDetector: {detector_class}")
        
        detector_name = detector_class("").name
        cls._detectors[detector_name] = detector_class
        
        logger.debug("Registered detector", framework=detector_name)
    
    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure all detectors are registered."""
        if cls._initialized:
            return
        
        # Import all detector modules to trigger registration
        try:
            from ..frameworks import (
                LaravelDetector, SymfonyDetector, CodeIgniterDetector,
                CakePHPDetector, YiiDetector, ThinkPHPDetector,
                SlimDetector, FuelDetector, PhalconDetector,
                LaminasDetector, ZendFrameworkDetector, DrupalDetector,
                DrushDetector, FatFreeDetector, PHPixieDetector,
                PopPHPDetector, FastRouteDetector
            )
            
            # Register all detectors
            detectors = [
                LaravelDetector, SymfonyDetector, CodeIgniterDetector,
                CakePHPDetector, YiiDetector, ThinkPHPDetector,
                SlimDetector, FuelDetector, PhalconDetector,
                LaminasDetector, ZendFrameworkDetector, DrupalDetector,
                DrushDetector, FatFreeDetector, PHPixieDetector,
                PopPHPDetector, FastRouteDetector
            ]
            
            for detector in detectors:
                cls.register_detector(detector)
            
            cls._initialized = True
            logger.debug("Initialized framework detector factory", count=len(detectors))
            
        except ImportError as e:
            logger.error("Failed to import detector modules", error=str(e))
            raise
    
    @classmethod
    def get_detector(
        cls,
        framework_name: str,
        project_path: str,
        config: Optional[DetectionConfig] = None
    ) -> FrameworkDetector:
        """
        Get a detector instance for the specified framework.
        
        Args:
            framework_name: Name of the framework to detect
            project_path: Path to the project directory
            config: Optional detection configuration
            
        Returns:
            FrameworkDetector instance
            
        Raises:
            UnsupportedFrameworkError: If framework is not supported
        """
        cls._ensure_initialized()
        
        if framework_name not in cls._detectors:
            available = list(cls._detectors.keys())
            raise UnsupportedFrameworkError(framework_name, available)
        
        detector_class = cls._detectors[framework_name]
        return detector_class(project_path, config)
    
    @classmethod
    def get_all_detectors(
        cls,
        project_path: str,
        config: Optional[DetectionConfig] = None
    ) -> List[FrameworkDetector]:
        """
        Get all detector instances.
        
        Args:
            project_path: Path to the project directory
            config: Optional detection configuration
            
        Returns:
            List of all FrameworkDetector instances
        """
        cls._ensure_initialized()
        
        detectors = []
        for detector_class in cls._detectors.values():
            detector = detector_class(project_path, config)
            detectors.append(detector)
        
        return detectors
    
    @classmethod
    def get_available_frameworks(cls) -> List[str]:
        """
        Get list of available framework names.
        
        Returns:
            List of framework identifier codes
        """
        cls._ensure_initialized()
        return list(cls._detectors.keys())
    
    @classmethod
    def get_framework_names(cls) -> Dict[str, str]:
        """
        Get mapping of framework codes to display names.
        
        Returns:
            Dictionary mapping framework codes to display names
        """
        cls._ensure_initialized()
        
        names = {}
        for framework_name in cls._detectors:
            detector = cls._detectors[framework_name]("")
            names[framework_name] = detector.display_name
        names["na"] = "Unknown"
        
        return names
    
    @classmethod
    def get_framework_types(cls) -> Dict[str, FrameworkType]:
        """
        Get mapping of framework codes to FrameworkType enums.
        
        Returns:
            Dictionary mapping framework codes to FrameworkType enums
        """
        cls._ensure_initialized()
        
        types = {}
        for framework_name in cls._detectors:
            types[framework_name] = FrameworkType.from_string(framework_name)
        types["na"] = FrameworkType.UNKNOWN
        
        return types
    
    @classmethod
    def get_framework_metadata(cls) -> Dict[str, FrameworkMetadata]:
        """
        Get metadata for all available frameworks.
        
        Returns:
            Dictionary mapping framework codes to metadata
        """
        cls._ensure_initialized()
        
        metadata = {}
        for framework_name in cls._detectors:
            detector = cls._detectors[framework_name]("")
            metadata[framework_name] = detector.metadata
        
        return metadata
    
    @classmethod
    async def detect_all_frameworks_async(
        cls,
        project_path: str,
        config: Optional[DetectionConfig] = None
    ) -> Dict[FrameworkType, int]:
        """
        Asynchronously detect all frameworks in parallel.
        
        Args:
            project_path: Path to the project directory
            config: Optional detection configuration
            
        Returns:
            Dictionary mapping framework types to detection scores
        """
        detectors = cls.get_all_detectors(project_path, config)
        
        # Create detection tasks
        tasks = []
        for detector in detectors:
            task = asyncio.create_task(detector.detect_async())
            tasks.append((detector.name, task))
        
        # Wait for all detections to complete
        results = {}
        for framework_name, task in tasks:
            try:
                score = await task
                framework_type = FrameworkType.from_string(framework_name)
                results[framework_type] = score
            except Exception as e:
                logger.error(
                    "Detection failed for framework",
                    framework=framework_name,
                    error=str(e)
                )
                framework_type = FrameworkType.from_string(framework_name)
                results[framework_type] = 0
        
        return results 