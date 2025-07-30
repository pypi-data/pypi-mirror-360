import numpy as np
from scipy.optimize import minimize


def head(st):
    if isinstance(st, str):
        return st
    elif isinstance(st[0], str):
        return st[0]
    else:
        return head(st[0])


def circuit_simplify_level1(circuit):
    from qlisp import Unitary2Angles, seq2mat

    ret = []
    stack = {}
    for gate, *qubits in circuit:
        if len(qubits) > 1 or head(gate) in ['Measure', 'Reset']:
            for qubit in qubits:
                if qubit in stack:
                    U = stack.pop(qubit)
                    theta, phi, lam, *_ = Unitary2Angles(U)
                    ret.append(
                        (('u3', float(theta), float(phi), float(lam)), qubit))
            ret.append((gate, *qubits))
        else:
            qubit, = qubits
            stack[qubit] = seq2mat([(gate, 0)]) @ stack.get(qubit, np.eye(2))
    for qubit, U in stack.items():
        theta, phi, lam, *_ = Unitary2Angles(U)
        ret.append((('u3', float(theta), float(phi), float(lam)), qubit))
    return ret


def circuit_simplify_level2(circ, add_barrier: bool = True):
    ret = []

    while True:
        blocked = set()
        stack = []
        rest = []
        for gate, *qubits in circ[::-1]:
            if any(q in blocked for q in qubits):
                rest.append((gate, *qubits))
                blocked.update(qubits)
            elif len(qubits) == 1:
                ret.append((gate, *qubits))
            else:
                blocked.update(qubits)
                stack.append((gate, *qubits))
        if stack:
            ret.append(('Barrier', *blocked))
            ret.extend(stack)
            ret.append(('Barrier', *blocked))
        if not rest:
            break
        circ = rest[::-1]
    circ = ret[::-1]
    #return circ

    actived = set()
    ret = []
    temp = []
    for gate, *qubits in circ:
        actived.update(qubits)
        if len(qubits) == 1:
            temp.append((gate, *qubits))
        elif head(gate) == 'Barrier':
            ret.append(('Barrier', *actived))
            ret.extend(temp)
            ret.append(('Barrier', *actived))
            temp = []
        else:
            ret.append((gate, *qubits))

    circ = []
    last = ''
    for gate, *qubits in ret + temp:
        if head(gate) == 'Barrier':
            last = head(gate)
            continue
        if last == 'Barrier' and add_barrier:
            circ.append(('Barrier', *actived))
        circ.append((gate, *qubits))
        last = head(gate)

    return circ


def circuit_2(x, n):
    circ = []
    if n == 0:
        return [(('u3', *x[:3]), 0), (('u3', *x[3:6]), 1)]
    for i in range(n):
        circ.extend([(('u3', *x[6 * i:6 * i + 3]), 0),
                     (('u3', *x[6 * i + 3:6 * i + 6]), 1), ('CZ', 0, 1)])
    i += 1
    circ.extend([
        (('u3', *x[6 * i:6 * i + 3]), 0),
        (('u3', *x[6 * i + 3:6 * i + 6]), 1),
    ])
    return circ


def loss(x, U, n):
    from qlisp import seq2mat, synchronize_global_phase

    return np.sum(
        np.abs(
            synchronize_global_phase(seq2mat(circuit_2(x, n))) -
            synchronize_global_phase(U))**2)


def SU4_to_circuit(U):
    for n in range(4):
        x0 = np.zeros(6 * n + 6)
        res = minimize(loss,
                       x0,
                       args=(U, n),
                       bounds=[(-np.pi, np.pi) if i % 3 else (0, np.pi)
                               for i in range(6 * n + 6)])
        if res.fun < 1e-10:
            return circuit_2(res.x, n)
    return circuit_2(res.x, n)


def _find_stack(stack, qubits):
    if qubits in stack:
        return qubits
    elif qubits[::-1] in stack:
        return qubits[::-1]
    else:
        ret = []
        for k in stack:
            if set(qubits) & set(k):
                ret.append(k)
                if len(ret) > 1:
                    return ret
        return ret


def circuit_simplify_level3(circuit):
    from qlisp import Unitary2Angles, seq2mat

    ret = []
    stack = {}
    for gate, *qubits in circuit:
        qubits = tuple(qubits)
        key = _find_stack(stack, qubits)
        if len(qubits) > 2:
            pass
        elif isinstance(key, list):
            for qubit in key:
                U = stack.pop(qubit)
                theta, phi, lam, *_ = Unitary2Angles(U)
                ret.append((('u3', theta, phi, lam), qubit))
            ret.append((gate, *qubits))
        else:
            qubit, = qubits
            stack[qubit] = seq2mat([(gate, 0)]) @ stack.get(qubit, np.eye(2))

    for qubits, U in stack.items():
        if len(qubits) == 2:
            for g, *q in SU4_to_circuit(U):
                ret.append((g, *[qubits[i] for i in q]))
        else:
            qubit, = qubits
            theta, phi, lam, *_ = Unitary2Angles(U)
            ret.append((('u3', theta, phi, lam), qubit))
    return ret
