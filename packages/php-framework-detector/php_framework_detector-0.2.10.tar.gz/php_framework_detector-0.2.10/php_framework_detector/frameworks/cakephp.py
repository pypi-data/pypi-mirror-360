"""
CakePHP framework detector.

This module provides detection capabilities for CakePHP PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class CakePHPDetector(FrameworkDetector):
    """
    Detector for CakePHP framework.
    
    Rapid development framework for PHP
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "cakephp"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "CakePHP"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Rapid development framework for PHP"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous CakePHP detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for CakePHP composer packages
        if await self._check_composer_dependency_async("cakephp/cakephp"):
            score += 100
        
        # Check for CakePHP-specific content patterns
        if await self._check_file_content_async(
            "app/Config/core.php",
            ["CakePHP", "Configure::", "App::"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for CakePHP."""
        return ["app", "lib", "app/Config", "app/Controller"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for CakePHP."""
        return ["cakephp/cakephp"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in CakePHP files."""
        return ["CakePHP", "Configure::", "App::"]
