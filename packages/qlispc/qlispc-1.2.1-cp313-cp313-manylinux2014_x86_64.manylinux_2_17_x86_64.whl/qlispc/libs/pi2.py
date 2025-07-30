import numpy as np
from numpy import mod, pi, sign, sum
from waveforms.waveform import (cos, coshPulse, cosPulse, gaussian,
                                general_cosine, mixing, pi, sin, square, zero)
from waveforms.waveform_parser import wave_eval


def get_frequency_phase(ctx, qubit, phi, level1, level2):
    freq = ctx.params.get('frequency', ctx.params.get('freq', 0.5))
    phi = mod(
        phi + ctx.phases_ext[qubit][level1] - ctx.phases_ext[qubit][level2],
        2 * pi)
    phi = phi if abs(level2 - level1) % 2 else phi - pi
    if phi > pi:
        phi -= 2 * pi
    phi = phi / (level2 - level1)

    return freq, phi


def DRAG(t, shape, width, plateau, eps, amp, alpha, beta, delta, freq, phase):
    from waveforms.waveform import drag

    if shape in ['hanning', 'cosPulse', 'CosPulse']:
        if beta == 0:
            block_freq = None
        else:
            block_freq = -1 / (2 * pi) / (beta / alpha)
        return (amp * alpha) * drag(freq, width, plateau, delta, block_freq,
                                    phase, t - width / 2 - plateau / 2)
    elif shape in ['coshPulse', 'CoshPulse']:
        pulse = coshPulse(width, plateau=plateau, eps=eps)
    else:
        pulse = gaussian(width, plateau=plateau)
    I, Q = mixing(amp * alpha * pulse,
                  phase=phase,
                  freq=delta,
                  DRAGScaling=beta / alpha)
    wav, _ = mixing(I >> t, Q >> t, freq=freq)
    return wav


def pi2(ctx, qubits, phi=0, level1=0, level2=1):
    qubit, = qubits

    freq, phase = get_frequency_phase(ctx, qubit, phi, level1, level2)

    amp = ctx.params.get('amp', 0.5)
    shape = ctx.params.get('shape', 'cosPulse')
    width = ctx.params.get('width', 5e-9)
    plateau = ctx.params.get('plateau', 0.0)
    buffer = ctx.params.get('buffer', 0)

    duration = width + plateau + buffer
    if amp != 0:
        alpha = ctx.params.get('alpha', 1)
        beta = ctx.params.get('beta', 0)
        delta = ctx.params.get('delta', 0)
        eps = ctx.params.get('eps', 1)
        channel = ctx.params.get('channel', 'RF')
        t = duration / 2 + ctx.time[qubit]

        if shape == 'S1':
            arg = ctx.params.get('arg', [-2.253, 0.977, 1.029])
            pulse = general_cosine(width, *arg) * sign(-sum(arg[::2]))
            I, Q = mixing(amp * alpha * pulse,
                          phase=phase,
                          freq=delta,
                          DRAGScaling=beta / alpha)
            wav, _ = mixing(I >> t, Q >> t, freq=freq)
        wav = DRAG(t, shape, width, plateau, eps, amp, alpha, beta, delta,
                   freq, phase)
        yield ('!play', wav), (channel, qubit)
    yield ('!add_time', duration), qubit
