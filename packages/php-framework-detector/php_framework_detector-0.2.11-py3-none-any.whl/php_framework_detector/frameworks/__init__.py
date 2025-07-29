"""
Framework detectors module.

This module contains all framework detector implementations and automatically
registers them with the FrameworkDetectorFactory.
"""

from .laravel import LaravelDetector
from .symfony import SymfonyDetector
from .codeigniter import CodeIgniterDetector
from .cakephp import CakePHPDetector
from .yii import YiiDetector
from .thinkphp import ThinkPHPDetector
from .slim import SlimDetector
from .fuel import FuelDetector
from .phalcon import PhalconDetector
from .laminas import LaminasDetector
from .zendframework import ZendFrameworkDetector
from .drupal import DrupalDetector
from .drush import DrushDetector
from .fatfree import FatFreeDetector
from .phpixie import PHPixieDetector
from .popphp import PopPHPDetector
from .fastroute import FastRouteDetector

# Import the factory to trigger registration
from ..core.factory import FrameworkDetectorFactory

# Register all detectors
FrameworkDetectorFactory.register_detector(LaravelDetector)
FrameworkDetectorFactory.register_detector(SymfonyDetector)
FrameworkDetectorFactory.register_detector(CodeIgniterDetector)
FrameworkDetectorFactory.register_detector(CakePHPDetector)
FrameworkDetectorFactory.register_detector(YiiDetector)
FrameworkDetectorFactory.register_detector(ThinkPHPDetector)
FrameworkDetectorFactory.register_detector(SlimDetector)
FrameworkDetectorFactory.register_detector(FuelDetector)
FrameworkDetectorFactory.register_detector(PhalconDetector)
FrameworkDetectorFactory.register_detector(LaminasDetector)
FrameworkDetectorFactory.register_detector(ZendFrameworkDetector)
FrameworkDetectorFactory.register_detector(DrupalDetector)
FrameworkDetectorFactory.register_detector(DrushDetector)
FrameworkDetectorFactory.register_detector(FatFreeDetector)
FrameworkDetectorFactory.register_detector(PHPixieDetector)
FrameworkDetectorFactory.register_detector(PopPHPDetector)
FrameworkDetectorFactory.register_detector(FastRouteDetector)

__all__ = [
    "LaravelDetector",
    "SymfonyDetector", 
    "CodeIgniterDetector",
    "CakePHPDetector",
    "YiiDetector",
    "ThinkPHPDetector",
    "SlimDetector",
    "FuelDetector",
    "PhalconDetector",
    "LaminasDetector",
    "ZendFrameworkDetector",
    "DrupalDetector",
    "DrushDetector",
    "FatFreeDetector",
    "PHPixieDetector",
    "PopPHPDetector",
    "FastRouteDetector",
] 