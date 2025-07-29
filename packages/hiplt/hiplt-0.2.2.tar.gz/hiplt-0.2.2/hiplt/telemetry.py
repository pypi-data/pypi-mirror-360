# hiplt/telemetry.py

import logging
import time
from typing import Optional


class Telemetry:
    """
    Лёгкий модуль логирования и метрик.
    Позволяет логировать события, ошибки и замеры времени.
    """

    def __init__(self, logger_name: str = "cso.telemetry"):
        self.logger = logging.getLogger(logger_name)
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[Telemetry][%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_event(self, event_name: str, data: Optional[dict] = None):
        self.logger.info(f"Event: {event_name} | Data: {data}")

    def log_error(self, error_msg: str):
        self.logger.error(error_msg)

    def timeit(self, func):
        """
        Декоратор для измерения времени выполнения функции.
        """

        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            self.logger.info(f"{func.__name__} выполнена за {end - start:.4f} сек.")
            return result

        return wrapper


if __name__ == "__main__":
    telemetry = Telemetry()
    telemetry.log_event("app_started", {"version": "0.1"})
    telemetry.log_error("Пример ошибки")

    @telemetry.timeit
    def slow_func():
        import time

        time.sleep(1)

    slow_func()