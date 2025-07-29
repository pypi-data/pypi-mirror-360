"""
Slim framework detector.

This module provides detection capabilities for Slim PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class SlimDetector(FrameworkDetector):
    """
    Detector for Slim framework.
    
    Lightweight PHP micro-framework
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "slim"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Slim"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Lightweight PHP micro-framework"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Slim detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0
        
        # Check for Slim composer packages
        if await self._check_composer_dependency_async("slim/slim"):
            score += 100
        
        # Check for Slim-specific content patterns
        if await self._check_file_content_async(
            "index.php",
            ["Slim\\", "use Slim\\", "$app = new Slim\\"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Slim."""
        return ["index.php", "composer.json"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Slim."""
        return ["slim/slim", "slim/slim4"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Slim files."""
        return ["Slim\\", "use Slim\\", "$app = new Slim\\"]
