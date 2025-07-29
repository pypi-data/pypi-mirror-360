# hiplt/locale.py

import json
from typing import Dict, Optional


class LocaleManager:
    """
    Менеджер локализации с загрузкой из JSON-файлов и поддержкой fallback.
    """

    def __init__(self, default_locale: str = "en"):
        self._locales: Dict[str, Dict[str, str]] = {}
        self.current_locale: str = default_locale
        self.default_locale: str = default_locale

    def load_locale(self, locale_code: str, filepath: str):
        """
        Загружает локализацию из JSON-файла.
        Формат файла: {"key1": "перевод1", "key2": "перевод2"}
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._locales[locale_code] = data
            print(f"[LocaleManager] Загружена локаль '{locale_code}' из '{filepath}'")
        except Exception as e:
            print(f"[LocaleManager] Ошибка загрузки локали '{locale_code}': {e}")

    def set_locale(self, locale_code: str):
        if locale_code not in self._locales:
            raise ValueError(f"Локаль '{locale_code}' не загружена")
        self.current_locale = locale_code
        print(f"[LocaleManager] Текущая локаль установлена на '{locale_code}'")

    def translate(self, key: str, locale_code: Optional[str] = None) -> str:
        """
        Переводит ключ в текущей локали или в указанной.
        Возвращает ключ, если перевод не найден.
        """
        locale_code = locale_code or self.current_locale

        # Пробуем сначала нужную локаль
        loc_dict = self._locales.get(locale_code, {})
        if key in loc_dict:
            return loc_dict[key]

        # fallback на дефолтную локаль
        if locale_code != self.default_locale:
            default_dict = self._locales.get(self.default_locale, {})
            return default_dict.get(key, key)

        return key


if __name__ == "__main__":
    lm = LocaleManager()
    lm.load_locale("en", "locales/en.json")
    lm.load_locale("ru", "locales/ru.json")

    lm.set_locale("ru")
    print(lm.translate("hello"))        # Выведет перевод из ru или ключ "hello"
    print(lm.translate("nonexistent"))  # Вернёт "nonexistent", т.к. перевода нет