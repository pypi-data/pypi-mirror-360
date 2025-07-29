"""
Fat-Free framework detector.

This module provides detection capabilities for Fat-Free PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class FatFreeDetector(FrameworkDetector):
    """
    Detector for Fat-Free framework.
    
    Lightweight PHP framework with minimal footprint
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "fatfree"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Fat-Free"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Lightweight PHP framework with minimal footprint"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Fat-Free detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0
        
        # Check for Fat-Free composer packages
        if await self._check_composer_dependency_async("bcosca/fatfree-core"):
            score += 100
        
        # Check for Fat-Free-specific content patterns
        if await self._check_file_content_async(
            "index.php",
            ["F3::", "Base::", "new F3"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Fat-Free."""
        return ["lib", "index.php", "lib/base.php"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Fat-Free."""
        return ["bcosca/fatfree-core"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Fat-Free files."""
        return ["F3::", "Base::", "new F3"]
