import re

from waveforms import cos, pi, square, step

from ..base import Capture


def extract_variable_and_index_if_match(s):
    pattern = r'^(\w+)\[(\d+)\]$'
    match = re.search(pattern, s)

    if match:
        name, index = match.groups()
        return (name, int(index))
    else:
        return (s, 0)


def measure(ctx, qubits, cbit=None):
    qubit, = qubits

    if cbit is None:
        if len(ctx.measures) == 0:
            cbit = 0
        else:
            cbit = max(ctx.measures.keys()) + 1

    if isinstance(cbit, int):
        cbit = ('result', cbit)
    elif isinstance(cbit, str):
        cbit = extract_variable_and_index_if_match(cbit)

    # lo = ctx.cfg._getReadoutADLO(qubit)
    amp = ctx.params['amp']
    duration = ctx.params['duration']
    frequency = ctx.params['frequency']
    bias = ctx.params.get('bias', None)
    signal = ctx.params.get('signal', 'state')
    ring_up_amp = ctx.params.get('ring_up_amp', amp)
    ring_up_time = ctx.params.get('ring_up_time', 50e-9)
    rsing_edge_time = ctx.params.get('rsing_edge_time', 5e-9)
    buffer = ctx.params.get('buffer', 0)
    space = ctx.params.get('space', 0)

    try:
        w = ctx.params['w']
        weight = None
    except:
        weight = ctx.params.get('weight',
                                f'square({duration}) >> {duration/2}')
        w = None

    t = ctx.time[qubit]

    # phi = 2 * np.pi * (lo - frequency) * t

    pulse = (ring_up_amp * (step(rsing_edge_time) >>
                            (t + space / 2 + buffer / 2)) -
             (ring_up_amp - amp) *
             (step(rsing_edge_time) >>
              (t + space / 2 + buffer / 2 + ring_up_time)) - amp *
             (step(rsing_edge_time) >>
              (t + space / 2 + buffer / 2 + duration)))
    yield ('!play', pulse * cos(2 * pi * frequency)), ('readoutLine.RF', qubit)
    # if bias is not None:
    #     yield ('!set_bias', bias), ('Z', qubit)
    if bias is not None:
        b = ctx.biases[('Z', qubit)]
        if isinstance(b, tuple):
            b = b[0]
        pulse = (bias - b) * square(duration + space) >> (duration + space +
                                                          buffer) / 2
        yield ('!play', pulse >> t), ('Z', qubit)

    # pulse = square(2 * duration) >> duration
    # ctx.channel['readoutLine.AD.trigger', qubit] |= pulse.marker

    params = {k: v for k, v in ctx.params.items()}
    params['w'] = w
    params['weight'] = weight
    if not (cbit[0] == 'result' and cbit[1] < 0):
        yield ('!capture',
               Capture(qubit, cbit, t + space / 2 + buffer / 2, signal,
                       params)), cbit
    yield ('!set_time', t + duration + space + buffer), qubit
    yield ('!set_phase', 0), qubit
