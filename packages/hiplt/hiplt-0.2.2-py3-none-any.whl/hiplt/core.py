# hiplt/core.py

import asyncio
import inspect

class Event:
    def __init__(self):
        self._listeners = []

    def listen(self, func=None, *, priority=0):
        """Декоратор или прямое добавление функции с приоритетом.
        Чем выше priority — тем раньше вызывается слушатель."""
        if func is None:
            def wrapper(f):
                self._add_listener(f, priority)
                return f
            return wrapper
        else:
            self._add_listener(func, priority)
            return func

    def _add_listener(self, func, priority):
        self._listeners.append((priority, func))
        # Сортируем слушателей по убыванию приоритета
        self._listeners.sort(key=lambda x: x[0], reverse=True)

    def remove(self, func):
        """Удалить слушателя, если он есть"""
        self._listeners = [(p, f) for (p, f) in self._listeners if f != func]

    def clear(self):
        """Удалить всех слушателей"""
        self._listeners.clear()

    def trigger(self, *args, **kwargs):
        """Вызов слушателей. Если слушатель - async, запускает через asyncio.create_task."""
        for _, func in self._listeners:
            try:
                if inspect.iscoroutinefunction(func):
                    asyncio.create_task(func(*args, **kwargs))
                else:
                    func(*args, **kwargs)
            except Exception as e:
                print(f"[Event] Ошибка в слушателе {func}: {e}")

    async def trigger_async(self, *args, **kwargs):
        """Асинхронный вызов всех слушателей с ожиданием (если async)"""
        for _, func in self._listeners:
            try:
                if inspect.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
            except Exception as e:
                print(f"[Event] Ошибка в слушателе {func}: {e}")