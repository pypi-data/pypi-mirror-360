from __future__ import annotations

import operator
from collections import defaultdict
from math import e, pi
from typing import Any
from .opcode import OPCODE
from .instructions import Instruction


class Frame():

    def __init__(self, frequency: int = 0):
        self.frequency = frequency
        self.phase = 0
        self.time = 0


class Channel():

    def __init__(self, name: str = 'demo', group: str = 'default'):
        self.name = name
        self.group = group
        self.frames = defaultdict(Frame)


def barrier(*channels: Channel):
    t_max = 0
    for channel in channels:
        for frame in channel.frames.values():
            t_max = max(t_max, frame.time)
    for channel in channels:
        for frame in channel.frames.values():
            frame.time = t_max


def vm_pop(vm, value: Any):
    vm._pop()


def vm_push(vm, value: Any):
    vm._push(value)


def vm_dup(vm, value: Any):
    x = vm._pop()
    vm._push(x)
    vm._push(x)


def vm_swap(vm, value: Any):
    v2 = vm._pop()
    v1 = vm._pop()
    vm._push(v2)
    vm._push(v1)


def vm_over(vm, value: Any):
    x = vm._pop()
    y = vm._pop()
    vm._push(y)
    vm._push(x)
    vm._push(y)


def vm_sload(vm, value: Any):
    level = vm._pop()
    n = vm._pop()
    addr = vm.bp
    for _ in range(level):
        addr = vm.stack[addr - 3]
    vm._push(vm.stack[addr + n])


def vm_sstore(vm, value: Any):
    level = vm._pop()
    n = vm._pop()
    value = vm._pop()

    addr = vm.bp
    for _ in range(level):
        addr = vm.stack[addr - 3]
    vm.stack[addr + n] = value


def vm_load(vm, value: Any):
    addr = vm._pop()
    vm._push(vm.mem[addr].argument)


def vm_store(vm, value: Any):
    addr = vm._pop()
    value = vm._pick()
    vm.mem[addr] = Instruction(OPCODE.PUSH, value)


def vm_call(vm, value: Any):
    func = vm._pop()
    argc = value
    args = [vm._pop() for _ in range(argc)]

    if callable(func):
        vm._push(func(*args))
    elif isinstance(func, int):
        vm._push(vm.bp)
        vm._push(vm.sl)
        vm._push(vm.pc)
        vm.bp = vm.sp
        for arg in reversed(args):
            vm._push(arg)
        vm.sl = func
        vm.pc = func
    else:
        raise RuntimeError(f"not callable {func}")


def vm_ret(vm, value: Any):
    result = vm._pop()
    vm.sp = vm.bp - 3
    vm.bp, vm.sl, vm.pc = vm.stack[vm.bp - 3:vm.bp]
    vm._push(result)


def vm_call_ret(vm, value: Any):
    func = vm._pop()
    argc = value

    if callable(func):
        args = reversed(vm.stack[vm.sp - argc:vm.sp])
        vm.sp = vm.bp - 3
        vm.bp, vm.sl, vm.pc = vm.stack[vm.bp - 3:vm.bp]
        vm._push(func(*args))
    elif isinstance(func, int):
        if vm.sp != vm.bp + argc:
            vm.stack[vm.bp:vm.bp + argc] = vm.stack[vm.sp - argc:vm.sp]
            vm.sp = vm.bp + argc
        vm.sl = func
        vm.pc = func
    else:
        raise RuntimeError(f"not callable {func}")


def vm_jmp(vm, value: Any):
    vm.pc = vm._pop() + vm.sl


def vm_jnz(vm, value: Any):
    addr = vm._pop()
    cond = vm._pop()
    if cond:
        vm.pc = addr + vm.sl


def vm_jz(vm, value: Any):
    addr = vm._pop()
    cond = vm._pop()
    if cond == 0:
        vm.pc = addr + vm.sl


dispatch_table = {
    OPCODE.PUSH: vm_push,
    OPCODE.DUP: vm_dup,
    OPCODE.DROP: vm_pop,
    OPCODE.SWAP: vm_swap,
    OPCODE.OVER: vm_over,
    OPCODE.SLOAD: vm_sload,
    OPCODE.SSTORE: vm_sstore,
    OPCODE.LOAD: vm_load,
    OPCODE.STORE: vm_store,
    OPCODE.CALL: vm_call,
    OPCODE.RET: vm_ret,
    OPCODE.CALL_RET: vm_call_ret,
    OPCODE.JMP: vm_jmp,
    OPCODE.JNZ: vm_jnz,
    OPCODE.JZ: vm_jz,
}


class VirtualMachine:

    def __init__(self, debug=False, dispatch=dispatch_table):
        self.mem = []
        self.stack = []
        self.channels = defaultdict(Channel)
        self.sp = 0  # stack pointer
        self.bp = 0  # base pointer
        self.sl = 0  # static link
        self.pc = 0  # program counter
        self.clk = 0
        self.debug = debug
        self.dispatch = dispatch

        self._dispatch_register = {
            OPCODE.PUSH_SP: 'sp',
            OPCODE.PUSH_BP: 'bp',
            OPCODE.PUSH_SL: 'sl',
            OPCODE.PUSH_PC: 'pc',
            OPCODE.SET_SP: 'sp',
            OPCODE.SET_BP: 'bp',
            OPCODE.SET_SL: 'sl',
            OPCODE.SET_PC: 'pc',
        }

    def _next(self):
        self.pc += 1
        return self.mem[self.pc - 1]

    def _pop(self):
        self.sp -= 1
        return self.stack[self.sp]

    def _push(self, value):
        if len(self.stack) > self.sp:
            self.stack[self.sp] = value
        else:
            self.stack.append(value)
        self.sp += 1

    def _pick(self, n=0):
        return self.stack[self.sp - n - 1]

    def _play(self):
        frame = self._pop()
        pulse = self._pop()

    def _captrue(self):
        frame = self._pop()
        cbit = self._pop()

    def display(self):
        if not self.debug:
            return
        print(f'State[{self.clk}] ====================')
        print(f'      OP: ', self.mem[self.pc])
        print(f'   STACK: ', self.stack[:self.sp])
        print(f'      BP: ', self.bp)
        print(f'      SL: ', self.sl)
        print(f'      PC: ', self.pc)
        print('')

    def trace(self):
        if not self.debug:
            return
        self.display()

    def run(self, code, step_limit=-1):
        if len(code) > len(self.mem):
            self.mem.extend([0] * (len(code) - len(self.mem)))
        for i, c in enumerate(code):
            self.mem[i] = c
        self.sp = 0  # stack pointer
        self.bp = 0  # base pointer
        self.sl = 0  # static link
        self.pc = 0  # program counter
        self.clk = 0  # clock

        while True:
            self.trace()
            instruction = self._next()
            if self.clk == step_limit:
                break
            self.clk += 1
            if instruction.opcode in self.dispatch:
                self.dispatch[instruction.opcode](self, instruction.argument)
            elif instruction.opcode == OPCODE.NOP:
                continue
            elif instruction.opcode == OPCODE.EXIT:
                break
            elif instruction.opcode in [
                    OPCODE._SP, OPCODE._BP, OPCODE._SL, OPCODE._PC
            ]:
                self._push(
                    getattr(self, self._dispatch_register[instruction.opcode]))
            elif instruction.opcode in [
                    OPCODE._WRITE_SP, OPCODE._WRITE_BP, OPCODE._WRITE_SL,
                    OPCODE._WRITE_PC
            ]:
                setattr(self, self._dispatch_register[instruction.opcode],
                        self._pop())
            else:
                raise RuntimeError(f"unknown command: {instruction}")

