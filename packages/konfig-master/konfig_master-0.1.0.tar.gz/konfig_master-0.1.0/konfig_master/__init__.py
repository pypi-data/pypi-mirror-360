# config_master/__init__.py
"""
config-master: A simple, unified interface for managing application configuration.
"""

__version__ = "0.1.0"

from .core import load

__all__ = ['load']