"""
Entry point for module execution.

This module allows the package to be executed directly with:
python -m php_framework_detector
"""

from .cli import app

if __name__ == "__main__":
    app() 