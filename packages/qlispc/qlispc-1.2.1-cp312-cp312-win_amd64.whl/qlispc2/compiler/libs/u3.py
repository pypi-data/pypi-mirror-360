from numpy import pi

from qlispc2.compiler.library import gate

__dependencies__ = ['U']


@gate
def u3(qubit, /, theta, phi, lam):
    yield (('U', theta, phi, lam), qubit)


@gate
def u2(qubit, /, phi, lam):
    yield (('U', pi / 2, phi, lam), qubit)


@gate
def u1(qubit, /, lam):
    yield (('VZ', lam), qubit)


@gate
def H(qubit, /):
    yield (('u2', 0, pi), qubit)


@gate
def I(q, /):
    yield (('u3', 0, 0, 0), q)


@gate
def X(q, /):
    yield (('u3', pi, 0, pi), q)


@gate
def Y(q, /):
    yield (('u3', pi, pi / 2, pi / 2), q)


@gate
def Z(q, /):
    yield (('u1', pi), q)


@gate
def S(q, /):
    yield (('u1', pi / 2), q)


@gate(name='-S')
def Sdg(q, /):
    yield (('u1', -pi / 2), q)


@gate()
def T(q, /):
    yield (('u1', pi / 4), q)


@gate(name='-T')
def Tdg(q, /):
    yield (('u1', -pi / 4), q)


@gate(name='X/2')
def sx(q, /):
    yield ('-S', q)
    yield ('H', q)
    yield ('-S', q)


@gate(name='-X/2')
def sxdg(q, /):
    yield ('S', q)
    yield ('H', q)
    yield ('S', q)


@gate(name='Y/2')
def sy(q, /):
    yield ('Z', q)
    yield ('H', q)


@gate(name='-Y/2')
def sydg(q, /):
    yield ('H', q)
    yield ('Z', q)


@gate
def Rx(q, /, theta):
    yield (('u3', theta, -pi / 2, pi / 2), q)


@gate
def Ry(q, /, theta):
    yield (('u3', theta, 0, 0), q)


@gate(name='W/2')
def W2(q, /):
    yield (('u3', pi / 2, -pi / 4, pi / 4), q)


@gate(name='-W/2')
def nW2(q, /):
    yield (('u3', -pi / 2, -pi / 4, pi / 4), q)


@gate(name='V/2')
def V2(q, /):
    yield (('u3', pi / 2, -3 * pi / 4, 3 * pi / 4), q)


@gate(name='-V/2')
def nV2(q, /):
    yield (('u3', -pi / 2, -3 * pi / 4, 3 * pi / 4), q)


@gate
def Rz(q, /, phi):
    yield (('u1', phi), q)
