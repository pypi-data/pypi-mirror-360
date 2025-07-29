"""
CodeIgniter framework detector.

This module provides detection capabilities for CodeIgniter PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class CodeIgniterDetector(FrameworkDetector):
    """
    Detector for CodeIgniter framework.
    
    Lightweight PHP framework for rapid web development
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "codeigniter"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "CodeIgniter"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Lightweight PHP framework for rapid web development"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous CodeIgniter detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for CodeIgniter composer packages
        if await self._check_composer_dependency_async("codeigniter/framework"):
            score += 100
        
        # Check for CodeIgniter-specific content patterns
        if await self._check_file_content_async(
            "index.php",
            ["CodeIgniter", "CI_", "defined('BASEPATH')"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for CodeIgniter."""
        return ["index.php", "application", "system", "application/config"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for CodeIgniter."""
        return ["codeigniter/framework", "codeigniter4/framework"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in CodeIgniter files."""
        return ["CodeIgniter", "CI_", "defined('BASEPATH')"]

