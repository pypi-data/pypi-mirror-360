import asyncio
import concurrent.futures
from dataclasses import dataclass, field
from typing import Optional

from .base import QLispCode, Signal
from .commands import COMMAND, DataMap
from .tools.scan import StepStatus


@dataclass
class ProgramFrame():
    """
    A frame of a program.
    """
    step: StepStatus = field(default=None)
    circuit: list = field(default_factory=list)
    cmds: list[COMMAND] = field(default_factory=list)
    data_map: DataMap = field(default_factory=dict)
    code: Optional[QLispCode] = None
    context: dict = field(default_factory=dict)

    flushed: bool = False
    compile_fut: asyncio.Future | concurrent.futures.Future | None = None

    fut: Optional[asyncio.Future] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        try:
            del state['fut']
            del state['compile_fut']
        except:
            pass
        return state


@dataclass
class Program:
    """
    A program is a list of commands.
    """
    with_feedback: bool = False
    arch: str = 'baqis'

    side_effects: dict = field(default_factory=dict)

    steps: list[ProgramFrame] = field(default_factory=list)
    shots: int = 1024
    signal: Signal = Signal.state

    snapshot: dict = field(default_factory=dict)
    patch: dict = field(default_factory=dict)
    task_arguments: tuple[tuple, dict] = (tuple(), dict())
    meta_info: dict = field(default_factory=dict)
