from typing import Any


class COMMAND():

    def __init__(self, address: str, value: Any):
        ...

    address: str
    value: Any


class READ(COMMAND):
    """Read a value from the scheduler"""

    def __init__(self, address: str):
        ...

    def __repr__(self) -> str:
        ...


class WRITE(COMMAND):

    def __repr__(self) -> str:
        ...


class TRIG(COMMAND):
    """Trigger the system"""

    def __init__(self, address: str):
        ...

    def __repr__(self) -> str:
        ...


class SYNC(COMMAND):
    """Synchronization command"""

    def __init__(self, delay: float = 0):
        ...

    def __repr__(self) -> str:
        ...


class PUSH(COMMAND):

    def __init__(self):
        ...

    def __repr__(self) -> str:
        ...


class FREE(COMMAND):

    def __init__(self):
        ...

    def __repr__(self) -> str:
        pass


CommandList = list[COMMAND]
DataMap = dict[str, dict]
RawData = Any
Result = dict
