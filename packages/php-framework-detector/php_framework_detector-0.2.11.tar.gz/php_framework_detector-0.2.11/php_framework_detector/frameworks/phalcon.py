"""
Phalcon framework detector.

This module provides detection capabilities for Phalcon PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class PhalconDetector(FrameworkDetector):
    """
    Detector for Phalcon framework.
    
    Full-stack PHP framework delivered as a C extension
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "phalcon"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Phalcon"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Full-stack PHP framework delivered as a C extension"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Phalcon detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for Phalcon composer packages
        if await self._check_composer_dependency_async("phalcon/incubator"):
            score += 100
        
        # Check for Phalcon-specific content patterns
        if await self._check_file_content_async(
            "app/config/config.php",
            ["Phalcon\\", "use Phalcon\\", "new Phalcon\\"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Phalcon."""
        return ["app", "public", "app/config"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Phalcon."""
        return ["phalcon/incubator"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Phalcon files."""
        return ["Phalcon\\", "use Phalcon\\", "new Phalcon\\"]
