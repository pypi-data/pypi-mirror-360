"""
DevOps AI EventBridge Module

A module for creating AWS EventBridge rules from natural language descriptions.
Converts text input to cron expressions and manages AWS EventBridge rules.
"""

__version__ = "0.1.0"
__author__ = "CosmicFusionLabs"

from .core import EventBridgeManager
from .cron_converter import CronConverter
from .cli import app

__all__ = ["EventBridgeManager", "CronConverter", "app"] 