# hiplt/config.py

import json
import os

class Config:
    def __init__(self, filename="config.json", autosave=True):
        self.filename = filename
        self.data = {}
        self.autosave = autosave
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Config] Ошибка загрузки файла {self.filename}: {e}")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"[Config] Ошибка сохранения файла {self.filename}: {e}")

    def get(self, key, default=None):
        """Поддержка вложенных ключей через точку: 'section.subkey'"""
        keys = key.split(".")
        val = self.data
        try:
            for k in keys:
                val = val[k]
            return val
        except (KeyError, TypeError):
            return default

    def set(self, key, value):
        """Поддержка вложенных ключей через точку"""
        keys = key.split(".")
        d = self.data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        if self.autosave:
            self.save()

    def update(self, data: dict):
        """Обновляет конфиг слиянием с другим словарём (рекурсивно)"""
        def merge(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = merge(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        merge(self.data, data)
        if self.autosave:
            self.save()

    def delete(self, key):
        """Удаляет ключ, поддерживает вложенные"""
        keys = key.split(".")
        d = self.data
        try:
            for k in keys[:-1]:
                d = d[k]
            del d[keys[-1]]
            if self.autosave:
                self.save()
            return True
        except (KeyError, TypeError):
            return False

    def exists(self, key):
        keys = key.split(".")
        d = self.data
        try:
            for k in keys:
                d = d[k]
            return True
        except (KeyError, TypeError):
            return False

    def clear(self):
        self.data = {}
        if self.autosave:
            self.save()