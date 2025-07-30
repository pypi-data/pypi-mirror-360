from typing import Any, Callable

def call_func_with_kwds(func: Callable, kwds: dict[str, Any]) -> Any:
    ...


def try_to_call(x: Any, kwds: dict[str, Any]) -> Any:
    ...


def mapping_qubits(circuit: list[tuple], mapping: dict) -> list[tuple]:
    ...
