"""
Drupal framework detector.

This module provides detection capabilities for Drupal PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class DrupalDetector(FrameworkDetector):
    """
    Detector for Drupal framework.
    
    Content management system and web application framework
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "drupal"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Drupal"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Drupal detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for Drupal composer packages
        if await self._check_composer_dependency_async("drupal/core"):
            score += 100
        
        # Check for Drupal-specific content patterns
        if await self._check_file_content_async(
            "sites/default/settings.php",
            ["Drupal\\", "use Drupal\\", "drupal_get_path"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Drupal."""
        return ["sites", "modules", "themes", "sites/default"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Drupal."""
        return ["drupal/core", "drupal/drupal"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Drupal files."""
        return ["Drupal\\", "use Drupal\\", "drupal_get_path"]
