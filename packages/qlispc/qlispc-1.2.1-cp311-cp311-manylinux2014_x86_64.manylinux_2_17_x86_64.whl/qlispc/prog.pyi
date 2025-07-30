import asyncio
import concurrent.futures
from dataclasses import dataclass
from typing import Any, Optional

from waveforms.scan.base import StepStatus

from .base import QLispCode, Signal
from .commands import COMMAND, DataMap


@dataclass
class ProgramFrame():
    step: StepStatus
    circuit: list
    cmds: list[COMMAND]
    data_map: DataMap
    code: Optional[QLispCode]
    context: dict

    flushed: bool
    compile_fut: asyncio.Future | concurrent.futures.Future | None

    fut: Optional[asyncio.Future]

    def __getstate__(self) -> dict[str, Any]:
        ...


@dataclass
class Program:
    with_feedback: bool
    arch: str

    side_effects: dict

    steps: list[ProgramFrame]
    shots: int
    signal: Signal

    snapshot: dict
    patch: dict
    task_arguments: tuple[tuple, dict]
    meta_info: dict
