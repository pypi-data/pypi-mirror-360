from typing import Any, Iterable

import numpy as np
from waveforms.waveform import Waveform

from .base import QLispCode
from .commands import COMMAND, DataMap
from .config import Config
from .library import Library


def qcompile(
        circuit: str | list | bytes,
        lib: Library,
        cfg: Config,
        signal,
        shots: int,
        context: dict,
        arch,
        align_right=False,
        waveform_length=98e-6
) -> tuple[QLispCode, tuple[list[COMMAND], DataMap]]:
    pass


def is_feedable(cmd: COMMAND) -> bool:
    pass


def pre_feed(
    cmds: list[COMMAND],
    state_caches: dict[str, Any] | None = None,
    active_suffixs: Iterable[str] = (),
    active_prefixs: Iterable[str] = ()
) -> dict[str, list[tuple[str, str, Any, str]]]:
    pass


def get_raw_channel_info(address: str, mapping: dict[str, str],
                         cfg: Config) -> str | dict | None:
    pass


def get_all_channels(cfg: Config) -> set[str]:
    pass


def sample_waveform(
        waveform: Waveform,
        calibration: dict[str, Any],
        sample_rate: float | int,
        start: float = 0,
        stop: float = 100e-6,
        support_waveform_object: bool = False,
        with_x: bool = False) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    pass


def try_to_call(x: Any, args: tuple, kwds: dict[str, Any]) -> Any:
    pass
