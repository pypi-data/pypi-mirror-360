"""Multiple architecture support"""
import importlib
from typing import Callable, NamedTuple, Optional

from qlispreg.dicttree import flattenDict

from ..base import ABCCompileConfigMixin, QLispCode
from ..commands import CommandList, DataMap, RawData, Result
from ..config import Config


class Architecture(NamedTuple):
    name: str
    description: str
    assembly_code: Callable[[QLispCode, Optional[dict]], tuple[CommandList,
                                                               DataMap]]
    assembly_data: Callable[[RawData, DataMap], Result]
    config_factory: Optional[ABCCompileConfigMixin] = None
    snapshot_factory: Optional[ABCCompileConfigMixin] = None


general_architecture = Architecture(
    name='general',
    description='General architecture',
    assembly_code=lambda code, context: (
        [],
        {
            'arch': 'general'
        },
    ),
    assembly_data=lambda data, data_map: flattenDict(data),
    config_factory=Config,
    snapshot_factory=Config,
)

__regested_architectures = {}


def get_arch(name: str = 'general',
             package: str | None = None) -> Architecture:
    if package is None and name in __regested_architectures:
        return __regested_architectures[name]
    if package is None and ':' in name:
        package, name = name.split(':')
    try:
        mod = importlib.import_module(package)
        for n, obj in mod.__dict__.items():
            if isinstance(obj, Architecture):
                __regested_architectures[obj.name] = obj
        if name in __regested_architectures:
            return __regested_architectures[name]
    except:
        pass
    raise ValueError(f"Architecture {name} not found")


def register_arch(arch: Architecture):
    __regested_architectures[arch.name] = arch


register_arch(general_architecture)

__all__ = ['Architecture', 'get_arch', 'register_arch']
