"""
Plugin system for Evolvishub Data Handler.

This module provides a comprehensive plugin architecture that allows:
1. Dynamic adapter registration
2. Data transformation pipelines
3. Custom middleware components
4. Event hooks and callbacks
5. External plugin loading
"""

from .base import BasePlugin, PluginType, PluginRegistry
from .adapters import AdapterPlugin
from .transformers import TransformerPlugin, DataTransformer
from .middleware import MiddlewarePlugin, BaseMiddleware
from .hooks import HookPlugin, EventHook
from .manager import PluginManager

__all__ = [
    'BasePlugin',
    'PluginType', 
    'PluginRegistry',
    'AdapterPlugin',
    'TransformerPlugin',
    'DataTransformer',
    'MiddlewarePlugin',
    'BaseMiddleware',
    'HookPlugin',
    'EventHook',
    'PluginManager'
]
