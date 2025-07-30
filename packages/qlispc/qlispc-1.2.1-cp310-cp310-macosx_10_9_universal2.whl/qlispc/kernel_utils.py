import importlib
import inspect
import os
import pathlib
import re
import sys
from concurrent.futures import Future
from typing import Any, Iterable

import dill
import numpy as np
from qlispreg.dicttree import NOTSET
from waveforms.waveform import Waveform, WaveVStack, step

from .base import Capture, Signal, head
from .commands import COMMAND, SYNC, WRITE
from .config import Config
from .library import Library, libraries


def cast_signal(sig):
    """signal类型
    """
    sig_tab = {
        'trace': Signal.trace,
        'iq': Signal.iq,
        'state': Signal.state,
        'count': Signal.count,
        'diag': Signal.diag,
        'population': Signal.population,
        'trace_avg': Signal.trace_avg,
        'iq_avg': Signal.iq_avg,
        'remote_trace_avg': Signal.remote_trace_avg,
        'remote_iq_avg': Signal.remote_iq_avg,
        'remote_state': Signal.remote_state,
        'remote_population': Signal.remote_population,
        'remote_count': Signal.remote_count,
    }
    if isinstance(sig, str):
        if sig == 'raw':
            sig = 'iq'
        try:
            if '|' not in sig:
                return sig_tab[sig]
            _sig = None
            for s in sig.split('|'):
                _s = getattr(Signal, s)
                _sig = _s if not _sig else _sig | _s
            return _sig
        except KeyError:
            pass
    elif isinstance(sig, Signal):
        return sig
    raise ValueError(f'unknow type of signal "{sig}".'
                     f" optional signal types: {list(sig_tab.keys())}")


def dispatch(command: str, args, info):
    from qlispc import Architecture, register_arch

    match command:
        case '!signal':
            info['signal'] = args[0]
        case '!shots':
            info['shots'] = args[0]
        case '!arch':
            if len(args) > 1:
                package = args[0]
                try:
                    mod = importlib.import_module(package)
                    for n, obj in mod.__dict__.items():
                        if isinstance(obj, Architecture):
                            register_arch(obj)
                except:
                    pass
                arch = args[1]
            else:
                arch = args[0]
            info['arch'] = arch
        case '!config':
            info['config'] = args[0]
        case '!set':
            if len(args) == 2:
                info['settings'][args[0]] = args[1]
        case '!waveform_length':
            info['waveform_length'] = args[0]
        case '!path':
            path = os.path.expanduser(args[0])
            if pathlib.Path(path).exists() and os.path.isdir(path):
                if path not in sys.path:
                    sys.path.append(str(path))
                    info['path'].append(str(path))
        case '!import':
            module = args[0]
            lib = args[1]
            try:
                mod = importlib.import_module(module)
                info['libs'].append(getattr(mod, lib))
            except:
                pass
        case _:
            raise ValueError(f"Unknown command: {command}")


def precompile(circuit: str | list | bytes) -> tuple[list | str, dict]:
    if isinstance(circuit, bytes):
        circuit = dill.loads(circuit)

    if isinstance(circuit, str):
        return circuit, {}

    circ = []
    info = {
        'path': [],
        'settings': {},
        'libs': [],
    }

    for c, *args in circuit:
        if isinstance(c, str) and c.startswith('!'):
            dispatch(c, args, info)
        else:
            if len(args) > 1:
                circ.append((c, tuple(args)))
            else:
                circ.append((c, *args))
    return circ, info


def qcompile(circuit: str | list | bytes,
             lib: Library,
             cfg: Config,
             signal,
             shots: int,
             context: dict,
             arch,
             align_right=False,
             waveform_length=98e-6):
    if len(circuit) > 1 and circuit[0] == ('!qlisp2', ):
        from qlispc2 import qcompile2
        return qcompile2(circuit)

    from qlispc import compile, get_arch

    circuit, info = precompile(circuit)

    if 'shots' in info:
        shots = info['shots']
    if 'signal' in info:
        signal = info['signal']
    if 'arch' in info:
        arch = info['arch']
    if info['libs']:
        lib = libraries(*reversed(info['libs']))

    code = compile(circuit, lib=lib, cfg=cfg)
    code.signal = cast_signal(signal)
    code.shots = shots
    code.arch = arch

    if align_right:
        delay = waveform_length - code.end

        code.waveforms = {k: v >> delay for k, v in code.waveforms.items()}
        code.measures = {
            k:
            Capture(v.qubit, v.cbit, v.time + delay, v.signal, v.params,
                    v.hardware, v.shift + delay)
            for k, v in code.measures.items()
        }

    return code, get_arch(code.arch).assembly_code(code, context)


def is_feedable(cmd):
    if isinstance(cmd, WRITE):
        if cmd.address.startswith('gate.'):
            return False
        if re.match(r'[QCM]\d+\..+', cmd.address) and not re.match(
                r'[QCM]\d+\.(setting|waveform)\..+', cmd.address):
            return False
    return True


_window = step(0) << 1e-3


def _eq(a, b):
    if isinstance(a, WaveVStack) or isinstance(b, WaveVStack):
        return False
    if isinstance(a, Waveform) and isinstance(b, Waveform):
        return (a * _window) == (b * _window)
    try:
        return a == b
    except:
        return False


def pre_feed(
    cmds: list[COMMAND],
    state_caches: dict[str, Any] | None = None,
    active_suffixs: Iterable[str] = (),
    active_prefixs: Iterable[str] = ()
) -> dict[str, list[tuple[str, str, Any, str]]]:
    """format data required by feed api of quark

    Args:
        cmds (list): commands to be executed
    """
    commands = []

    writes = {}
    updates = {}
    others = []

    for cmd in cmds:
        if is_feedable(cmd):
            if isinstance(cmd, WRITE):
                if (state_caches is not None and cmd.address in state_caches
                        and not cmd.address.startswith(tuple(active_prefixs))
                        and not cmd.address.endswith(tuple(active_suffixs))):
                    try:
                        start = f"{cmd.address.split('.')[0]}.calibration."
                        if any([key.startswith(start) for key in updates]):
                            pass
                        elif _eq(state_caches[cmd.address], cmd.value):
                            continue
                    except:
                        print(cmd.address)
                        print(cmd.value.bounds)
                        print(cmd.value.seq)
                        print()
                        print(state_caches[cmd.address].bounds)
                        print(state_caches[cmd.address].seq)
                        raise
                state_caches[cmd.address] = cmd.value
                if not (isinstance(cmd.value, tuple)
                        and cmd.value[0] is NOTSET):
                    writes[cmd.address] = (type(cmd).__name__, cmd.value)
            # elif isinstance(cmd, SYNC):
            #     commands.extend(list(writes.items()))
            #     writes = {}
            #     commands.extend(others)
            #     others = []
            #     # commands.append(
            #     #     (cmd.address, (type(cmd).__name__, cmd.value)))
            else:
                others.append((cmd.address, (type(cmd).__name__, cmd.value)))
        else:
            updates[cmd.address] = ('UPDATE', cmd.value)
    commands.extend(list(writes.items()))
    commands.extend(others)

    if len(commands) == 0:
        raise ValueError('No commands to be executed')

    cmds = {'UPDATE': [], 'WRITE': [], 'TRIG': [], 'READ': []}
    # cmds = {'WRITE': [], 'TRIG': [], 'READ': []}

    for address, (cmd, value) in updates.items():
        cmds['UPDATE'].append((cmd, address, value, ''))

    for address, (cmd, value) in commands:
        cmds[cmd].append((cmd, address, value, ''))
    """
        cmds: dict
            in the form of {
                'INIT': [('UPDATE', address, value, ''), ...],
                'step1': [('WRITE', address, value, ''), ...],
                'step2': [('WAIT', '', delay, '')],
                'step3': [('TRIG', address, 0, ''), ...],
                ...
                'READ': [('READ', address, 0, ''), ...]
            }
        """
    return cmds


def get_raw_channel_info(address: str, mapping: dict[str, str],
                         cfg: Config) -> str | dict | None:
    for k, v in mapping.items():
        if address.endswith(k):
            break
    else:
        return address

    prefix = address[:-len(k)]
    channel_type, property = v.split('.')
    config = cfg.query(prefix)
    channel = config['channel'][channel_type]
    if channel is None:
        return None
    calibration = config['calibration'][channel_type]
    if not isinstance(calibration, dict):
        calibration = {}
    sample_rate = cfg.query('dev.' + channel.split('.')[0] + '.srate')
    if not isinstance(sample_rate, (int, float)):
        sample_rate = None
    return {
        'channel': channel,
        'property': property,
        'calibration': calibration,
        'sample_rate': sample_rate,
        'LEN': config['waveform'].get('LEN', 99e-6)
    }


def get_all_channels(cfg):
    d = cfg.export()
    mapping = {}
    ch_types = set()
    for k, v in d['etc']['dirver']['mapping'].items():
        mapping['.' + '.'.join(k.split('_'))] = v
        if k.startswith('waveform_'):
            ch_types.add(k.split('_')[-1])
    channels = set()
    for k, v in d.items():
        if isinstance(v, dict) and 'channel' in v and 'waveform' in v:
            for ch in ch_types:
                try:
                    info = get_raw_channel_info(f'{k}.waveform.{ch}', mapping,
                                                cfg)
                    if isinstance(info, dict):
                        ins = info['channel'].split('.')[0]
                        if ins in d['dev']:
                            channels.add(
                                cfg._map_repetitive_channel(
                                    f'{k}.waveform.{ch}'))
                except:
                    pass
    return channels


def get_sample_method(name):
    import importlib
    import inspect

    if name is None:
        return _sample_waveform

    module_name, function_name = name.rsplit('.', 1)

    try:
        sample_method = importlib.import_module(
            module_name).__dict__[function_name]
    except:
        raise ValueError(f"Sample method {name} not found.")
    if not callable(sample_method):
        raise ValueError(f"Sample method {name} is not callable.")
    sig = inspect.signature(sample_method)
    for key in [
            'waveform', 'calibration', 'sample_rate', 'start', 'stop',
            'support_waveform_object', 'with_x'
    ]:
        if key not in sig.parameters:
            raise ValueError(
                f"Sample method {name} should have '{key}' as a parameter.")
    return sample_method


def sample_waveform(waveform,
                    calibration,
                    sample_rate,
                    start=0,
                    stop=100e-6,
                    support_waveform_object=False,
                    with_x=False):
    """
    Sample a waveform with calibration parameters.

    Parameters
    ----------
    waveform : Waveform
        The waveform to be sampled.
    calibration : dict
        Calibration parameters. It should contain 'delay' and 'distortion'.
        Example:
        ```
            {
                'delay': 0.0,
                'distortion': {
                    'decay': [(0.1, 1e-6), (0.2, 2e-6)]
                }
            }
        ```
        'decay' is a list of (amplitude, decay time) or
                (amplitude list, decay time list) pairs.
    sample_rate : int | float
        Sample rate.
    start : int | float
        Start time of the sampled waveform.
    stop : int | float
        Stop time of the sampled waveform.
    support_waveform_object : bool
        Whether to return a Waveform object. Some AWG drivers support sending
        Waveform object rather than ndarray.
    with_x : bool
        Whether to return the x axis (used for plotting).
    """

    sample_method = get_sample_method(calibration.get('sample_method', None))
    return sample_method(waveform,
                         calibration,
                         sample_rate,
                         start,
                         stop,
                         support_waveform_object=support_waveform_object,
                         with_x=with_x)


def _sample_waveform(waveform,
                     calibration,
                     sample_rate,
                     start=0,
                     stop=100e-6,
                     support_waveform_object=False,
                     with_x=False):
    from wath.signal import correct_reflection, exp_decay_filter, predistort

    waveform >>= calibration.get('delay', 0)
    if waveform.start is None:
        waveform.start = start
    if waveform.stop is None:
        waveform.stop = stop
    if waveform.sample_rate is None:
        waveform.sample_rate = sample_rate

    if support_waveform_object:
        return waveform

    distortion_params = calibration.get('distortion', {})
    if not isinstance(distortion_params, dict):
        distortion_params = {}

    points = waveform.sample()

    filters = []
    ker = None
    if 'decay' in distortion_params and isinstance(distortion_params['decay'],
                                                   (list, tuple, np.ndarray)):
        for amp, tau in distortion_params.get('decay', []):
            a, b = exp_decay_filter(amp, tau, sample_rate)
            filters.append((b, a))

    length = len(points)
    if length > 0:
        last = points[-1]
        try:
            points = predistort(points, filters, ker, initial=last)
        except:
            points = np.hstack([np.full((length, ), last), points])
            points = predistort(points, filters, ker)[length:]
        points[-1] = last

    if with_x:
        return np.linspace(start, stop, len(points), endpoint=False), points
    else:
        return points


def _call_func_with_kwds(func, args, kwds):
    sig = inspect.signature(func)
    for p in sig.parameters.values():
        if p.kind == p.VAR_KEYWORD:
            return func(*args, **kwds)
    kw = {
        k: v
        for k, v in kwds.items()
        if k in list(sig.parameters.keys())[len(args):]
    }
    args = [arg.result() if isinstance(arg, Future) else arg for arg in args]
    kw = {k: v.result() if isinstance(v, Future) else v for k, v in kw.items()}
    return func(*args, **kw)


def try_to_call(x, args, kwds):
    if callable(x):
        return _call_func_with_kwds(x, args, kwds)
    return x
