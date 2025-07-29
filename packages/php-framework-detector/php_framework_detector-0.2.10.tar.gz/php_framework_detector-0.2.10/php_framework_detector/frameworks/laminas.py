"""
Laminas framework detector.

This module provides detection capabilities for Laminas PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class LaminasDetector(FrameworkDetector):
    """
    Detector for Laminas framework.
    
    Enterprise-ready PHP framework and component library
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "laminas"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Laminas"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Enterprise-ready PHP framework and component library"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Laminas detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for Laminas composer packages
        if await self._check_composer_dependency_async("laminas/laminas-mvc"):
            score += 100
        
        # Check for Laminas-specific content patterns
        if await self._check_file_content_async(
            "config/application.config.php",
            ["Laminas\\", "use Laminas\\", "Zend\\"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Laminas."""
        return ["config", "module", "public"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Laminas."""
        return ["laminas/laminas-mvc", "laminas/laminas-framework"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Laminas files."""
        return ["Laminas\\", "use Laminas\\", "Zend\\"]
