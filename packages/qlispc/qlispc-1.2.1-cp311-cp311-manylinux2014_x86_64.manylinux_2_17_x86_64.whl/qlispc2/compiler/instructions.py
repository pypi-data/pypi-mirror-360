from typing import Any, Generator, NamedTuple

from .opcode import OPCODE


class Instruction(NamedTuple):
    opcode: OPCODE
    argument: Any = None
    label: str = ''
    trace: tuple = ()

    def __str__(self):
        if self.argument is None:
            return f"{self.opcode.name:10s} {self.label}"
        return f"{self.opcode.name:10s} {self.argument} {self.label}"


class Channel(NamedTuple):
    qubits: tuple[str, ...]
    type: str


def capture_trace(channel,
                  cbit,
                  duration,
                  label='',
                  trace=()) -> Generator[Instruction, None, None]:
    """
    Capture a waveform from a channel.

    Args:
        channel: The channel to capture.
        cbit: The label of the result.
    """
    yield Instruction(OPCODE.PUSH, (duration, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (cbit, ), label=label, trace=trace)
    yield Instruction(OPCODE.CAPTURE_TRACE, (channel, ),
                      label=label,
                      trace=trace)


def capture_iq(channel,
               cbit,
               duration,
               frequency,
               label='',
               trace=()) -> Generator[Instruction, None, None]:
    """
    Capture a waveform from a channel.

    Args:
        channel: The channel to capture.
        cbit: The label of the result.
    """
    yield Instruction(OPCODE.PUSH, (frequency, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (duration, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (cbit, ), label=label, trace=trace)
    yield Instruction(OPCODE.CAPTURE_IQ, (channel, ), label=label, trace=trace)


def capture(channel,
            cbit,
            qubit,
            label='',
            trace=()) -> Generator[Instruction, None, None]:
    """
    Capture a waveform from a channel.

    Args:
        channel: The channel to capture.
        cbit: The label of the result.
    """
    yield Instruction(OPCODE.PUSH, (qubit, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (cbit, ), label=label, trace=trace)
    yield Instruction(OPCODE.CAPTURE, (channel, ), label=label, trace=trace)


def play(channel,
         shape,
         frequency,
         phase,
         label='',
         trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (phase, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (frequency, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (shape, ), label=label, trace=trace)
    yield Instruction(OPCODE.PLAY, (channel, ), label=label, trace=trace)


def set_time(channel,
             time,
             label='',
             trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (time, ), label=label, trace=trace)
    yield Instruction(OPCODE.SET_TIME, (channel, ), label=label, trace=trace)


def set_phase(channel,
              frequency,
              phase,
              label='',
              trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (phase, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (frequency, ), label=label, trace=trace)
    yield Instruction(OPCODE.SET_PHASE, (channel, ), label=label, trace=trace)


def set_phase_ext(channel,
                  frequency,
                  phase,
                  label='',
                  trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (phase, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (frequency, ), label=label, trace=trace)
    yield Instruction(OPCODE.SET_PHASE_EXT, (channel, ),
                      label=label,
                      trace=trace)


def set_bias(channel,
             bias,
             label='',
             trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (bias, ), label=label, trace=trace)
    yield Instruction(OPCODE.SET_BIAS, (channel, ), label=label, trace=trace)


def set_instrument(channel,
                   key,
                   value,
                   label='',
                   trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (value, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (key, ), label=label, trace=trace)
    yield Instruction(OPCODE.SET, (channel, ), label=label, trace=trace)


def add_time(channel,
             time,
             label='',
             trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (time, ), label=label, trace=trace)
    yield Instruction(OPCODE.ADD_TIME, (channel, ), label=label, trace=trace)


def add_phase(channel,
              frequency,
              phase,
              label='',
              trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (phase, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (frequency, ), label=label, trace=trace)
    yield Instruction(OPCODE.ADD_PHASE, (channel, ), label=label, trace=trace)


def add_phase_ext(channel,
                  frequency,
                  phase,
                  label='',
                  trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (phase, ), label=label, trace=trace)
    yield Instruction(OPCODE.PUSH, (frequency, ), label=label, trace=trace)
    yield Instruction(OPCODE.ADD_PHASE_EXT, (channel, ),
                      label=label,
                      trace=trace)


def add_bias(channel,
             bias,
             label='',
             trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.PUSH, (bias, ), label=label, trace=trace)
    yield Instruction(OPCODE.ADD_BIAS, (channel, ), label=label, trace=trace)


def nop(label='', trace=()) -> Generator[Instruction, None, None]:
    yield Instruction(OPCODE.NOP, label=label, trace=trace)
