# hiplt/shell.py

import code
import sys
import traceback


class Shell:
    """
    Интерактивный REPL-терминал для отладки и быстрого запуска кода.
    Можно передать словарь локальных переменных.
    """

    def __init__(self, locals_: dict = None):
        self.locals = locals_ if locals_ else {}

    def start(self):
        banner = (
            "CSO Shell Interactive Mode\n"
            "Введите Python команды.\n"
            "Для выхода Ctrl+D или команда exit()\n"
        )
        try:
            shell = code.InteractiveConsole(locals=self.locals)
            shell.interact(banner=banner)
        except SystemExit:
            print("Выход из CSO Shell.")
        except Exception:
            traceback.print_exc()
            print("Ошибка в Shell.")


if __name__ == "__main__":
    shell = Shell()
    shell.start()