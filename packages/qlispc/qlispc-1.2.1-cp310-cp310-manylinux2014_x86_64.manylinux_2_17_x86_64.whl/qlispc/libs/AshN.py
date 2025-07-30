import numpy as np
from scipy import optimize


def inv_sinc(a):
    return optimize.fsolve(lambda x: np.sinc(x) - a, 1 - a) * np.pi


def AshN_ND(x, y, z):
    t = 2 * x
    a1, a2 = np.sin(y + z) / x, np.sin(y - z) / x
    r1 = inv_sinc(a1) / x
    r2 = inv_sinc(a2) / x
    omega_1 = 1 / 2 * np.sqrt(r1 * r1 - 1)
    omega_2 = 1 / 2 * np.sqrt(r2 * r2 - 1)
    return t, omega_1, omega_2, 0


def AshN_ND_EXT(x, y, z):
    t = np.pi - 2 * x
    a1, a2 = np.sin(y + z) / t * 2, np.sin(y - z) / t * 2
    r1 = inv_sinc(a1) / t * 2
    r2 = inv_sinc(a2) / t * 2
    omega_1 = 1 / 2 * np.sqrt(r1 * r1 - 1)
    omega_2 = 1 / 2 * np.sqrt(r2 * r2 - 1)
    return t, omega_2, omega_1, 0


def T(t, a, b):
    return (1 - a) * b / (
        (2 * a + b) *
        (1 + a + 2 * b)) * np.exp(1j * t * (a + b)) - (1 - a) * (1 + a + b) / (
            (1 - a + b) *
            (1 + a + 2 * b)) * np.exp(-1j * t * (1 + b)) - b * (1 + a + b) / (
                (1 - a + b) * (2 * a + b)) * np.exp(-1j * t * a)


def S(x, y, z):
    return np.exp(1j * (y - x - z)) - np.exp(1j *
                                             (x - y - z)) - np.exp(1j *
                                                                   (z - x - y))


def AshN_EA(x, y, z):
    s = S(x, y, np.abs(z))
    t = (x + y + np.abs(z))
    a, b = optimize.fsolve(
        lambda x:
        [np.real(T(t, x[0], x[1]) - s),
         np.imag(T(t, x[0], x[1]) - s)], [0.5, np.pi / t])
    omega = np.sqrt((1 + a + b) * (1 - a) * b)
    delta = np.sqrt((a + b) * a * (1 + b))
    if z >= 0:  # AshN_EA_plus
        return t, 0, omega, -delta
    else:       # AshN_EA_minus
        return t, omega, 0, delta


if __name__ == '__main__':
    from cirq import kak_decomposition
    from qutip import *

    def U(g, Omega1, Omega2, Delta, duration):
        H = (g / 2 *
             (tensor(sigmax(), sigmax()) + tensor(sigmay(), sigmay())) +
             Omega1 / 2 * tensor(sigmax(), qeye(2)) +
             Omega2 / 2 * tensor(qeye(2), sigmax()) + Delta *
             (tensor(sigmaz(), qeye(2)) + tensor(qeye(2), sigmaz())))

        return (-1j * H * duration).expm()

    g = 1.0

    for x, y, z in [(0, 0, 0), (np.pi / 4, 0, 0), (np.pi / 4, np.pi / 4, 0),
                    (np.pi / 4, np.pi / 8, 0),
                    (np.pi / 4, np.pi / 8, np.pi / 8),
                    (np.pi / 4, np.pi / 8, -np.pi / 8)]:
        for method in [AshN_EA, AshN_ND, AshN_ND_EXT]:
            try:
                t, s, m, d = method(x, y, z)

                Omega1, Omega2, Delta, duration = (s + m) * g, (
                    s - m) * g, d * g, t / g
                ret = np.array(
                    kak_decomposition(
                        U(g, Omega1, Omega2, Delta,
                          duration).data_as()).interaction_coefficients)

                print(method)
                print(f"{Omega1=},\n{Omega2=},\n{Delta=},\n{duration=},\n")
                print((ret, np.array([x, y, z])))
                print(np.allclose(ret, np.array([x, y, z])))
                print()
                print()
            except Exception as e:
                pass
