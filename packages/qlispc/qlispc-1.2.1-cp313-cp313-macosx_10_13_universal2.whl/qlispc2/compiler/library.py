import hashlib
import importlib
import importlib.util
import inspect
import os
import string
import sys
from functools import partial, partialmethod
from pathlib import Path
from typing import Any, Callable, cast
from types import ModuleType

from qlispreg.dicttree import NOTSET, query_tree


class Gate():

    def __init__(self, function, name: str, type: str, query):
        self.function = function
        self.name = name
        self.type = type
        self.query = query
        self.number_of_qubits = 0
        self.qubits = []
        self.arguments = []
        self.default_params = {}
        self.args = ()
        self.params = {}
        self.pass_ctx = False

        self.post_init()

    def __repr__(self):
        if self.number_of_qubits == -1:
            noq = '...'
        else:
            noq = self.number_of_qubits
        return f"<{self.name}:{noq}, type={self.type!r}, args={self.arguments!r}, params={list(self.default_params.keys())!r}>"

    def post_init(self):
        self.__doc__ = self.function.__doc__
        self.__signature__ = inspect.signature(self.function)
        self.__name__ = self.function.__name__
        self.__annotations__ = self.function.__annotations__
        for name, param in self.__signature__.parameters.items():
            if param.kind == param.POSITIONAL_ONLY:
                self.qubits.append(name)
            elif param.kind == param.POSITIONAL_OR_KEYWORD:
                self.arguments.append(name)
            elif param.kind == param.KEYWORD_ONLY:
                if name == 'ctx':
                    self.pass_ctx = True
                else:
                    self.default_params[name] = param.default

        if 'qubits' in self.qubits:
            self.number_of_qubits = -1
        else:
            self.number_of_qubits = len(self.qubits)

    def __call__(self, *args, **kwds):
        return self.function(*args, **kwds)

    def call(self,
             qubits: list,
             args: tuple = (),
             params: dict = {},
             ctx=None):
        if self.pass_ctx:
            params['ctx'] = ctx
        if self.number_of_qubits == -1:
            index = self.qubits.index('qubits')
            arb = qubits[index:index + len(qubits) - len(self.qubits) + 1]
            q = qubits[:index] + [arb] + qubits[index + len(qubits) -
                                                len(self.qubits) + 1:]
            return self.function(*q, *args, **params)
        else:
            return self.function(*qubits, *args, **params)

    def q(self, qubits, args: tuple = (), config: dict = {}):
        params = self.default_params.copy()
        if callable(self.query):
            return params.update(self.query(config, qubits, args))
        elif isinstance(self.query, str):
            result = query_tree(self._format_query(self.query, qubits, args),
                                config)
            if isinstance(result, dict):
                return params.update(result)
        elif isinstance(self.query, dict):
            for k, v in self.query.items():
                query = self._format_query(v, qubits, args)
                result = query_tree(query, config)
                if isinstance(
                        result,
                        tuple) and len(result) == 2 and result[0] is NOTSET:
                    continue
                params[k] = result
            return params
        else:
            return params

    def _format_query(self, query: str, qubits: list, args: tuple):
        template = string.Template(query)
        # TODO


GateDecorator = Callable[[Callable], Gate]


def gate(
    name: str | Callable | None = None,
    type: str = 'default',
    query: str | dict[str, str] | Callable | None = None
) -> Gate | GateDecorator:
    if callable(name):
        func = name
        if isinstance(func, (partial, partialmethod)):
            return gate(name=func.func.__name__)(func)
        else:
            return gate(name=func.__name__)(func)

    def decorator(func, name=name):
        if name is None:
            name = func.__name__
        gate = Gate(func, name, type, query)

        module = sys.modules[func.__module__]

        if '__qlisp_library__' not in module.__dict__:
            setattr(module, '__qlisp_library__', Library())
        library: Library = module.__qlisp_library__
        library.add_gate(gate)

        return gate

    return decorator


class Library():

    def __init__(self):
        self.parents: tuple[Library, ...] = ()
        self.namespace: dict[str, dict[str, Gate | str]] = {}

    def get(self, name: str, type: str | None = None) -> Gate:
        error_msg = f'can not find {name!r} in library.'

        if name not in self.namespace and not self.parents:
            raise KeyError(error_msg)

        if name in self.namespace:
            group = self.namespace[name]
            if type is None:
                type = cast(str, group.get("__default_type__", "default"))
            try:
                return cast(Gate, group[type])
            except KeyError:
                raise KeyError(
                    f'can not find {name!r} with type {type!r} in library.')
        else:
            for parent in reversed(self.parents):
                try:
                    return parent.get(name, type)
                except KeyError as e:
                    if len(e.args[0]) > len(error_msg):
                        error_msg = e.args[0]
                    continue
            raise KeyError(error_msg)

    def add_gate(self,
                 gate: Gate,
                 name: str | None = None,
                 type: str | None = None):
        if name is None:
            name = gate.name
        if type is None:
            type = gate.type
        if name not in self.namespace:
            self.namespace[name] = {'__default_type__': 'default'}
        self.namespace[name][type] = Gate(gate.function, name, type,
                                          gate.query)


def libraries(*libs: Library) -> Library:
    lib = Library()
    lib.parents = tuple(libs)
    return lib


def load_library_from_module(module: ModuleType) -> Library:
    """
    Load a library from a module.

    The module must have a __qlisp_library__ attribute.
    The __qlisp_library__ attribute must be a Library object.
    The __qlisp_library__ attribute must have a __dependencies__ attribute.
    The __dependencies__ attribute must be a list of strings.
    The strings must be the names of the libraries that this library depends on.
    The __qlisp_library__ attribute must have a __qlisp_library__ attribute.
    The __qlisp_library__ attribute must be a Library object.
    """
    module = importlib.reload(module)
    module.__qlisp_library__.__dependencies__ = getattr(
        module, '__dependencies__', [])
    return cast(Library, module.__qlisp_library__)


def load_library_from_file(path: Path) -> Library:
    """
    Load a library from a file.
    """
    path = path.resolve().absolute()
    if not path.exists():
        raise FileNotFoundError(f"Library file {path!r} does not exist.")
    name = '_'.join(path.parts).removeprefix('/').removesuffix('.py')
    name = name.replace('-', '_')
    name = name.replace('/', '_')
    name = name.replace('\\', '_')
    name = name.replace('.', '_')
    name = name.replace(' ', '_')
    name = "_qlisp_lib_" + name
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        raise ValueError(f"can not load library from {path!r}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore
    sys.modules.pop(name)
    return load_library_from_module(module)


def load_library_from_source_code(code: str, name: str = '') -> Library:
    """
    Load a library from source code.
    """
    hash_str = hashlib.md5(code.encode()).hexdigest()
    name = f'_qlisp_lib_{name}_{hash_str}'
    spec = importlib.util.spec_from_loader(name, loader=None)
    if spec is None:
        raise ValueError(f"can not load library from {name!r}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(code, module.__dict__)
    sys.modules.pop(name)
    return load_library_from_module(module)


def import_gate_from_library_as(library: Library,
                                name: str,
                                as_name: str | None = None,
                                as_type: str = 'default',
                                ret: Library | None = None) -> Library:
    """
    Import a gate from a library.

    Parameters
    ----------
    library : Library
        The library to import the gate from.
    name : str
        The name of the gate to import.
    as_name : str | None, optional
        The name to import the gate as.
    as_type : str, optional
        The type of the gate to import.
    ret : Library | None, optional
        The library to return.

    Raises
    ------
    KeyError
        If the gate is not found in the library.

    Returns
    -------
    Library
        The library with the gate imported.
    """
    if ret is None:
        ret = Library()
    try:
        if as_name is None:
            as_name = name
        gate = library.get(name)
        ret.add_gate(gate, as_name, as_type)
        return ret
    except KeyError:
        raise KeyError(f"can not find gate {name!r} in library {library!r}.")


def load_library(name: str) -> Library:
    """
    Load a library by name.

    Parameters
    ----------
    name : str
        The name of the library to load.
        The name can be a path to a file, a module name or a string of source code.

    Returns
    -------
    Library
        The library loaded.
    """
    if is_module_name(name):
        module = importlib.import_module(name)
        return load_library_from_module(module)

    if name.isidentifier():
        return load_library_from_module(
            importlib.import_module(f"qlispc2.compiler.libs.{name}"))

    if is_file_name(name):
        return load_library_from_file(Path(os.path.expanduser(name)))

    if is_source_code(name):
        return load_library_from_source_code(name)

    raise SyntaxError(f"can not load library {name!r}. "
                      "Please check the syntax of the source code.")


def is_module_name(s: str) -> bool:
    return '.' in s and all(c.isidentifier() for c in s.split('.'))


def is_file_name(s: str) -> bool:
    return s.endswith('.py') and '\n' not in s


def is_source_code(s: str) -> bool:
    return '@gate' in s
