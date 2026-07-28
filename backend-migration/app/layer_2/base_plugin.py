from abc import ABC, abstractmethod

class BasePlugin(ABC):
    name: str = ""
    version: str = "0.0.1"
    label: str = ""
    plugin_manager: "PluginManager"
    aliases : set[str] = {}
    priority_level : int = 100

    def set_plugin_manager(self, plugin_manager : "PluginManager"):
        self.plugin_manager = plugin_manager

    def on_load(self):
        """Called once when plugin is first loaded"""
        pass

    def on_unload(self):
        """Called when plugin is unloaded/app shuts down"""
        pass

    def __init_subclass__(cls, **kwargs):
        """
        This is called automatically whenever someone
        subclasses BasePlugin - even before instantiation
        """
        super().__init_subclass__(**kwargs)
        if cls.name == "":
            raise TypeError(f"{cls.__name__} must define a 'name' attribute")
