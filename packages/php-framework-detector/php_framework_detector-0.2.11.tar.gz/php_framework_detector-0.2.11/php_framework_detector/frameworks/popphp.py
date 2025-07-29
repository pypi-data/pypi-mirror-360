"""
PopPHP framework detector.

This module provides detection capabilities for PopPHP PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class PopPHPDetector(FrameworkDetector):
    """
    Detector for PopPHP framework.
    
    PHP framework for rapid application development
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "popphp"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "PopPHP"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "PHP framework for rapid application development"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous PopPHP detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for PopPHP composer packages
        if await self._check_composer_dependency_async("popphp/pop"):
            score += 100
        
        # Check for PopPHP-specific content patterns
        if await self._check_file_content_async(
            "public/index.php",
            ["Pop\\", "use Pop\\", "new Pop\\"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for PopPHP."""
        return ["app", "public", "app/config"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for PopPHP."""
        return ["popphp/pop"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in PopPHP files."""
        return ["Pop\\", "use Pop\\", "new Pop\\"]
