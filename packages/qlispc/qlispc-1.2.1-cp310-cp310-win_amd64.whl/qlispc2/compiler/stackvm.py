from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Any, List, Optional, Union
from collections import defaultdict

class OpCode(IntEnum):
    # No operation
    NOP = auto()
    
    # Stack Operations
    PUSH = auto()  # Push immediate value or value from data segment
    POP = auto()  # Pop value from stack
    DUP = auto()  # Duplicate top value
    SWAP = auto()  # Swap top two values
    OVER = auto()  # Copy second value to top

    # Control Flow
    JMP = auto()  # Unconditional jump
    JZ = auto()  # Jump if zero
    JNZ = auto()  # Jump if not zero
    CALL = auto()  # Call subroutine (immediate = number of arguments)
    RET = auto()  # Return from subroutine
    TAILCALL = auto(
    )  # Tail call optimization (immediate = number of arguments)

    # Memory Operations
    LOAD = auto()  # Load from data segment
    STORE = auto()  # Store to data segment
    LOAD_LOCAL = auto()  # Load local variable relative to frame pointer
    STORE_LOCAL = auto()  # Store local variable relative to frame pointer

    # System
    HALT = auto()  # Stop execution

    # Arithmetic Operations
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()

    # Comparison Operations
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # Bitwise Operations
    AND = auto()
    OR = auto()
    NOT = auto()
    XOR = auto()
    SHL = auto()
    SHR = auto()

    # Type conversion
    TO_INT = auto()
    TO_FLOAT = auto()

    # Math Functions
    ABS = auto()
    SQRT = auto()
    EXP = auto()
    LOG = auto()
    POW = auto()
    MIN = auto()
    MAX = auto()

    # Trigonometric Functions
    SIN = auto()
    COS = auto()
    TAN = auto()
    ASIN = auto()
    ACOS = auto()
    ATAN = auto()
    ATAN2 = auto()

    # Quantum Operations
    PLAY = auto()
    CAPTURE = auto()
    CAPTURE_IQ = auto()
    CAPTURE_TRACE = auto()
    SET_TIME = auto()
    SET_PHASE = auto()
    SET_BIAS = auto()
    ADD_TIME = auto()
    ADD_PHASE = auto()
    ADD_BIAS = auto()
    ALIGN = auto()
    WAIT_UNTIL = auto()


@dataclass
class Instruction:
    opcode: OpCode
    immediate: Optional[int] = None  # Immediate value or data segment address

    def __repr__(self):
        if self.immediate is not None:
            return f"{self.opcode.name}({self.immediate})"
        return self.opcode.name


class StackVM:

    def __init__(self, data_size: int = 1024):
        # Memory segments
        self.code: List[Instruction] = []
        self.data: List[Any] = [0] * data_size

        # Registers
        self.pc: int = 0  # Program Counter
        self.sp: int = 0  # Stack Pointer
        self.fp: int = 0  # Frame Pointer

        # Stack
        self.stack: List[Any] = []

        # Execution control
        self.running: bool = False

        # external functions (negative addresses)
        self.externals: dict[int, callable] = {}

        # Channels
        self.waveforms: dict = defaultdict(list)
        self.captures: dict = defaultdict(list)
        self.times: dict = defaultdict(lambda: 0)
        self.phases: dict = defaultdict(lambda: 0)
        self.biases: dict = defaultdict(lambda: 0)

        # Initialize dispatch table
        self.dispatch = {
            OpCode.NOP: self._nop,
            
            # Stack Operations
            OpCode.PUSH: self._push,
            OpCode.POP: self._pop,
            OpCode.DUP: self._dup,
            OpCode.SWAP: self._swap,
            OpCode.OVER: self._over,

            # Control Flow
            OpCode.JMP: self._jmp,
            OpCode.JZ: self._jz,
            OpCode.JNZ: self._jnz,
            OpCode.CALL: self._call,
            OpCode.RET: self._ret,
            OpCode.TAILCALL: self._tailcall,

            # Memory Operations
            OpCode.LOAD: self._load,
            OpCode.STORE: self._store,
            OpCode.LOAD_LOCAL: self._load_local,
            OpCode.STORE_LOCAL: self._store_local,

            # System Operations
            OpCode.HALT: self._halt,

            # Arithmetic Operations
            OpCode.ADD: self._add,
            OpCode.SUB: self._sub,
            OpCode.MUL: self._mul,
            OpCode.DIV: self._div,
            OpCode.MOD: self._mod,
            OpCode.NEG: self._neg,

            # Comparison Operations
            OpCode.EQ: self._eq,
            OpCode.NE: self._ne,
            OpCode.LT: self._lt,
            OpCode.LE: self._le,
            OpCode.GT: self._gt,
            OpCode.GE: self._ge,

            # Bitwise Operations
            OpCode.AND: self._and,
            OpCode.OR: self._or,
            OpCode.NOT: self._not,
            OpCode.XOR: self._xor,
            OpCode.SHL: self._shl,
            OpCode.SHR: self._shr,

            # Type Conversion
            OpCode.TO_INT: self._to_int,
            OpCode.TO_FLOAT: self._to_float,

            # Math Functions
            OpCode.ABS: self._abs,
            OpCode.SQRT: self._sqrt,
            OpCode.EXP: self._exp,
            OpCode.LOG: self._log,
            OpCode.POW: self._pow,
            OpCode.MIN: self._min,
            OpCode.MAX: self._max,

            # Trigonometric Functions
            OpCode.SIN: self._sin,
            OpCode.COS: self._cos,
            OpCode.TAN: self._tan,
            OpCode.ASIN: self._asin,
            OpCode.ACOS: self._acos,
            OpCode.ATAN: self._atan,
            OpCode.ATAN2: self._atan2,

            # Quantum Operations
            OpCode.PLAY: self._play,
            OpCode.CAPTURE: self._capture,
            OpCode.CAPTURE_IQ: self._capture_iq,
            OpCode.CAPTURE_TRACE: self._capture_trace,
            OpCode.SET_TIME: self._set_time,
            OpCode.SET_PHASE: self._set_phase,
            OpCode.SET_BIAS: self._set_bias,
            OpCode.ADD_TIME: self._add_time,
            OpCode.ADD_PHASE: self._add_phase,
            OpCode.ADD_BIAS: self._add_bias,
            OpCode.ALIGN: self._align,
            OpCode.WAIT_UNTIL: self._wait_until,
        }

    def load_program(self,
                     code: List[Instruction],
                     data: List[Any],
                     externals: dict[int, callable] = None):
        """Load program into VM memory"""
        self.code = code
        if len(data) > len(self.data):
            raise RuntimeError("Data segment is too large")
        self.data[:len(data)] = data
        self.externals = externals or {}
        self.pc = 0
        self.sp = 0
        self.fp = 0
        self.stack = []
        self.running = False

    def run(self):
        """Run program until HALT instruction"""
        self.running = True
        while self.running and self.pc < len(self.code):
            instruction = self.code[self.pc]
            self.pc += 1
            try:
                self.dispatch[instruction.opcode](instruction.immediate)
            except Exception as e:
                self.running = False
                raise e

    def result(self):
        return self.stack[self.sp-1]

    def _push_value(self, value: Any):
        """Helper to push value onto stack"""
        if len(self.stack) > self.sp:
            self.stack[self.sp] = value
        else:
            self.stack.append(value)
        self.sp += 1

    def _pop_value(self) -> Any:
        """Helper to pop value from stack"""
        if self.sp <= 0:
            raise RuntimeError("Stack underflow")
        self.sp -= 1
        return self.stack[self.sp]

    def _peek(self, offset: int = 0) -> Any:
        """Helper to peek at stack value without popping"""
        if self.sp <= offset:
            raise RuntimeError("Stack underflow")
        return self.stack[-(offset + 1)]

    # Instruction implementations
    def _nop(self, _):
        pass

    def _push(self, immediate: Optional[int]):
        """Push immediate value or value from data segment"""
        if immediate is None:
            raise RuntimeError("PUSH requires an immediate value")
        self._push_value(immediate)

    def _pop(self, _):
        """Pop value from stack"""
        self._pop_value()

    def _dup(self, _):
        """Duplicate top value"""
        value = self._peek()
        self._push_value(value)

    def _swap(self, _):
        """Swap top two values"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(b)
        self._push_value(a)

    def _over(self, _):
        """Copy second value to top"""
        if self.sp < 2:
            raise RuntimeError("Stack underflow")
        value = self.stack[-2]
        self._push_value(value)

    def _add(self, _):
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a + b)

    def _sub(self, _):
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a - b)

    def _mul(self, _):
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a * b)

    def _div(self, _):
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a / b)

    def _jmp(self, addr: int):
        """Unconditional jump"""
        if addr is None or addr == 0:
            addr = self._pop_value()
        if addr is None or self.pc + addr < 0 or self.pc + addr >= len(self.code):
            raise RuntimeError(f"Invalid jump address: {addr}")
        self.pc += addr-1

    def _jz(self, addr: int):
        """Jump if top of stack is zero or false
        
        The top of stack can be:
        - A number: jump if it's 0
        - A boolean: jump if it's False
        """
        if addr is None or addr == 0:
            addr = self._pop_value()
        if addr is None or self.pc + addr < 0 or self.pc + addr >= len(self.code):
            raise RuntimeError(f"Invalid jump address: {addr}")
        value = self._pop_value()
        if isinstance(value, bool):
            if not value:
                self.pc += addr-1
        else:
            if value == 0:
                self.pc += addr-1

    def _jnz(self, addr: int):
        """Jump if top of stack is not zero or true
        
        The top of stack can be:
        - A number: jump if it's not 0
        - A boolean: jump if it's True
        """
        if addr is None or addr == 0:
            addr = self._pop_value()
        if addr is None or self.pc + addr < 0 or self.pc + addr >= len(self.code):
            raise RuntimeError(f"Invalid jump address: {addr}")
        value = self._pop_value()
        if isinstance(value, bool):
            if value:
                self.pc += addr-1
        else:
            if value != 0:
                self.pc += addr-1

    def _call(self, nargs: int):
        """Call subroutine with n arguments
        
        Stack before: arg1 arg2 ... argN func_addr
        Stack after: (call frame created)
        
        Frame layout:
        [arg0, arg1, ..., argN, ret_addr, old_fp]
         ^
         fp
        """
        # Get function address from stack
        func_addr = self._pop_value()
        if not isinstance(func_addr, int):
            raise RuntimeError(f"Invalid function address: {func_addr}")

        # Check if this is an external function call (negative address)
        if func_addr < 0:
            self._call_external(func_addr, nargs)
            return

        # Regular function call
        if func_addr >= len(self.code):
            raise RuntimeError(f"Invalid function address: {func_addr}")

        # Save arguments
        if self.sp < nargs:
            raise RuntimeError("Stack underflow in CALL")
        #args = self.stack[self.sp-nargs:self.sp]
        #self.sp -= nargs

        # Save return address and old frame pointer
        old_fp = self.fp
        ret_addr = self.pc

        # Push arguments back in original order (reverse of how we popped them)
        #self.stack[self.sp-nargs:self.sp] = args

        # Set new frame pointer to point to first argument
        self.fp = self.sp - nargs

        # Push return data after arguments
        self._push_value(ret_addr)  # Return address
        self._push_value(old_fp)  # Old frame pointer

        # Jump to function
        self.pc = func_addr

    def _ret(self, _):
        """Return from subroutine
        
        Restores previous frame and jumps to return address
        
        Frame layout:
        [arg0, arg1, ..., argN, ret_addr, old_fp]
         ^
         fp
        """
        # Restore frame pointer and return address
        if self.sp < 3:
            raise RuntimeError("Stack underflow in RET")

        ret_addr, old_fp, return_value = self.stack[self.sp-3:self.sp]

        # Clear arguments by resetting stack pointer
        self.sp = self.fp

        # Restore frame pointer
        self.fp = old_fp

        # Push return value
        self._push_value(return_value)

        # Jump to return address
        self.pc = ret_addr

    def _tailcall(self, nargs: int):
        """Tail call optimization
        
        Instead of creating a new stack frame, reuse the current one
        Stack before: arg1 arg2 ... argN func_addr
        Stack after: arg1 arg2 ... argN ret_addr old_fp
        
        Frame layout:
        [arg0, arg1, ..., argN, ret_addr, old_fp]
         ^
         fp
        """
        if nargs is None:
            raise RuntimeError("TAILCALL requires number of arguments")

        # Get function address
        if self.sp <= 0:
            raise RuntimeError("Stack underflow in TAILCALL")
        func_addr = self._pop_value()
        if not isinstance(func_addr, int):
            raise RuntimeError(f"Invalid function address: {func_addr}")

        # Check if this is an external function call (negative address)
        # For external functions, we can't do tail call optimization since
        # they don't follow the same calling convention, so treat as regular call
        if func_addr < 0:
            self._call_external(func_addr, nargs)
            self._ret(None)
            return

        if func_addr >= len(self.code):
            raise RuntimeError(f"Invalid function address: {func_addr}")

        if self.sp <= nargs:
            raise RuntimeError("Stack underflow in TAILCALL") 

        # Get return data from current frame
        # Old frame pointer is at top of stack
        # Return address is second from top of stack
        # New arguments are the rest of the stack
        ret_addr, old_fp, *new_args = self.stack[self.sp-2-nargs:self.sp]
        self.sp = self.fp + nargs + 2
        self.stack[self.fp:self.sp] = [*new_args, ret_addr, old_fp]
        
        # Jump to function
        self.pc = func_addr

    def _call_external(self, func_addr: int, nargs: int):
        """Call an external function
        
        External functions are raw Python functions that receive their arguments
        and return their result. The VM handles popping arguments from stack
        and pushing the return value.
        """
        if func_addr not in self.externals:
            raise RuntimeError(
                f"Unknown external function at address {func_addr}")

        external_func = self.externals[func_addr]

        # Pop arguments from stack (in reverse order due to stack LIFO nature)
        args = []
        for _ in range(nargs):
            args.append(self._pop_value())

        # Call function with arguments in correct order
        try:
            if nargs == 0:
                result = external_func()
            else:
                result = external_func(*reversed(args))

            # Push result back to stack
            self._push_value(result)

        except Exception as e:
            raise RuntimeError(f"Error in external function {func_addr}: {e}")

    def _load(self, addr: int):
        """Load value from data segment"""
        if addr is None or addr < 0 or addr >= len(self.data):
            raise RuntimeError(f"Invalid data address: {addr}")
        self._push_value(self.data[addr])

    def _store(self, addr: int):
        """Store value to data segment"""
        if addr is None or addr < 0 or addr >= len(self.data):
            raise RuntimeError(f"Invalid data address: {addr}")
        value = self._pop_value()
        self.data[addr] = value

    def _load_local(self, offset: int):
        """Load local variable relative to frame pointer
        
        Frame layout:
        [arg0, arg1, ..., argN, ret_addr, old_fp]
         ^
         fp
        
        offset 0 -> arg0
        offset 1 -> arg1
        etc.
        """
        if offset is None:
            raise RuntimeError("LOAD_LOCAL requires an offset")
        if offset < 0:
            raise RuntimeError(f"Invalid local variable offset: {offset}")
        addr = self.fp + offset  # Load relative to frame pointer
        if addr < 0 or addr >= self.sp:
            raise RuntimeError(f"Invalid local variable offset: {offset}")
        self._push_value(self.stack[addr])

    def _store_local(self, offset: int):
        """Store local variable relative to frame pointer
        
        Frame layout:
        [arg0, arg1, ..., argN, ret_addr, old_fp]
         ^
         fp
        
        offset 0 -> arg0
        offset 1 -> arg1
        etc.
        """
        if offset is None:
            raise RuntimeError("STORE_LOCAL requires an offset")
        if offset < 0:
            raise RuntimeError(f"Invalid local variable offset: {offset}")
        addr = self.fp + offset  # Store relative to frame pointer
        if addr < 0 or addr >= self.sp:
            raise RuntimeError(f"Invalid local variable offset: {offset}")
        value = self._pop_value()
        self.stack[addr] = value

    def _halt(self, _):
        """Stop execution"""
        self.running = False

    def _abs(self, _):
        """Absolute value"""
        value = self._pop_value()
        self._push_value(abs(value))

    def _sqrt(self, _):
        """Square root"""
        value = self._pop_value()
        self._push_value(math.sqrt(value))

    def _exp(self, _):
        """Exponential"""
        value = self._pop_value()
        self._push_value(math.exp(value))

    def _sin(self, _):
        """Sine"""
        value = self._pop_value()
        self._push_value(math.sin(value))

    def _cos(self, _):
        """Cosine"""
        value = self._pop_value()
        self._push_value(math.cos(value))

    def _tan(self, _):
        """Tangent"""
        value = self._pop_value()
        self._push_value(math.tan(value))

    def _asin(self, _):
        """Arcsine"""
        value = self._pop_value()
        self._push_value(math.asin(value))

    def _acos(self, _):
        """Arccosine"""
        value = self._pop_value()
        self._push_value(math.acos(value))

    def _atan(self, _):
        """Arctangent"""
        value = self._pop_value()
        self._push_value(math.atan(value))

    def _atan2(self, _):
        """Arctangent of two arguments"""
        y = self._pop_value()
        x = self._pop_value()
        self._push_value(math.atan2(y, x))

    def _log(self, _):
        """Natural logarithm"""
        value = self._pop_value()
        self._push_value(math.log(value))

    def _pow(self, _):
        """Power"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a**b)

    def _min(self, _):
        """Minimum"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(min(a, b))

    def _max(self, _):
        """Maximum"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(max(a, b))

    def _to_int(self, _):
        """Convert to integer"""
        value = self._pop_value()
        self._push_value(int(value))

    def _to_float(self, _):
        """Convert to float"""
        value = self._pop_value()
        self._push_value(float(value))

    def _and(self, _):
        """Bitwise AND"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a & b)

    def _or(self, _):
        """Bitwise OR"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a | b)

    def _not(self, _):
        """Bitwise NOT"""
        value = self._pop_value()
        self._push_value(~value)

    def _xor(self, _):
        """Bitwise XOR"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a ^ b)

    def _shl(self, _):
        """Bitwise left shift"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a << b)

    def _shr(self, _):
        """Bitwise right shift"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a >> b)

    def _le(self, _):
        """Less than or equal"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a <= b)

    def _gt(self, _):
        """Greater than"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a > b)

    def _lt(self, _):
        """Less than"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a < b)

    def _ge(self, _):
        """Greater than or equal"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a >= b)

    def _eq(self, _):
        """Equal"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a == b)

    def _ne(self, _):
        """Not equal"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a != b)

    def _mod(self, _):
        """Modulus"""
        b = self._pop_value()
        a = self._pop_value()
        self._push_value(a % b)

    def _neg(self, _):
        """Negate"""
        value = self._pop_value()
        self._push_value(-value)

    def _play(self, shape: int):
        """Play quantum state"""
        channel = self._pop_value()
        args = self._pop_value()
        duration = self._pop_value()
        self.waveforms[channel].append((shape, self.times[channel], self.phases[channel], self.biases[channel], args, duration))
        self.times[channel] += duration

    def _capture(self, _):
        """Capture quantum state"""
        channel = self._pop_value()
        args = self._pop_value()
        duration = self._pop_value()
        self.captures[channel].append(('capture', self.times[channel], args, duration))

    def _capture_iq(self, _):
        """Capture quantum state in IQ format"""
        channel = self._pop_value()
        args = self._pop_value()
        duration = self._pop_value()
        self.captures[channel].append(('capture_iq', self.times[channel], args, duration))

    def _capture_trace(self, _):
        """Capture quantum state in trace format"""
        channel = self._pop_value()
        args = self._pop_value()
        duration = self._pop_value()
        self.captures[channel].append(('capture_trace', self.times[channel], args, duration))

    def _set_time(self, _):
        """Set time"""
        channel = self._pop_value()
        self.times[channel] = self._pop_value()

    def _set_phase(self, _):
        """Set phase"""
        channel = self._pop_value()
        self.phases[channel] = self._pop_value()

    def _set_bias(self, _):
        """Set bias"""
        channel = self._pop_value()
        self.biases[channel] = self._pop_value()

    def _add_time(self, _):
        """Add time"""
        channel = self._pop_value()
        self.times[channel] += self._pop_value()

    def _add_phase(self, _):
        """Add phase"""
        channel = self._pop_value()
        self.phases[channel] += self._pop_value()

    def _add_bias(self, _):
        """Add bias"""
        channel = self._pop_value()
        self.biases[channel] += self._pop_value()

    def _align(self, nchannels: int):
        """Align"""
        channels = []
        for channel in range(nchannels):
            channels.append(self._pop_value())
        self.align(channels)

    def _wait_until(self, nchannels: int):
        """Wait until"""
        channels = []
        signal = self._pop_value()
        for channel in range(nchannels):
            channels.append(self._pop_value())
        self.wait_until(channels, signal)

    def align(self, channels: List[int]):
        """Align"""
        t = max(self.times[channel] for channel in channels)
        for channel in channels:
            self.times[channel] = t

    def wait_until(self, channels: List[int], signal: int):
        """Wait until"""
        t = max(self.times[channel] for channel in channels)
        for channel in channels:
            self.times[channel] = t
