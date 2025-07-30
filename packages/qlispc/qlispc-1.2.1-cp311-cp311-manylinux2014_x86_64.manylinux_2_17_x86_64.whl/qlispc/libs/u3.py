from math import fmod, pi

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


def u3_2p(q, theta, phi, lam):
    yield (('pi2', -lam), q)
    yield (('pi2', pi - theta - lam), q)
    yield (('VZ', theta + phi + lam), q)


def u3_4p(q, theta, phi, lam):
    yield (('pi2', pi - lam), q)
    yield (('pi2', (theta - lam + phi) / 2), q)
    yield (('pi2', (theta - lam + phi) / 2), q)
    yield (('pi2', pi + phi), q)


def u3_2p_compact(q, theta, phi, lam):

    theta, phi, lam = phase_mod(theta, phi, lam)

    if abs(theta) < EPS:
        yield (('VZ', phi + lam), q)
    elif abs(theta - pi / 2) < EPS:
        yield (('pi2', pi / 2 - lam), q)
        yield (('VZ', phi + lam), q)
    else:
        yield from u3_2p(q, theta, phi, lam)


def u3_4p_compact(q, theta, phi, lam):

    theta, phi, lam = phase_mod(theta, phi, lam)

    if abs(theta - pi / 2) < EPS and abs(phi + lam) < EPS:
        yield (('pi2', pi / 2 - lam), q)
    elif abs(theta - pi) < EPS and abs(phi + lam) < EPS:
        yield (('pi2', pi / 2 - lam), q)
        yield (('pi2', pi / 2 - lam), q)
    elif abs(theta + phi + lam) < EPS:
        yield (('pi2', -lam), q)
        yield (('pi2', -pi - theta - lam), q)
    else:
        yield from u3_4p(q, theta, phi, lam)
