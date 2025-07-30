from .precompler import precompile

def qcompile(circuit):
    assert len(circuit) >= 1 and circuit[0] == (
        '!qlispc2', ), "circuit must start with ('!qlispc2', )"
    circuit = precompile(circuit)
    return circuit
