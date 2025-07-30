from collections import defaultdict

import numpy as np

from ..tools.geo import EPS, point_in_polygon


def count_state(state):
    ret = defaultdict(lambda: 0)
    for s in state:
        ret[tuple(s)] += 1
    return dict(ret)


def count_to_diag(count, shape=None):
    state = list(count.keys())
    if shape is None:
        shape = (2, ) * len(state[0])
    n = np.asarray(list(count.values()))
    p = n / np.sum(n)
    state = np.ravel_multi_index(np.asarray(state).T, shape)
    ret = np.zeros(shape).reshape(-1)
    ret[state] = p
    return ret


def _atleast_type(a, dtype):
    if dtype == np.double and a.dtype.type == np.int8:
        return a.astype(np.double)
    elif dtype == complex and a.dtype.type in [np.int8, np.double]:
        return a.astype(complex)
    else:
        return a


__classify_methods = {}


def install_classify_method(method: str, func: callable):
    __classify_methods[method] = func


def uninstall_classify_method(method: str):
    if method in __classify_methods:
        del __classify_methods[method]


def classify(data, method, params):
    if method in __classify_methods:
        return __classify_methods[method](data, params)
    else:
        raise ValueError("method not found")


def default_classify(data, params):
    """
    默认的分类方法
    """
    thr = params.get('threshold', 0)
    phi = params.get('phi', 0)
    return 1 + ((data * np.exp(-1j * phi)).real > thr)


def classify_svm(data, params):
    """
    分类方法：SVM
    """
    raise NotImplementedError
    from sklearn import svm

    clf = svm.SVC(kernel='rbf',
                  gamma=params.get('gamma', 1),
                  C=params.get('C', 1))
    clf.fit(data, data)
    return clf.predict(data)


def classify_kmeans(data, params):
    """
    分类方法：KMeans
    """
    from sklearn.cluster import KMeans

    centers = params.get('centers', None)
    if isinstance(centers, list):
        centers = np.asarray(centers)

    k = params.get('k', None)
    if k is None and centers is not None:
        k = np.asarray(centers).shape[0]
    cur_shape = data.shape

    flatten_init = np.array([np.real(centers), np.imag(centers)]).T

    flatten_data = data.flatten()
    ret_ans = KMeans(n_clusters=k, init=flatten_init).fit_predict(
        np.array([np.real(flatten_data),
                  np.imag(flatten_data)]).T)
    return 2**ret_ans.reshape(cur_shape)


def classify_nearest(data, params):
    """
    分类方法：最近邻
    """
    centers = params.get('centers', None)
    if centers is None:
        raise ValueError("centers not found")
    return 2**np.argmin([np.abs(data - c) for c in centers], axis=0)


def classify_range(data, params):
    """
    分类方法：范围
    """
    centers = params.get('centers', None)
    radians = params.get('radians', None)
    if centers is None:
        raise ValueError("centers not found")
    if radians is None:
        return 2**np.argmin([np.abs(data - c) for c in centers], axis=0)

    ret = np.full_like(data, 0, dtype=int)
    for i, (c, r) in enumerate(zip(centers, radians)):
        ret[np.abs(data - c) <= r] += 2**i
    return ret


def classify_polygon(data, params):
    """
    分类方法: 多边形内
    """
    polygons = params.get('polygons', None)
    eps = params.get('eps', EPS)
    if polygons is None:
        raise ValueError("polygons not found")

    ret = np.full_like(data, 0, dtype=int)
    for i, polygon in enumerate(polygons):
        ret[point_in_polygon(data, polygon, eps)] += 2**i
    return ret


install_classify_method("state", default_classify)
install_classify_method("nearest", classify_nearest)
install_classify_method("range", classify_range)
install_classify_method("kmeans", classify_kmeans)
install_classify_method("polygon", classify_polygon)


def classify_data(data, measure_gates, avg=False):
    assert data.shape[-1] == len(
        measure_gates), 'number of qubits must equal to the size of last axis'

    ret = np.zeros_like(data, dtype=np.int8)

    for i, g in enumerate(measure_gates):
        signal = g['params'].get('signal', 'state')

        if signal in __classify_methods:
            ret[..., i] = classify(data[..., i], signal, g['params'])
        elif signal == 'amp':
            phi = g['params'].get('phi', 0)
            ret = _atleast_type(ret, np.double)
            ret[..., i] = (data[..., i] * np.exp(-1j * phi)).real
        if signal == 'raw':
            ret = _atleast_type(ret, complex)
            ret[..., i] = data[..., i]
        elif signal == 'real':
            ret = _atleast_type(ret, np.double)
            ret[..., i] = data[..., i].real
        elif signal == 'imag':
            ret = _atleast_type(ret, np.double)
            ret[..., i] = data[..., i].imag
        elif signal == 'abs':
            ret = _atleast_type(ret, np.double)
            ret[..., i] = np.abs(data[..., i])
        else:
            pass
    if avg:
        ret = ret.mean(axis=-2)
    return ret
