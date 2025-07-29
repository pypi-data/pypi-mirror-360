"""
Zend Framework framework detector.

This module provides detection capabilities for Zend Framework PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class ZendFrameworkDetector(FrameworkDetector):
    """
    Detector for Zend Framework framework.
    
    Enterprise PHP framework and component library
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "zendframework"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Zend Framework"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Enterprise PHP framework and component library"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Zend Framework detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0
        
        # Check for Zend Framework composer packages
        if await self._check_composer_dependency_async("zendframework/zendframework1"):
            score += 100
        
        # Check for Zend Framework-specific content patterns
        if await self._check_file_content_async(
            "application/configs/application.ini",
            ["Zend_", "Zend\\", "Zend_Application"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Zend Framework."""
        return ["application", "library", "application/config"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Zend Framework."""
        return ["zendframework/zendframework1"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Zend Framework files."""
        return ["Zend_", "Zend\\", "Zend_Application"]
