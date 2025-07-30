from typing import Callable, Generator

from .library import Library


def extend_macro(qlisp,
                 lib: Library,
                 env: Library | None = ...) -> Generator[tuple, None, None]:
    pass


def add_VZ_rule(gateName: str, rule: Callable):
    pass


def remove_VZ_rule(gateName: str, rule: Callable):
    pass


def reduceVirtualZ(qlisp: tuple, lib: Library) -> Generator[tuple, None, None]:
    pass
