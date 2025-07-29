"""
Drush framework detector.

This module provides detection capabilities for Drush PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class DrushDetector(FrameworkDetector):
    """
    Detector for Drush framework.
    
    Command-line shell and scripting interface for Drupal
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "drush"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Drush"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Command-line shell and scripting interface for Drupal"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Drush detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0
        
        # Check for Drush-specific files
        if await self._check_path_patterns_async(["drush", "drush/commands"]):
            score += 100
        
        # Check for Drush composer packages
        if await self._check_composer_dependency_async("drush/drush"):
            score += 100
        
        # Check for Drush-specific content patterns
        if await self._check_file_content_async(
            "drush/drush.php",
            ["drush_", "Drush\\", "drush_invoke"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Drush."""
        return ["drush", "drush/commands"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Drush."""
        return ["drush/drush"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Drush files."""
        return ["drush_", "Drush\\", "drush_invoke"]
