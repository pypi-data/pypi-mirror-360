# hiplt/plugins.py

import importlib.util
import os
import traceback

class PluginManager:
    def __init__(self, folder="plugins"):
        self.folder = folder
        self.plugins = {}  # name: module
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def load_all(self):
        for file in os.listdir(self.folder):
            if file.endswith(".py"):
                name = file[:-3]
                path = os.path.join(self.folder, file)
                self.load_plugin(name, path)

    def load_plugin(self, name, path=None):
        if path is None:
            path = os.path.join(self.folder, f"{name}.py")

        if not os.path.isfile(path):
            print(f"[PluginManager] Плагин {name} не найден по пути {path}")
            return False

        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Вызов on_load() если есть
            if hasattr(mod, "on_load"):
                mod.on_load()

            self.plugins[name] = mod
            print(f"[PluginManager] Плагин {name} успешно загружен.")
            return True
        except Exception as e:
            print(f"[PluginManager] Ошибка загрузки плагина {name}:\n{traceback.format_exc()}")
            return False

    def unload_plugin(self, name):
        if name not in self.plugins:
            print(f"[PluginManager] Плагин {name} не загружен.")
            return False

        try:
            mod = self.plugins[name]
            if hasattr(mod, "on_unload"):
                mod.on_unload()
            del self.plugins[name]
            print(f"[PluginManager] Плагин {name} выгружен.")
            return True
        except Exception as e:
            print(f"[PluginManager] Ошибка при выгрузке {name}:\n{traceback.format_exc()}")
            return False

    def reload_plugin(self, name):
        if name in self.plugins:
            self.unload_plugin(name)
        return self.load_plugin(name)

    def get_plugin(self, name):
        return self.plugins.get(name)

    def list_plugins(self):
        return list(self.plugins.keys())