# hiplt/system.py

import os
import platform
import subprocess
import shutil

class SystemUtil:
    @staticmethod
    def run(command, shell=True, capture_stderr=False, as_root=False):
        """
        Выполняет команду и возвращает результат
        """
        if as_root and not SystemUtil.is_root():
            command = f"su -c \"{command}\""

        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True
            )
            if capture_stderr:
                return result.stderr
            return result.stdout
        except Exception as e:
            return f"[run] Ошибка: {e}"

    @staticmethod
    def is_android():
        return "android" in platform.platform().lower()

    @staticmethod
    def is_termux():
        return SystemUtil.is_android() and shutil.which("termux-info") is not None

    @staticmethod
    def is_windows():
        return os.name == "nt"

    @staticmethod
    def is_linux():
        return os.name == "posix" and not SystemUtil.is_android()

    @staticmethod
    def is_root():
        if SystemUtil.is_windows():
            return False  # в Windows проверка прав сложнее
        try:
            return os.geteuid() == 0
        except AttributeError:
            # На Android/Termux getuid недоступен — можно попробовать другой способ
            return os.path.exists("/data/adb")

    @staticmethod
    def info():
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "is_android": SystemUtil.is_android(),
            "is_termux": SystemUtil.is_termux(),
            "is_root": SystemUtil.is_root(),
            "python_version": platform.python_version()
        }