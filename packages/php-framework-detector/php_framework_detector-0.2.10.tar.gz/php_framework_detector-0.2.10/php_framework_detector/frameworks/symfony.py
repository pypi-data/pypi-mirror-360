"""
Symfony framework detector.

This module provides detection capabilities for Symfony PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class SymfonyDetector(FrameworkDetector):
    """
    Detector for Symfony framework.
    
    Symfony is a set of reusable PHP components and a web application framework.
    It provides a set of tools and libraries for building web applications.
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "symfony"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Symfony"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "PHP web application framework and component library"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Symfony detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0
                
        # Check for symfony.lock file (highest confidence)
        if await self._check_path_patterns_async(["symfony.lock"]):
            score += 100

        # Check for Symfony composer packages
        if await self._check_composer_dependency_async("symfony/symfony"):
            score += 25
        elif await self._check_composer_dependency_async("symfony/framework-bundle"):
            score += 20
        
        # Check for Symfony-specific content patterns
        if await self._check_file_content_async(
            "config/services.yaml",
            ["services:", "Symfony\\"]
        ):
            score += 15
        
        # Check for .env.local file (common in Symfony projects)
        if await self._check_path_patterns_async([".env.local"]):
            score += 10
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Symfony."""
        return [
            "symfony.lock",
            "src",
            "config",
            "var",
            ".env.local",
            "public/index.php",
            "bin/console"
        ]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Symfony."""
        return [
            "symfony/symfony",
            "symfony/framework-bundle",
            "symfony/console",
            "symfony/http-foundation"
        ]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Symfony files."""
        return [
            "Symfony\\",
            "services:",
            "framework:",
            "doctrine:",
            "App\\",
            "use Symfony\\"
        ]
