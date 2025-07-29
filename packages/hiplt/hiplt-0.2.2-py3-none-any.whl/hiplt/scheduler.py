# hiplt/scheduler.py

import asyncio
import time
import datetime

class Task:
    def __init__(self, func, *, interval=None, delay_time=None, at_time=None, loop=False, name=None):
        self.func = func
        self.interval = interval
        self.delay_time = delay_time
        self.at_time = at_time
        self.loop = loop
        self.name = name or func.__name__
        self.running = False
        self.paused = False
        self._task = None

    async def _run(self):
        self.running = True

        # Задержка
        if self.delay_time:
            await asyncio.sleep(self.delay_time)
            await self._execute_once()
            self.running = False
            return

        # Запуск в заданное время
        if self.at_time:
            while self.running:
                now = datetime.datetime.now().strftime("%H:%M")
                if now == self.at_time and not self.paused:
                    await self._execute_once()
                    self.running = False
                    return
                await asyncio.sleep(30)

        # Интервальный режим
        while self.loop and self.running:
            await asyncio.sleep(self.interval)
            if not self.paused:
                await self._execute_once()

    async def _execute_once(self):
        try:
            if asyncio.iscoroutinefunction(self.func):
                await self.func()
            else:
                self.func()
        except Exception as e:
            print(f"[SCHEDULER:{self.name}] Ошибка в задаче: {e}")

    def start(self):
        self._task = asyncio.create_task(self._run())

    def stop(self):
        self.running = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False


class Scheduler:
    def __init__(self):
        self.tasks = []

    def every(self, seconds, name=None):
        def decorator(func):
            task = Task(func, interval=seconds, loop=True, name=name)
            self.tasks.append(task)
            task.start()
            return func
        return decorator

    def delay(self, seconds, name=None):
        def decorator(func):
            task = Task(func, delay_time=seconds, name=name)
            self.tasks.append(task)
            task.start()
            return func
        return decorator

    def at(self, time_str, name=None):
        def decorator(func):
            task = Task(func, at_time=time_str, name=name)
            self.tasks.append(task)
            task.start()
            return func
        return decorator

    def stop_all(self):
        for task in self.tasks:
            task.stop()
        self.tasks.clear()

    def get(self, name):
        for task in self.tasks:
            if task.name == name:
                return task
        return None

    def list_tasks(self):
        return [task.name for task in self.tasks]

# Глобальный экземпляр
scheduler = Scheduler()