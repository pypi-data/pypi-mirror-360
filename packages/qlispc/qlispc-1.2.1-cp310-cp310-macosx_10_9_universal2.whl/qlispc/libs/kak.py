import numpy as np
from qlisp import A, B, Unitary2Angles, kak_decomposition, seq2mat


def su4_A(qubits, matrix):
    res = kak_decomposition(matrix)

    theta, phi, lam, g = Unitary2Angles(res.single_qubit_operations_before[0])
    yield (('u3', theta, phi, lam), qubits[0])
    theta, phi, lam, g = Unitary2Angles(res.single_qubit_operations_before[1])
    yield (('u3', theta, phi, lam), qubits[1])

    yield (('A', *res.interaction_coefficients), *qubits)

    theta, phi, lam, g = Unitary2Angles(res.single_qubit_operations_after[0])
    yield (('u3', theta, phi, lam), qubits[0])
    theta, phi, lam, g = Unitary2Angles(res.single_qubit_operations_after[1])
    yield (('u3', theta, phi, lam), qubits[1])


def su4_B(qubits, matrix):
    res1 = kak_decomposition(matrix)
    x, y, z = res1.interaction_coefficients

    if z < 0:
        x = np.pi / 2 - x
        z = -z

    beta1 = np.arccos(1 - 4 * np.sin(y)**2 * np.cos(z)**2)
    beta2 = np.arcsin(
        np.sqrt(
            np.cos(2 * y) * np.cos(2 * z) /
            (1 - 2 * np.sin(y)**2 * np.cos(z)**2)))

    res2 = kak_decomposition(
        B @ seq2mat([(('u3', -2 * x, 0, 0), 0),
                     (('u3', -beta1, -beta2, -beta2), 1)]) @ B)

    b0, b1 = res1.single_qubit_operations_before
    a0, a1 = res1.single_qubit_operations_after
    c0, c1 = res2.single_qubit_operations_before
    d0, d1 = res2.single_qubit_operations_after

    b0 = c0.T.conj() @ b0
    b1 = c1.T.conj() @ b1
    a0 = a0 @ d0.T.conj()
    a1 = a1 @ d1.T.conj()

    yield (('u3', *Unitary2Angles(b0)[:3]), qubits[0])
    yield (('u3', *Unitary2Angles(b1)[:3]), qubits[1])

    yield ('B', *qubits)
    yield (('u3', -2 * x, 0, 0), qubits[0])
    yield (('u3', -beta1, -beta2, -beta2), qubits[1])
    yield ('B', *qubits)

    yield (('u3', *Unitary2Angles(a0)[:3]), qubits[0])
    yield (('u3', *Unitary2Angles(a1)[:3]), qubits[1])


def su4_CZ(qubits, matrix):
    res1 = kak_decomposition(matrix)
    x, y, z = res1.interaction_coefficients

    res2 = kak_decomposition(
        seq2mat([
            ('CZ', 1, 0),
            (("u3", np.pi / 2, np.pi / 2 - 2 * z, np.pi), 0),
            (("u3", 2 * x, 0, np.pi), 1),
            ('CZ', 0, 1),
            (("u3", 2 * y, 0, np.pi), 1),
            (("u3", np.pi / 2, 0, np.pi), 0),
            ('CZ', 1, 0),
        ]))

    b0, b1 = res1.single_qubit_operations_before
    a0, a1 = res1.single_qubit_operations_after
    c0, c1 = res2.single_qubit_operations_before
    d0, d1 = res2.single_qubit_operations_after

    b0 = c0.T.conj() @ b0
    b1 = c1.T.conj() @ b1
    a0 = a0 @ d0.T.conj()
    a1 = a1 @ d1.T.conj()

    yield (('u3', *Unitary2Angles(b0)[:3]), qubits[0])
    yield (('u3', *Unitary2Angles(b1)[:3]), qubits[1])

    yield ('CZ', *qubits)
    yield (('u3', np.pi / 2, np.pi / 2 - 2 * z, np.pi), qubits[0])
    yield (('u3', 2 * x, 0, np.pi), qubits[1])
    yield ('CZ', *qubits)
    yield (('u3', np.pi / 2, 0, np.pi), qubits[0])
    yield (('u3', 2 * y, 0, np.pi), qubits[1])
    yield ('CZ', *qubits)

    yield (('u3', *Unitary2Angles(a0)[:3]), qubits[0])
    yield (('u3', *Unitary2Angles(a1)[:3]), qubits[1])


def su4_iSWAP(qubits, matrix):
    res1 = kak_decomposition(matrix)
    x, y, z = res1.interaction_coefficients

    # TODO
    # find a better way to implement this
    raise NotImplementedError
    res2 = kak_decomposition(
        seq2mat([
            ('iSWAP', 1, 0),
            (("u3", np.pi / 2, np.pi / 2 - 2 * z, np.pi), 0),
            (("u3", 2 * x, 0, np.pi), 1),
            ('iSWAP', 0, 1),
            (("u3", 2 * y, 0, np.pi), 1),
            (("u3", np.pi / 2, 0, np.pi), 0),
            ('iSWAP', 1, 0),
        ]))

    b0, b1 = res1.single_qubit_operations_before
    a0, a1 = res1.single_qubit_operations_after
    c0, c1 = res2.single_qubit_operations_before
    d0, d1 = res2.single_qubit_operations_after

    b0 = c0.T.conj() @ b0
    b1 = c1.T.conj() @ b1
    a0 = a0 @ d0.T.conj()
    a1 = a1 @ d1.T.conj()

    yield (('u3', *Unitary2Angles(b0)[:3]), qubits[0])
    yield (('u3', *Unitary2Angles(b1)[:3]), qubits[1])

    yield ('iSWAP', *qubits)
    yield (('u3', np.pi / 2, np.pi / 2 - 2 * z, np.pi), qubits[0])
    yield (('u3', 2 * x, 0, np.pi), qubits[1])
    yield ('iSWAP', *qubits)
    yield (('u3', np.pi / 2, 0, np.pi), qubits[0])
    yield (('u3', 2 * y, 0, np.pi), qubits[1])
    yield ('iSWAP', *qubits)

    yield (('u3', *Unitary2Angles(a0)[:3]), qubits[0])
    yield (('u3', *Unitary2Angles(a1)[:3]), qubits[1])
