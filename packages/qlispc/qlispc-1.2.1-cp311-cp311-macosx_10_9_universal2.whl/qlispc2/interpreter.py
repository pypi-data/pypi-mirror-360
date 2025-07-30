from __future__ import annotations

import operator
from collections import defaultdict
from enum import Enum, auto
from math import e, pi
from typing import Any

from .parse import parse as qlisp_parser
from .tokenize import Expression, Symbol
from .compiler.instructions import Instruction
from .compiler.opcode import OPCODE
from .compiler.vm import VirtualMachine


class Context:

    def __init__(self):
        self.internal = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '==': operator.eq,
            '!=': operator.ne,
            '<': operator.lt,
            '>': operator.gt,
            '<=': operator.le,
            '>=': operator.ge,
            'and': operator.and_,
            'or': operator.or_,
            'not': operator.not_,
            '>>': operator.rshift,
            '<<': operator.lshift,
            '|': operator.or_,
            '&': operator.and_,
            '^': operator.xor,
            '~': operator.invert,
            'print': print,
            'input': input,
            'cast_int': int,
            'cast_float': float,
        }
        self.functions = {}
        self.constants = {}
        self.counter = 0
        self.env = {}
        self.outer = None
        self.namespaces = []

    def new_label(self, label):
        self.counter += 1
        try:
            namespace = '.'.join(self.namespaces)
        except:
            print(self.namespaces)
            raise
        return f':{namespace}.{label}-{self.counter}'

    def assign(self, name, value):
        self.env[name] = value

    def find(self, name, level=0):
        if name in self.env:
            return self.env, level
        elif self.outer:
            return self.outer.find(name, level + 1)
        else:
            return None, None

    def lookup(self, name):
        env, level = self.find(name)
        if env:
            return env[name], level
        else:
            raise RuntimeError(f"undefined variable {name}")

    def child(self, namespace):
        child = Context()
        child.internal = self.internal
        child.outer = self
        child.functions = self.functions
        child.constants = self.constants
        child.namespaces = self.namespaces + [namespace]
        return child


def head(expr):
    if isinstance(expr, Expression) and len(expr) == 0:
        return 'None'
    if isinstance(expr, Expression) and isinstance(expr[0], Symbol):
        return expr[0].name
    if isinstance(expr, Expression):
        return f"OP{expr[0]}"
    if isinstance(expr, Symbol):
        return 'Symbol'
    return 'Atom'


def compile_call(expr, ctx, ret):
    func, *args = expr
    if isinstance(func, Symbol) and func.name == '!asm':
        return list(args)

    code = []
    for arg in reversed(args):
        code.extend(compile_expr(arg, ctx, False))
    code.extend([
        *compile_expr(func, ctx, ret),
        (OPCODE.CALL_RET if ret else OPCODE.CALL, len(args))
    ])

    return code


def compile_define(expr, ctx, ret):
    is_function = False

    name, value = expr[1:]
    name = name.name
    label = ctx.new_label(name)
    code = compile_expr(value, ctx, False)

    ret = []

    if len(code) == 1 and isinstance(code[0], str):
        if 'lambda' in code[0]:
            is_function = True
            func_code = ctx.functions[code[0]]
            for i in range(len(func_code)):
                if isinstance(func_code[i],
                              str) and func_code[i] == f":external_ref:{name}":
                    func_code[i] = label

    if is_function:
        ctx.functions[label] = ctx.functions.pop(code[0])
    else:
        if len(code) == 2 and code[1] == OPCODE.LOAD:
            label = code[0]
        elif len(code) == 1:
            ctx.constants[label] = value
        else:
            ctx.constants[label] = 0
            ret = [*code, label, OPCODE.STORE]
    ctx.assign(name, label)
    return ret


def compile_lambda(expr, ctx, ret):
    args, body = expr[1:]
    args = [arg.name for arg in args[::-1]]
    label = ctx.new_label('lambda')
    ctx.functions[label] = []
    sub_ctx = ctx.child(label)
    for i, arg in enumerate(args):
        sub_ctx.assign(arg, i)
    code = compile_function_body(body, sub_ctx)
    ctx.functions[label] = code
    return [label]


def compile_function_body(expr, ctx):
    body = compile_expr(expr, ctx, True)
    if (body and (isinstance(body[-1], OPCODE) and body[-1] == OPCODE.CALL_RET)
            or (isinstance(body[-1], tuple) and len(body[-1]) == 2
                and isinstance(body[-1][0], OPCODE)
                and body[-1][0] == OPCODE.CALL_RET)):
        return body
    return [*body, OPCODE.RET]


def compile_symbol(expr, ctx, ret):
    if expr.name in ctx.internal:
        return [ctx.internal[expr.name]]

    try:
        ref, level = ctx.lookup(expr.name)
    except:
        return [f":external_ref:{expr.name}"]

    if ref in ctx.functions:
        return [ref]
    if ref in ctx.constants:
        return [ref, OPCODE.LOAD]

    return [ref, level, OPCODE.SLOAD]


def compile_value(expr, ctx, ret):
    if isinstance(expr, (int, float)):
        return [expr]
    label = ctx.new_label('value')
    ctx.constants[label] = expr
    return [label, OPCODE.LOAD]


def compile_if(expr, ctx, ret):
    cond, then, else_ = expr[1:]
    else_label = ctx.new_label('else')
    end_label = ctx.new_label('end')
    code = compile_expr(cond, ctx, False)
    code.extend([else_label, OPCODE.JZ])
    code.extend([*compile_expr(then, ctx, ret), end_label, OPCODE.JMP])
    code.extend([f"label{else_label}"])
    code.extend(compile_expr(else_, ctx, ret))
    code.extend([f"label{end_label}"])
    return code


def compile_cond(expr, ctx, ret):
    # TODO
    code = []
    return code


def compile_begin(expr, ctx, ret):
    code = []
    for e in expr[1:-1]:
        c = compile_expr(e, ctx, False)
        code.extend(c)
        if len(c) > 0:
            code.append(OPCODE.DROP)
    code.extend(compile_expr(expr[-1], ctx, ret))
    return code


def compile_setq(expr, ctx, ret):
    name, value = expr[1:]
    name = name.name
    ref, level = ctx.lookup(name)
    code = compile_expr(value, ctx, False)
    code.extend([OPCODE.DUP, ref, level, OPCODE.SSTORE])
    return code


def compile_let(expr, ctx, ret):
    _, bindings, body = expr
    args = []
    params = []
    for name, value in bindings:
        args.append(name)
        params.append(value)
    expr = Expression(
        [Expression([Symbol('lambda'),
                     Expression(args), body]), *params])
    return compile_expr(expr, ctx, ret)


def compile_let_star(expr, ctx, ret):
    _, bindings, body = expr
    tmp_bindings = []
    inner_bindings = []
    args = []
    for name, _ in bindings:
        args.append(name)
        tmp_bindings.append(Expression([name, 0]))
        inner_bindings.append(Expression([name, name]))
    expr = Expression([
        Symbol('let'),
        Expression([*tmp_bindings]),
        Expression([
            Symbol('begin'), *[
                Expression([Symbol('setq'), name, value])
                for name, value in bindings
            ],
            Expression([Symbol('let'),
                        Expression(inner_bindings), body])
        ])
    ])
    return compile_expr(expr, ctx, ret)


def compile_quote(expr, ctx, ret):
    # TODO
    return [expr]


def compile_while(expr, ctx, ret):
    cond, body = expr[1:]

    loop_start = ctx.new_label('loop')
    loop_end = ctx.new_label('end')
    code = [
        f"label{loop_start}",
        *compile_expr(cond, ctx, False),
        loop_end, OPCODE.JZ,
        *compile_expr(body, ctx, ret),
        OPCODE.DROP,
        loop_start, OPCODE.JMP,
        f"label{loop_end}", None
    ] #yapf: disable
    return code


def compile_expr(expr, ctx: Context, ret: bool = False) -> list[Any]:
    dispatch_table = {
        'if': compile_if,
        'cond': compile_cond,
        'begin': compile_begin,
        'setq': compile_setq,
        'let': compile_let,
        'let*': compile_let_star,
        'quote': compile_quote,
        'while': compile_while,
        'lambda': compile_lambda,
        'define': compile_define,
    }

    if isinstance(expr, Expression):
        cond = head(expr)
        if cond == 'None':
            return [None]
        if cond in dispatch_table:
            return dispatch_table[cond](expr, ctx, ret)
        else:
            return compile_call(expr, ctx, ret)
    elif isinstance(expr, Symbol):
        return compile_symbol(expr, ctx, ret)
    else:
        return compile_value(expr, ctx, ret)


def compile(prog: str,
            extra_commands: dict[str, Any] = {},
            language='qlisp',
            debug=False) -> list[Any]:
    ctx = Context()
    ctx.internal.update(extra_commands)
    functions = {}

    parsers = {'qlisp': qlisp_parser}
    parse = parsers[language]

    functions['main'] = compile_function_body(parse(prog), ctx)

    for name, code in ctx.functions.items():
        functions[name[1:]] = code

    constants = {}
    for name, value in ctx.constants.items():
        constants[name[1:]] = value

    lib = (functions, constants, ctx.env)

    code = link(functions, constants)
    if debug:
        return code, functions, ctx
    else:
        return code  #, functions, ctx


def _link(code, functions, constants):

    def process(code):
        count = 0
        tmp = []
        labels = {}
        pointers = {}
        functions = {}
        for c in code:
            if isinstance(c, str) and c.startswith('label:'):
                labels[c[6:]] = count
            else:
                count += 1
                tmp.append(c)
                if isinstance(c, str) and c.startswith(':'):
                    pointers[count] = c[1:]
        for i, label in pointers.items():
            if label in labels:
                tmp[i - 1] = labels[label]
            else:
                functions[i - 1] = label
        return tmp, functions

    for name in list(functions.keys()):
        if isinstance(functions[name], tuple):
            continue
        functions[name] = process(functions[name])

    fun_ptrs = {}
    const_ptrs = {}
    code, fun_refs = process(code)

    for name, value in constants.items():
        const_ptrs[name] = len(code)
        code.append(value)

    for name, (c, f_refs) in functions.items():
        fun_ptrs[name] = len(code)
        code.extend(c)
        for i, n in f_refs.items():
            fun_refs[i + fun_ptrs[name]] = n
    external_refs = {}
    for addr, label in fun_refs.items():
        if label in fun_ptrs:
            code[addr] = fun_ptrs[label]
        elif label in const_ptrs:
            code[addr] = const_ptrs[label]
        else:
            external_refs[addr] = label
    return code, external_refs


def link(functions=None, constants=None, dynamic=False):
    if functions is None:
        functions = {}
    if constants is None:
        constants = {}
    if "main" not in functions and not dynamic:
        raise RuntimeError("main function not defined")

    enter_code = [
        ":main",
        Instruction(OPCODE.CALL, 0),
        Instruction(OPCODE.EXIT, 0)
    ]
    code_, external_refs = _link(enter_code, functions, constants)
    if external_refs and not dynamic:
        raise RuntimeError(
            f"external references: {set(external_refs.values())}")
    code = []
    for c in code_:
        if isinstance(c, OPCODE):
            code.append(Instruction(c, None))
        elif isinstance(c, tuple) and len(c) == 2 and isinstance(c[0], OPCODE):
            code.append(Instruction(c[0], c[1]))
        elif isinstance(c, Instruction):
            code.append(c)
        else:
            code.append(Instruction(OPCODE.PUSH, c))
    return code
