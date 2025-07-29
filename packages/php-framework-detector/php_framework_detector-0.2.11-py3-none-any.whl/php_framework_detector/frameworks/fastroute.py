"""
FastRoute framework detector.

This module provides detection capabilities for FastRoute PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class FastRouteDetector(FrameworkDetector):
    """
    Detector for FastRoute framework.
    
    Fast request router for PHP
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "fastroute"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "FastRoute"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Fast request router for PHP"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous FastRoute detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0
        
        # Check for FastRoute composer packages
        if await self._check_composer_dependency_async("nikic/fast-route"):
            score += 100
        
        # Check for FastRoute-specific content patterns
        if await self._check_file_content_async(
            "index.php",
            ["FastRoute\\", "use FastRoute\\", "FastRoute\\"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for FastRoute."""
        return ["index.php", "composer.json"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for FastRoute."""
        return ["nikic/fast-route"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in FastRoute files."""
        return ["FastRoute\\", "use FastRoute\\", "FastRoute\\"]
    