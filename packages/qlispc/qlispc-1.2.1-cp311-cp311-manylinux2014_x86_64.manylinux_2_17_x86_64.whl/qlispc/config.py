from __future__ import annotations

import copy
import json
import pickle
import random
import re
import warnings
from abc import ABC, abstractmethod
from itertools import chain, permutations
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np
from qlispreg.dicttree import flattenDict as _flattenDict
from qlispreg.dicttree import flattenDictIter as _flattenDictIter
from qlispreg.dicttree import foldDict as _foldDict
from qlispreg.dicttree import update_tree as _update

from .base import (ABCCompileConfigMixin, ADChannel, AWGChannel, GateConfig,
                   MultADChannel, MultAWGChannel, getConfig,
                   set_config_factory)

_NO_DEFAULT = object()


def _query(q, dct):
    return {
        k.removeprefix(q + '.'): v
        for k, v in dct.items() if k.startswith(q + '.')
    }


def randomStr(n):
    s = ('abcdefghijklmnopqrstuvwxyz'
         'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
         '0123456789')
    return ''.join(random.choices(s, k=n))


def mixin(o: object, *traits: type) -> object:
    bases = (o.__class__, *traits)
    name = '_'.join([cls.__name__ for cls in bases])
    name = '_'.join([name, randomStr(6)])
    cls = type(name, bases, {})
    o.__class__ = cls
    return o


class TraitMeta(type):
    _traits = {}

    def __new__(cls, name, bases, namespace):
        cls = super().__new__(cls, name, bases, namespace)
        if name != 'Trait':
            TraitMeta._traits[name] = cls
        return cls


class Trait(metaclass=TraitMeta):
    pass


def queryKey(q, dct, prefix=None):
    if prefix is None:
        prefix = []

    keys = q.split('.', maxsplit=1)

    if not isinstance(dct, dict):
        k = '.'.join(prefix)
        raise KeyError(
            f"Query {k}.{q} error, type '{k}' is {type(dct)}, not dict.")
    try:
        sub = dct[keys[0]]
    except KeyError:
        k = '.'.join([*prefix, keys[0]])
        raise KeyError(
            f"Query {'.'.join([*prefix, q])} error, key '{k}' not found.")

    if len(keys) == 1:
        return sub

    else:
        return queryKey(keys[1], sub, [*prefix, keys[0]])


def query(q, dct, prefix=None):
    if isinstance(q, str):
        return queryKey(q, dct, prefix)
    elif isinstance(q, list):
        return [query(sub_q, dct, prefix) for sub_q in q]
    elif isinstance(q, tuple):
        return tuple([query(sub_q, dct, prefix) for sub_q in q])
    elif isinstance(q, set):
        return {sub_q: query(sub_q, dct, prefix) for sub_q in q}
    elif isinstance(q, dict):
        if prefix is None:
            prefix = []
        ret = {}
        for k, sub_q in q.items():
            if sub_q is None:
                ret[k] = queryKey(k, dct, prefix)
            else:
                ret[k] = query(sub_q, queryKey(k, dct, prefix), [*prefix, k])
        return ret
    else:
        raise TypeError


def setKey(q, value, dct, prefix=None):
    if prefix is None:
        prefix = []

    keys = q.split('.', maxsplit=1)

    if len(keys) == 1:
        if keys[0] in dct and isinstance(dct[keys[0]],
                                         dict) and not isinstance(value, dict):
            k = '.'.join([*prefix, keys[0]])
            raise ValueError(f'try to set a dict {k} to {type(value)}')
        else:
            dct[keys[0]] = value
    else:
        if keys[0] in dct and isinstance(dct[keys[0]], dict):
            sub = dct[keys[0]]
        elif keys[0] in dct and not isinstance(dct[keys[0]], dict):
            k = '.'.join([*prefix, keys[0]])
            raise ValueError(f'try to set a dict {k} to {type(value)}')
        else:
            sub = {}
            dct[keys[0]] = sub
        setKey(keys[1], sub, [*prefix, keys[0]])


class ConfigSection(dict):

    def __init__(self, cfg: BaseConfig, key: str):
        self._cfg_ = cfg
        self._key_ = key

    def __setitem__(self, key: str, value: Any) -> None:
        if self._cfg_ is None:
            self._modified_ = True
        else:
            self._cfg_._modified_ = True
        if isinstance(value, dict) and not isinstance(value, ConfigSection):
            key, *traits = key.split(':')
            if self._cfg_ is None:
                cfg = self
                k = key
            else:
                cfg = self._cfg_
                k = '.'.join([self._key_, key])
            d = ConfigSection(cfg, k)
            d.update(value)
            value = d
        elif isinstance(value, ConfigSection):
            value.__class__ = ConfigSection
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> ValueType:
        key, *traits = key.split(':')
        if self._cfg_ is not None:
            d = self._cfg_.query(self._key_)
            if self is not d:
                self.update(d)
        ret = super().__getitem__(key)
        if isinstance(ret, ConfigSection) and len(traits) > 0:
            traits = [
                TraitMeta._traits[n] for n in traits if n in TraitMeta._traits
            ]
            mixin(ret, *traits)
        return ret

    def __delitem__(self, key: str) -> None:
        if self._cfg_ is None:
            self._modified_ = True
        else:
            self._cfg_._modified_ = True
        return super().__delitem__(key)

    def __delattr__(self, name: str) -> None:
        if name in self:
            return self.__delitem__(name)
        else:
            return super().__delattr__(name)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.__getattribute__(name)
        except:
            try:
                return self.__getitem__(name)
            except:
                raise AttributeError(f'Not Find Attr: {name}')

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self:
            self.__setitem__(name, value)
        else:
            super().__setattr__(name, value)

    def __deepcopy__(self, memo):
        dct = {k: copy.deepcopy(v) for k, v in self.items()}
        return dct

    def query(self, q: Union[str, set, tuple, list,
                             dict]) -> Union[dict, ValueType]:
        if self._key_ is None:
            prefix = []
        else:
            prefix = self._key_.split('.')
        return query(q, self, prefix=prefix)

    def set(self, q, value):
        if self._key_ is None:
            prefix = []
        else:
            prefix = self._key_.split('.')
        setKey(q, value, self, prefix=prefix)

    def update(self, other):
        _update(self, other)


ValueType = Union[str, int, float, list, ConfigSection]


class BaseConfig(ConfigSection):

    def __init__(self,
                 path: Optional[Union[str, Path]] = None,
                 backup: bool = False):
        super().__init__(None, None)
        if isinstance(path, str):
            path = Path(path)
        self._path_ = path
        self._backup_ = backup
        self._modified_ = False

        if self._path_ is None:
            return
        if self._path_.exists():
            self.reload()
            if '__version__' not in self:
                self['__version__'] = 1
        else:
            self._path_.parent.mkdir(parents=True, exist_ok=True)
            self['__version__'] = 1
            self._modified_ = True
            self.commit()

    def commit(self):
        if not self._modified_ or self._path_ is None:
            return
        if self._backup_ and self._path_.exists():
            v = self['__version__']
            bk = self._path_.with_stem(self._path_.stem + f"_{v}")
            self._path_.rename(bk)
        with self._path_.open('w') as f:
            self['__version__'] = self['__version__'] + 1
            json.dump(self, f, indent=4)
            self._modified_ = False

    def rollback(self):
        if not self._modified_ or self._path_ is None:
            return
        self.reload()

    def reload(self):
        with self._path_.open('r') as f:
            dct = json.load(f)
            self.clear()
            self.update(dct)
            self._modified_ = False

    @classmethod
    def fromdict(cls, d: dict) -> BaseConfig:
        ret = cls()
        ret.update(d)
        return ret


class CompileConfigMixin(ABCCompileConfigMixin):

    def _getAWGChannel(self, name, *qubits) -> Union[str, dict]:

        def _getSharedCoupler(qubits):
            s = set(qubits[0]['couplers'])
            for qubit in qubits[1:]:
                s = s & set(qubit['couplers'])
            return s

        qubits = [self.getQubit(q) for q in qubits]

        if name.startswith('readoutLine.'):
            name = name.removeprefix('readoutLine.')
            rl = self.getReadoutLine(qubits[0]['readoutLine'])
            chInfo = rl.query('channels.' + name)
        elif name.startswith('coupler.'):
            name = name.removeprefix('coupler.')
            c = _getSharedCoupler(qubits).pop()
            c = self.getCoupler(c)
            chInfo = c.query('channels.' + name)
        else:
            chInfo = qubits[0].query('channels.' + name)
        if isinstance(chInfo, dict):
            return self._makeMultAWGChannel(chInfo)
        else:
            return self._makeAWGChannel(chInfo)

    def _makeAWGChannel(self, name: str) -> AWGChannel:
        info = {'name': name}
        if re.match(r'.*\.Marker[0-9]$', name):
            ch = self.getChannel(name[:name.rfind('.')])
        else:
            ch = self.getChannel(name)
        info['sampleRate'] = ch.params.sampleRate
        return AWGChannel(**info)

    def _makeMultAWGChannel(self, chInfo: dict) -> MultAWGChannel:
        info = {}
        if 'I' in chInfo:
            info['I'] = self._makeAWGChannel(chInfo['I'])
        if 'Q' in chInfo:
            info['Q'] = self._makeAWGChannel(chInfo['Q'])
        if 'LO' in chInfo:
            lo = self.getChannel(chInfo['LO'])
            info['lo_freq'] = lo.status.frequency
        return MultAWGChannel(**info)

    def _getADChannel(self, qubit) -> Union[str, dict]:
        rl = self.getQubit(qubit).readoutLine
        rl = self.getReadoutLine(rl)
        chInfo = rl.channels.AD

        if isinstance(chInfo, str):
            return self._makeADChannel(chInfo)
        else:
            return self._makeMultADChannel(chInfo)

    def _makeADChannel(self,
                       name: str,
                       trigger: str = '',
                       triggerDelay: float = 0) -> ADChannel:
        info = {'name': name}
        ch = self.getChannel(name)
        info['sampleRate'] = ch.params.sampleRate
        info['triggerDelay'] = triggerDelay
        info['trigger'] = trigger
        return ADChannel(**info)

    def _makeMultADChannel(self, chInfo: dict) -> MultADChannel:
        info = {}
        if 'I' in chInfo:
            info['I'] = self._makeADChannel(chInfo['I'],
                                            chInfo.get('trigger', ''),
                                            chInfo.get('triggerDelay', 0))
        if 'Q' in chInfo:
            info['Q'] = self._makeADChannel(chInfo['Q'],
                                            chInfo.get('trigger', ''),
                                            chInfo.get('triggerDelay', 0))
        if 'IQ' in chInfo:
            info['IQ'] = self._makeADChannel(chInfo['IQ'],
                                             chInfo.get('trigger', ''),
                                             chInfo.get('triggerDelay', 0))
        if 'Ref' in chInfo:
            info['Ref'] = self._makeADChannel(chInfo['Ref'],
                                              chInfo.get('trigger', ''),
                                              chInfo.get('triggerDelay', 0))
        if 'LO' in chInfo:
            lo = self.getChannel(chInfo['LO'])
            info['LO'] = chInfo['LO']
            info['lo_freq'] = lo.status.frequency
            info['lo_power'] = lo.status.power
        return MultADChannel(**info)

    def _getGateConfig(self, name, *qubits, type=None) -> GateConfig:
        try:
            gate = self.getGate(name, *qubits)
        except:
            return GateConfig(name, qubits)
        if type is None:
            type = gate.get('default_type', 'default')
        if type not in gate and 'params' in gate:
            params = gate['params']
        else:
            try:
                params = gate[type]
            except KeyError:
                raise KeyError(f'Gate {name} has no type {type}')
        return GateConfig(name, gate['qubits'], type, params)

    def _getAllQubitLabels(self) -> list[str]:
        return sorted(self['chip']['qubits'].keys(), key=lambda s: int(s[1:]))


class Config(BaseConfig, CompileConfigMixin):

    def __init__(self, path: Optional[Union[str, Path]] = None):
        super().__init__(path)
        if 'station' not in self:
            self.update({
                'station': {
                    'name': "",
                    'instruments': {},
                    'channels': {},
                    'params': {},
                    'status': {},
                    'calibrations': {}
                },
                'chip': {
                    'qubits': {},
                    'couplers': {},
                    'readoutLines': {},
                    'params': {},
                    'status': {},
                    'calibrations': {
                        'fluxCrosstalk': [],
                        'rfCrosstalk': []
                    }
                },
                'gates': {
                    'Measure': {},
                    'Reset': {},
                    'rfUnitary': {},
                    'CZ': {},
                    'iSWAP': {},
                    'CR': {
                        '__order_senstive__': True
                    }
                }
            })

    def newObject(self,
                  section,
                  key,
                  template=None,
                  properties=('params', 'status', 'calibrations')):
        try:
            d = self.query('.'.join([section, key]))
            return d
        except:
            pass
        d = self
        for k in chain(section.split('.'), key.split('.')):
            if k not in d:
                d[k] = {}
            d = d[k]
        if template is not None:
            d.update(template)
        for k in properties:
            if k not in d:
                d[k] = {}
        return d

    def newInstrument(self, name, driver, address, **params):
        d = self.newObject('station.instruments', name, {
            'dirver': driver,
            'address': address,
            'params': params
        })
        return d

    def newChannel(self, name, instrument='', channel=1, **params):
        try:
            self.getInstrument(instrument)
        except:
            warnings.warn(f'instrument {instrument} not exist.', )
        d = self.newObject(
            'station.channels', name, {
                'port': {
                    'instrument': instrument,
                    'channel': channel,
                },
                'params': params
            })
        return d

    def newQubit(self, name, couplers=[], readoutLine='', **params):
        for coupler in couplers:
            try:
                c = self.getCoupler(coupler)
            except:
                c = self.newCoupler(coupler, [])
            c['qubits'].append(name)
        try:
            rl = self.getReadoutLine(readoutLine)
        except:
            rl = self.newReadoutLine(readoutLine, [])
        rl['qubits'].append(name)

        d = self.newObject(
            'chip.qubits', name, {
                'params': params,
                'couplers': couplers,
                'readoutLine': readoutLine,
                'channels': {}
            })
        return d

    def newCoupler(self, name, qubits, **params):
        for qubit in qubits:
            try:
                q = self.getQubit(qubit)
            except:
                q = self.newQubit(qubit)
            q['couplers'].append(name)
        d = self.newObject('chip.couplers', name, {
            'params': params,
            'qubits': qubits,
            'channels': {}
        })
        return d

    def newReadoutLine(self, name, qubits, **params):
        for qubit in qubits:
            try:
                q = self.getQubit(qubit)
            except:
                q = self.newQubit(qubit)
            q['readoutLine'] = name
        d = self.newObject('chip.readoutLines', name, {
            'params': params,
            'qubits': qubits,
            'channels': {}
        })
        return d

    def newGate(self, name, *qubits, type='default', **params):
        for qubit in qubits:
            try:
                self.getQubit(qubit)
            except:
                self.newQubit(qubit)
        key = ','.join(qubits)
        template = {'type': type, 'params': params}
        g = self.newObject(f'gates.{name}',
                           key,
                           template,
                           properties=('type', 'params'))
        return g

    def getObject(self, q, cls=None):
        if cls is None:
            cls = 'ConfigObject'
        return self.query(q + ':' + cls)

    def getQubit(self, name):
        return self.getObject(f"chip.qubits.{name}", cls='Qubit')

    def getCoupler(self, name):
        return self.getObject(f"chip.couplers.{name}")

    def getReadoutLine(self, name):
        return self.getObject(f"chip.readoutLines.{name}")

    def getChannel(self, name):
        return self.getObject(f"station.channels.{name}")

    def getInstrument(self, name):
        return self.getObject(f"station.instruments.{name}")

    def getGate(self, name, *qubits):
        if name not in self['gates']:
            raise KeyError(f'"{name}" gate not defined.')
        if name == 'rfUnitary':
            ret = self.getObject(f"gates.{name}.{','.join(qubits)}",
                                 cls='rfUnitary')
            ret['qubits'] = tuple(qubits)
            return ret
        elif name == 'Measure':
            ret = self.getObject(f"gates.{name}.{','.join(qubits)}",
                                 cls='Measure')
            ret['qubits'] = tuple(qubits)
            return ret
        if ('__order_senstive__' in self['gates'][name]
                and self['gates'][name]['__order_senstive__']):
            ret = self.getObject(f"gates.{name}.{','.join(qubits)}",
                                 cls='Gate')
            ret['qubits'] = tuple(qubits)
            return ret
        else:
            for qlist in permutations(qubits):
                try:
                    ret = self.getObject(f"gates.{name}.{','.join(qlist)}",
                                         cls='Gate')
                    ret['qubits'] = tuple(qlist)
                    return ret
                except:
                    pass
            else:
                raise KeyError(f'Could not find "{name}" gate for {qubits}')

    def get(self, key, default=_NO_DEFAULT):
        try:
            return self.query(key)
        except:
            if default is _NO_DEFAULT:
                raise KeyError(f'"{key}" not found.')
            else:
                return default


class ConfigObject(Trait):

    def setParams(self, **params):
        self['params'].update(params)

    def setStatus(self, **status):
        self['status'].update(status)

    def _channelDetails(self):
        if 'channels' not in self:
            return {}

        def _getChannels(dct):
            ret = {}
            for c, v in dct.items():
                if isinstance(v, str):
                    try:
                        ret[c] = self._cfg_.getChannel(v)
                    except:
                        ret[c] = v
                elif isinstance(v, dict):
                    ret[c] = _getChannels(v)
                else:
                    ret[c] = v
            return ret

        return _getChannels(self.channels)

    def _getSectionDetails(self, section, skip):
        if section not in self:
            return None

        getMethod = {
            'qubits': self._cfg_.getQubit,
            'couplers': self._cfg_.getCoupler,
            'readoutLine': self._cfg_.getReadoutLine
        }[section]

        if isinstance(self[section], str):
            return getMethod(self[section]).details(skip + (section, ))
        else:
            return {
                k: getMethod(k).details(skip + (section, ))
                for k in self[section]
            }

    def details(self, skip=('channels', 'qubits', 'couplers', 'readoutLine')):
        ret = {}
        ret.update(self)
        if 'channels' not in skip:
            ret['channels'] = self._channelDetails()
        if 'qubits' not in skip:
            ret['qubits'] = self._getSectionDetails('qubits', skip)
        if 'couplers' not in skip:
            ret['couplers'] = self._getSectionDetails('couplers', skip)
        if 'readoutLine' not in skip:
            ret['readoutLine'] = self._getSectionDetails('readoutLine', skip)
        return BaseConfig.fromdict(ret)


class Qubit(ConfigObject):

    def details(self):
        return super().details(skip=('qubits', ))


class Gate(ConfigObject):

    def details(self):
        ret = {}
        ret.update(self)
        ret['qubits'] = {
            q: self._cfg_.getQubit(q).details()
            for q in self.qubits
        }
        return BaseConfig.fromdict(ret)

    @property
    def name(self):
        return self._key_.split('.')[1]

    @property
    def qubits(self):
        return self._key_.split('.')[-1].split(',')

    def reset(self):
        qubit = self._cfg_.getQubit(self.qubits[0])
        if self.name == 'rfUnitary':
            self.setParams(frequency=qubit.params()['f01'])
        elif self.name == 'measure':
            self.setParams(frequency=qubit.params()['fr'])
        elif self.name == 'iSWAP':
            qubit2 = self._cfg_.getQubit(self.qubits[1])
            self.setParams(frequency=abs(qubit.params()['f01'] -
                                         qubit2.params()['f01']))


class rfUnitary(Gate):

    def setAmp(self, theta, amp):
        t = theta / np.pi
        dct = {k: v for k, v in zip(*self['params']['amp'])}
        dct[t] = amp
        self['params']['amp'] = [
            sorted(dct.keys()), [dct[k] for k in sorted(dct.keys())]
        ]

    def setDuration(self, theta, duration):
        t = theta / np.pi
        dct = {k: v for k, v in zip(*self['params']['duration'])}
        dct[t] = duration
        self['params']['duration'] = [
            sorted(dct.keys()), [dct[k] for k in sorted(dct.keys())]
        ]

    def setPhase(self, phi, phase):
        p = phi / np.pi
        dct = {k: v for k, v in zip(*self['params']['phase'])}
        dct[p] = phase / np.pi
        self['params']['phase'] = [
            sorted(dct.keys()), [dct[k] for k in sorted(dct.keys())]
        ]

    def amp(self, theta):
        return np.interp(theta / np.pi, *self['params']['amp'])

    def duration(self, theta):
        return np.interp(theta / np.pi, *self['params']['duration'])

    def phase(self, phi):
        return np.pi * np.interp(phi / np.pi, *self['params']['phase'])

    def reset(self):
        qubit = self._cfg_.getQubit(self.qubits[0])
        self.setParams(frequency=qubit.params.f01)
        self['params']['amp'] = [[0, 1], [self.amp(0), self.amp(np.pi)]]
        self['params']['duration'] = [[0, 1],
                                      [self.duration(0),
                                       self.duration(np.pi)]]
        self['params']['phase'] = [[-1, 1], [-1, 1]]

    def shape(self, theta, phi=0):
        return {
            'shape': self['params'].get('shape', 'Gaussian'),
            'amp': self.amp(theta),
            'duration': self.duration(theta),
            'phase': self.phase(phi),
            'frequency': self['params']['frequency'],
            'DRAGScaling': self['params'].get('DRAGScaling', 0)
        }


class Measure(Gate):

    @property
    def wfile(self) -> Path:
        return self._cfg_._path_.parent / 'Measure' / (self.qubits[0] + '.pic')

    def setW(self, w):
        self.wfile.parent.mkdir(parents=True, exist_ok=True)
        with open(self.wfile, 'wb') as f:
            pickle.dump(w, f)

    def W(self):
        with open(self.wfile, 'rb') as f:
            return pickle.load(f)


class ConfigProxy(ABC):

    @abstractmethod
    def getQubit(self, name):
        pass

    @abstractmethod
    def getCoupler(self, name):
        pass

    @abstractmethod
    def getReadoutLine(self, name):
        pass

    @abstractmethod
    def getGate(self, name, *qubits):
        pass

    @abstractmethod
    def get(self, key, default=_NO_DEFAULT):
        pass


def setConfig(path: Union[Path, str, ABCCompileConfigMixin]) -> None:
    factory = lambda path=Path(path): Config(path)
    set_config_factory(factory)


__all__ = ['Config', 'getConfig', 'setConfig']
