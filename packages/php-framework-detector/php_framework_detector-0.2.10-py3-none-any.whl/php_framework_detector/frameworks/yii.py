"""
Yii framework detector.

This module provides detection capabilities for Yii PHP framework,
including file pattern matching, composer dependency checking, and content analysis.
"""

from typing import List

from ..core.detector import FrameworkDetector


class YiiDetector(FrameworkDetector):
    """
    Detector for Yii framework.
    
    High-performance PHP framework for web applications
    """
    
    @property
    def name(self) -> str:
        """Return the framework identifier code."""
        return "yii"
    
    @property
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        return "Yii"
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return "High-performance PHP framework for web applications"
    
    async def _detect_async_impl(self) -> int:
        """
        Asynchronous Yii detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        score = 0

        # Check for Yii composer packages
        if await self._check_composer_dependency_async("yiisoft/yii2"):
            score += 100
        
        # Check for Yii-specific content patterns
        if await self._check_file_content_async(
            "protected/config/main.php",
            ["Yii::", "Yii2", "CApplication"]
        ):
            score += 20
        
        return min(score, 100)
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for Yii."""
        return ["protected", "index.php", "protected/config"]
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for Yii."""
        return ["yiisoft/yii", "yiisoft/yii2"]
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in Yii files."""
        return ["Yii::", "Yii2", "CApplication"]
