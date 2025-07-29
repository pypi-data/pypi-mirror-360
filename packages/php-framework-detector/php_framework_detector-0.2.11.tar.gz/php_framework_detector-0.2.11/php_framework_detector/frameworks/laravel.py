"""
Laravel framework detector.

This module provides detection capabilities for Laravel PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class LaravelDetector(FrameworkDetector):
    """
    Detector for Laravel framework.
    
    Laravel is a web application framework with expressive, elegant syntax.
    It provides a robust set of tools for building modern web applications.
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "laravel"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Laravel"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "Modern PHP web application framework with elegant syntax"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Laravel detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0
        
        # Check for artisan file (highest confidence)
        if await self._check_path_patterns_async(["artisan"]):
            score += 100
        
        # Check for Laravel composer package
        if await self._check_composer_dependency_async("laravel/framework"):
            score += 20
        
        # Check for Laravel-specific content patterns
        if await self._check_file_content_async(
            "artisan",
            ["Laravel Framework", "Artisan Console Application"]
        ):
            score += 20
        
        # Check for .env file (common in Laravel projects)
        if await self._check_path_patterns_async([".env"]):
            score += 10
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Laravel."""
        return [
            "artisan",
            "app",
            "bootstrap",
            "config",
            ".env",
            "resources/views",
            "routes/web.php"
        ]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Laravel."""
        return [
            "laravel/framework",
            "laravel/laravel"
        ]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Laravel files."""
        return [
            "Laravel Framework",
            "Artisan Console Application",
            "Illuminate\\",
            "Route::",
            "DB::",
            "Auth::"
        ]
