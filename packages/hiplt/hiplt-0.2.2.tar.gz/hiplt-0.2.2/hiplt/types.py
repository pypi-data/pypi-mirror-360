# hiplt/types.py

from typing import Protocol, runtime_checkable, Callable


@runtime_checkable
class Plugin(Protocol):
    def load(self) -> None:
        ...

    def unload(self) -> None:
        ...


# Общие типы
UserID = str
Permission = str
RoleName = str