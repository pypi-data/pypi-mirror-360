from daydream.knowledge import Node
from daydream.utils import import_submodules

from .base import REGISTRY, Plugin, PluginCapability, PluginManager

# Autoload all plugins in the plugins directory
import_submodules("daydream.plugins")

__all__ = ["REGISTRY", "Node", "Plugin", "PluginCapability", "PluginManager"]
