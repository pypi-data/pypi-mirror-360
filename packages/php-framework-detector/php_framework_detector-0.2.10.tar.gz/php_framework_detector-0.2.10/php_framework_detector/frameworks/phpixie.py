"""
PHPixie framework detector.

This module provides detection capabilities for PHPixie PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class PHPixieDetector(FrameworkDetector):
    """
    Detector for PHPixie framework.
    
    Lightweight PHP framework for web applications
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "phpixie"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "PHPixie"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Lightweight PHP framework for web applications"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous PHPixie detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for PHPixie composer packages
        if await self._check_composer_dependency_async("phpixie/framework"):
            score += 100
        
        # Check for PHPixie-specific content patterns
        if await self._check_file_content_async(
            "web/index.php",
            ["PHPixie\\", "use PHPixie\\", "new PHPixie\\"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for PHPixie."""
        return ["web", "vendor", "web/index.php"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for PHPixie."""
        return ["phpixie/framework"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in PHPixie files."""
        return ["PHPixie\\", "use PHPixie\\", "new PHPixie\\"]
