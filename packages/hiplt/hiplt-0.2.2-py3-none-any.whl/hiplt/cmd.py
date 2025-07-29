# hiplt/cmd.py

import asyncio
from inspect import iscoroutinefunction

class CommandHandler:
    def __init__(self):
        self.commands = {}

    def register(self, name):
        def wrapper(func):
            self.commands[name] = func
            return func
        return wrapper

    def run(self, command_line):
        parts = command_line.strip().split()
        if not parts:
            return
        cmd, *args = parts
        if cmd in self.commands:
            func = self.commands[cmd]
            if iscoroutinefunction(func):
                asyncio.run(func(*args))
            else:
                return func(*args)
        else:
            print(f"Unknown command: {cmd}")

    async def run_async(self, command_line):
        parts = command_line.strip().split()
        if not parts:
            return
        cmd, *args = parts
        if cmd in self.commands:
            func = self.commands[cmd]
            if iscoroutinefunction(func):
                await func(*args)
            else:
                func(*args)
        else:
            print(f"Unknown command: {cmd}")