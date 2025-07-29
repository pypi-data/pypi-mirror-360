"""
ThinkPHP framework detector.

This module provides detection capabilities for ThinkPHP PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class ThinkPHPDetector(FrameworkDetector):
    """
    Detector for ThinkPHP framework.
    
    Chinese PHP framework for web development
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "thinkphp"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "ThinkPHP"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Chinese PHP framework for web development"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous ThinkPHP detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for ThinkPHP composer packages
        if await self._check_composer_dependency_async("topthink/framework"):
            score += 100

        # Check for ThinkPHP-specific content patterns
        if await self._check_file_content_async(
            "application/config.php",
            ["ThinkPHP", "think\\", "App::"]
        ):
            score += 20

        # Check for "ThinkPHP" in public/index.php
        if await self._check_file_content_async(
            "public/index.php",
            ["ThinkPHP"]
        ):
            score += 20

        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for ThinkPHP."""
        return ["application", "thinkphp", "application/config"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for ThinkPHP."""
        return ["topthink/framework"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in ThinkPHP files."""
        return ["ThinkPHP", "think\\", "App::"]
