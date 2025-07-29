"""
Fuel framework detector.

This module provides detection capabilities for Fuel PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class FuelDetector(FrameworkDetector):
    """
    Detector for Fuel framework.
    
    PHP 5.3+ framework for web applications
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "fuel"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Fuel"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "PHP 5.3+ framework for web applications"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Fuel detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for Fuel composer packages
        if await self._check_composer_dependency_async("fuel/core"):
            score += 100
        
        # Check for Fuel-specific content patterns
        if await self._check_file_content_async(
            "fuel/app/config/config.php",
            ["Fuel\\", "Fuel::", "Config::"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Fuel."""
        return ["fuel", "app", "fuel/app"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Fuel."""
        return ["fuel/core"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Fuel files."""
        return ["Fuel\\", "Fuel::", "Config::"]
