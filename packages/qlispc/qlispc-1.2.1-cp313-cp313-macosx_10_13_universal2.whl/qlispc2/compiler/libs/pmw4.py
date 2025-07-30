from math import fmod, pi

from numpy import pi

from qlispc2.compiler.library import gate

__dependencies__ = ['pi/2']

EPS = 1e-9


def phase_mod(theta, phi, lam):
    theta = fmod(theta, 2 * pi)
    if theta < 0:
        theta += 2 * pi
    if theta > pi:
        theta -= pi
        phi += pi
        lam += pi

    phi = fmod(phi, 2 * pi)
    lam = fmod(lam, 2 * pi)
    if phi < 0:
        phi += 2 * pi
    if lam < 0:
        lam += 2 * pi
    if phi + lam >= 2 * pi:
        if phi > lam:
            phi -= 2 * pi
        else:
            lam -= 2 * pi
    if theta == 0:
        lam, phi = 0, lam + phi
    elif theta == pi:
        lam, phi = 0, phi - lam
        if phi < 0:
            phi += 2 * pi
    return theta, phi, lam


def u3_4p_compact(q, theta, phi, lam):

    theta, phi, lam = phase_mod(theta, phi, lam)

    if abs(theta - pi / 2) < EPS and abs(phi + lam) < EPS:
        yield (('pi/2', pi / 2 - lam), q)
    elif abs(theta - pi) < EPS and abs(phi + lam) < EPS:
        yield (('pi/2', pi / 2 - lam), q)
        yield (('pi/2', pi / 2 - lam), q)
    elif abs(theta + phi + lam) < EPS:
        yield (('pi/2', -lam), q)
        yield (('pi/2', -pi - theta - lam), q)
    else:
        yield (('pi/2', pi - lam), q)
        yield (('pi/2', (theta - lam + phi) / 2), q)
        yield (('pi/2', (theta - lam + phi) / 2), q)
        yield (('pi/2', pi + phi), q)


@gate
def U(q, /, theta, phi, lam):
    yield (('pi/2', pi - lam), q)
    yield (('pi/2', (theta - lam + phi) / 2), q)
    yield (('pi/2', (theta - lam + phi) / 2), q)
    yield (('pi/2', pi + phi), q)
