from qlispc2.compiler.library import gate


@gate
def Cnot(c, t, /):
    yield ('H', t)
    yield ('CZ', c, t)
    yield ('H', t)


@gate
def crz(c, t, /, lam):

    yield (('u1', lam / 2), t)
    yield ('Cnot', c, t)
    yield (('u1', -lam / 2), t)
    yield ('Cnot', c, t)
