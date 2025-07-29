"""
Core framework detector base class.

This module provides the abstract base class for all framework detectors,
with modern async support, improved error handling, and comprehensive logging.
"""

import asyncio
import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import aiofiles
import structlog

from .exceptions import FileReadError, TimeoutError
from .models import DetectionConfig, FrameworkMetadata, FrameworkType

logger = structlog.get_logger()


class FrameworkDetector(ABC):
    """
    Abstract base class for all framework detectors.
    
    This class provides common functionality for detecting PHP frameworks,
    including async file operations, composer.json parsing, and pattern matching.
    """
    
    def __init__(self, project_path: str, config: Optional[DetectionConfig] = None) -> None:
        """
        Initialize the framework detector.
        
        Args:
            project_path: Path to the PHP project directory
            config: Optional detection configuration
        """
        self.project_path = Path(project_path).resolve()
        self.config = config or DetectionConfig()
        self._composer_data: Optional[Dict[str, Any]] = None
        self._file_cache: Dict[str, str] = {}
        
        logger.debug(
            "Initialized detector",
            framework=self.name,
            project_path=str(self.project_path)
        )
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the framework identifier code."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Return the human-readable framework name."""
        pass
    
    @property
    def description(self) -> str:
        """Return framework description."""
        return f"Detector for {self.display_name} framework"
    
    @property
    def metadata(self) -> FrameworkMetadata:
        """Return framework detection metadata."""
        return FrameworkMetadata(
            framework_type=FrameworkType.from_string(self.name),
            detection_methods=self._get_detection_methods(),
            file_patterns=self._get_file_patterns(),
            composer_packages=self._get_composer_packages(),
            content_patterns=self._get_content_patterns()
        )
    
    async def detect_async(self) -> int:
        """
        Asynchronous detection method with scoring.
        
        Returns:
            Detection score (0-100) where 100 indicates certain detection
        """
        try:
            # Run detection with timeout
            result = await asyncio.wait_for(
                self._detect_async_impl(),
                timeout=self.config.timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(
                "Detection timed out",
                framework=self.name,
                timeout=self.config.timeout
            )
            raise TimeoutError("framework detection", self.config.timeout)
        except Exception as e:
            logger.error(
                "Detection failed",
                framework=self.name,
                error=str(e)
            )
            return 0
    
    async def _detect_async_impl(self) -> int:
        """
        Internal async detection implementation.
        
        Returns:
            Detection score (0-100)
        """
        # Default implementation calls sync method
        return 100 if self.detect() else 0
    
    async def _load_composer_json_async(self) -> Dict[str, Any]:
        """
        Asynchronously load composer.json or composer.lock file.
        
        Returns:
            Parsed composer data as dictionary
        """
        if self._composer_data is not None:
            return self._composer_data
        
        composer_path = self.project_path / "composer.json"
        lock_path = self.project_path / "composer.lock"
        
        # Try composer.json first
        if composer_path.exists():
            try:
                async with aiofiles.open(composer_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    self._composer_data = json.loads(content)
                    logger.debug("Loaded composer.json", path=str(composer_path))
                    return self._composer_data
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"Failed to parse {composer_path}", error=str(e))
            except Exception as e:
                logger.warning(f"Failed to read {composer_path}", error=str(e))
        
        # Try composer.lock as fallback
        if lock_path.exists():
            try:
                async with aiofiles.open(lock_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    self._composer_data = json.loads(content)
                    logger.debug("Loaded composer.lock", path=str(lock_path))
                    return self._composer_data
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"Failed to parse {lock_path}", error=str(e))
            except Exception as e:
                logger.warning(f"Failed to read {lock_path}", error=str(e))
        
        self._composer_data = {}
        return {}
    
    async def _check_path_patterns_async(self, patterns: List[str]) -> bool:
        """
        Asynchronously check if any of the path patterns exist.
        
        Args:
            patterns: List of file/directory patterns to check
            
        Returns:
            True if any pattern exists, False otherwise
        """
        for pattern in patterns:
            path = self.project_path / pattern
            if path.exists():
                logger.debug("Found path pattern", pattern=pattern)
                return True
        return False
    
    async def _check_composer_dependency_async(self, package_name: str) -> bool:
        """
        Asynchronously check if a package is listed in composer dependencies.
        
        Args:
            package_name: Name of the composer package to check
            
        Returns:
            True if package is found in dependencies, False otherwise
        """
        composer_data = await self._load_composer_json_async()
        
        # Check require section
        if package_name in composer_data.get("require", {}):
            logger.debug("Found composer dependency", package=package_name)
            return True
        
        # Check require-dev section
        if package_name in composer_data.get("require-dev", {}):
            logger.debug("Found composer dev dependency", package=package_name)
            return True
        
        return False
    
    async def _check_file_content_async(
        self,
        file_path: Union[str, Path],
        content_patterns: List[str],
        max_size: Optional[int] = None
    ) -> bool:
        """
        Asynchronously check if a file contains specific content patterns.
        
        Args:
            file_path: Path to the file to check
            content_patterns: List of patterns to search for
            max_size: Maximum file size to read (uses config if None)
            
        Returns:
            True if any pattern is found, False otherwise
        """
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            return False
        
        # Check file size
        file_size = full_path.stat().st_size
        max_read_size = max_size or self.config.max_file_size
        
        if file_size > max_read_size:
            logger.debug(
                "File too large, skipping content check",
                file=str(full_path),
                size=file_size,
                max_size=max_read_size
            )
            return False
        
        try:
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
                for pattern in content_patterns:
                    if pattern in content:
                        logger.debug(
                            "Found content pattern",
                            file=str(full_path),
                            pattern=pattern
                        )
                        return True
                        
        except UnicodeDecodeError:
            logger.debug("File is not UTF-8 encoded, skipping content check", file=str(full_path))
        except Exception as e:
            logger.warning("Failed to read file for content check", file=str(full_path), error=str(e))
        
        return False
    
    async def _check_regex_patterns_async(
        self,
        file_path: Union[str, Path],
        regex_patterns: List[str],
        max_size: Optional[int] = None
    ) -> bool:
        """
        Asynchronously check if a file matches regex patterns.
        
        Args:
            file_path: Path to the file to check
            regex_patterns: List of regex patterns to match
            max_size: Maximum file size to read (uses config if None)
            
        Returns:
            True if any pattern matches, False otherwise
        """
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            return False
        
        # Check file size
        file_size = full_path.stat().st_size
        max_read_size = max_size or self.config.max_file_size
        
        if file_size > max_read_size:
            logger.debug(
                "File too large, skipping regex check",
                file=str(full_path),
                size=file_size,
                max_size=max_read_size
            )
            return False
        
        try:
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
                for pattern in regex_patterns:
                    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                        logger.debug(
                            "Found regex pattern",
                            file=str(full_path),
                            pattern=pattern
                        )
                        return True
                        
        except UnicodeDecodeError:
            logger.debug("File is not UTF-8 encoded, skipping regex check", file=str(full_path))
        except Exception as e:
            logger.warning("Failed to read file for regex check", file=str(full_path), error=str(e))
        
        return False
    
    def _get_detection_methods(self) -> List[str]:
        """Get list of detection methods used by this detector."""
        methods = []
        
        if self._get_file_patterns():
            methods.append("file_patterns")
        if self._get_composer_packages():
            methods.append("composer_packages")
        if self._get_content_patterns():
            methods.append("content_patterns")
        
        return methods
    
    def _get_file_patterns(self) -> List[str]:
        """Get file patterns to check for this framework."""
        return []
    
    def _get_composer_packages(self) -> List[str]:
        """Get composer package names to check for this framework."""
        return []
    
    def _get_content_patterns(self) -> List[str]:
        """Get content patterns to search for in files."""
        return []
    
    def _load_composer_json(self) -> dict:
        """
        Load composer.json file synchronously for backward compatibility.
        Returns:
            Parsed composer data as dictionary
        """
        composer_path = self.project_path / "composer.json"
        if composer_path.exists():
            try:
                with open(composer_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {} 