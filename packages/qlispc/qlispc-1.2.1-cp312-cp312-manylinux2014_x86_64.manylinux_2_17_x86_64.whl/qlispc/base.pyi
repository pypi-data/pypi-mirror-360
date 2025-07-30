from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Flag
from functools import cached_property
from typing import Any, Callable, NamedTuple, Optional, SupportsIndex, Union

import numpy as np
from waveforms.waveform import Waveform


class Signal(Flag):
    trace: 'Signal'
    iq: 'Signal'
    state: 'Signal'
    _avg_trace: 'Signal'
    _avg_iq: 'Signal'
    _avg_state: 'Signal'
    _count: 'Signal'
    _remote: 'Signal'
    trace_avg: 'Signal'
    iq_avg: 'Signal'
    population: 'Signal'
    count: 'Signal'
    diag: 'Signal'
    remote_trace_avg: 'Signal'
    remote_iq_avg: 'Signal'
    remote_state: 'Signal'
    remote_population: 'Signal'
    remote_count: 'Signal'


def head(st: tuple) -> str:
    ...


class QLispError(SyntaxError):
    pass


class Capture(NamedTuple):
    qubit: str
    cbit: tuple[str, int]
    time: float
    signal: Signal
    params: dict
    hardware: Union['ADChannel', 'MultADChannel'] = None
    shift: float = 0


class AWGChannel(NamedTuple):
    name: str
    sampleRate: float
    size: int = -1
    amplitude: Optional[float] = None
    offset: Optional[float] = None
    delay: float = 0
    sos: Optional[np.ndarray] = None
    commandAddresses: tuple = ()


class MultAWGChannel(NamedTuple):
    I: Optional[AWGChannel] = None
    Q: Optional[AWGChannel] = None
    LO: Optional[str] = None
    lo_freq: float = -1
    lo_power: Optional[float] = None


class ADChannel(NamedTuple):
    name: str
    sampleRate: float = 1e9
    trigger: str = ''
    triggerDelay: float = 0
    triggerClockCycle: float = 8e-9
    commandAddresses: tuple = ()


class MultADChannel(NamedTuple):
    I: Optional[ADChannel] = None
    Q: Optional[ADChannel] = None
    IQ: Optional[ADChannel] = None
    Ref: Optional[ADChannel] = None
    LO: Optional[str] = None
    lo_freq: float = -1
    lo_power: Optional[float] = None


class GateConfig(NamedTuple):
    name: str
    qubits: tuple
    type: str = 'default'
    params: dict = {}


class ABCCompileConfigMixin(ABC):

    @abstractmethod
    def _getAWGChannel(self, name,
                       *qubits) -> Union[AWGChannel, MultAWGChannel]:
        ...

    @abstractmethod
    def _getADChannel(self, qubit) -> Union[ADChannel, MultADChannel]:
        ...

    @abstractmethod
    def _getGateConfig(self, name, *qubits) -> GateConfig:
        ...

    @abstractmethod
    def _getAllQubitLabels(self) -> list[str]:
        ...


def set_config_factory(factory: Callable):
    ...


def getConfig() -> ABCCompileConfigMixin:
    ...


@dataclass
class Context():
    cfg: ABCCompileConfigMixin
    scopes: list[dict[str, Any]]
    qlisp: list
    time: dict[str, float]
    addressTable: dict
    waveforms: dict[str, list[Waveform]]
    measures: dict[str, dict[int, Capture]]
    phases_ext: dict[str, dict[Union[int, str], float]]
    biases: dict[str, float]
    end: float
    cache: dict

    @property
    def channel(self) -> SupportsIndex:
        ...

    @property
    def phases(self) -> SupportsIndex:
        ...

    @property
    def params(self) -> dict[str, Any]:
        ...

    @property
    def vars(self) -> dict[str, Any]:
        ...

    @property
    def globals(self) -> dict[str, Any]:
        ...

    @cached_property
    def all_qubits(self) -> list[str]:
        ...

    def get_gate_config(self, name: str, qubits: tuple,
                        type: str) -> GateConfig:
        ...

    def get_awg_channel(self, name: str,
                        qubits: tuple) -> AWGChannel | MultAWGChannel:
        ...

    def get_ad_channel(self, qubit: str | int) -> ADChannel | MultADChannel:
        ...

    def qubit(self, q):
        ...


@dataclass
class QLispCode():
    cfg: ABCCompileConfigMixin
    qlisp: list
    waveforms: dict[str, Waveform]
    measures: dict[tuple[str, int], list[Capture]]
    end: float
    signal: Signal
    shots: int
    arch: str
    cbit_alias: dict[int, tuple[int, int]]
    sub_code_count: int


def create_context(ctx: Optional[Context] = None, **kw) -> Context:
    ...
