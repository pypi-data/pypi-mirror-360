from math import pi

from qlispc2.compiler.library import gate


def DRAG(channel, frequency, amp, width, plateau, delta, phi, block_frequency):
    yield ('!play', channel, 'drag', frequency, amp, width, plateau, delta,
           phi, block_frequency)


@gate(name='pi/2',
      query={
          'frequency': "gate.R.{qubit}.params.frequency",
          'amp': "gate.R.{qubit}.params.amp",
          'width': "gate.R.{qubit}.params.width",
          'plateau': "gate.R.{qubit}.params.plateau",
          'delta': "gate.R.{qubit}.params.delta",
          'phase': "gate.R.{qubit}.params.phase",
          'block_frequency': "gate.R.{qubit}.params.block_frequency"
      })
def pi2(qubit, /, phi, *, frequency, amp, width, plateau, delta, phase,
        block_frequency):
    channel = qubit
    yield from DRAG(channel, frequency, amp, width, plateau, delta, phi,
                    block_frequency)
    yield ('VZ', phase), qubit


@gate
def VZ(qubit, /, phi):
    yield ('!add_phase', qubit, phi)


@gate(query="{qubit}.frequency")
def delay(qubit, /, t, *, frequency):
    yield ('!add_time', qubit, t)
    yield ('!add_phase', qubit, 2 * pi * frequency * t)


@gate
def barrier(qubits, /, *, ctx):
    pass


@gate
def measure(qubit, /, cbit):
    pass
