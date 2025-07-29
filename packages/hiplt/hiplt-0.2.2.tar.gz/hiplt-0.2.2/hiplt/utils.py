# hiplt/utils.py

import os
import datetime
import logging
from typing import Optional


def now_iso() -> str:
    """
    Возвращает текущую дату и время в ISO 8601 формате UTC.
    """
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_dir(path: str):
    """
    Создаёт директорию, если её нет.
    """
    os.makedirs(path, exist_ok=True)


def setup_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Настраивает и возвращает логгер с указанным именем и уровнем логирования.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


# Дополнительные утилиты:

def safe_read_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger = logging.getLogger("cso.utils")
        logger.error(f"Ошибка чтения файла '{path}': {e}")
        return None


def safe_write_file(path: str, content: str) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger = logging.getLogger("cso.utils")
        logger.error(f"Ошибка записи в файл '{path}': {e}")
        return False