from .base import Context, QLispCode
from .library import Library


def call_opaque(st: tuple, ctx: Context, lib: Library):
    ...


def assembly_align_left(qlisp, ctx: Context, lib: Library) -> QLispCode:
    ...


def assembly_align_right(qlisp, ctx: Context, lib: Library) -> QLispCode:
    ...
