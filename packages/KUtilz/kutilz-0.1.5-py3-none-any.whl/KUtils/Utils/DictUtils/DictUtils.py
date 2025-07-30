from __future__ import annotations
from typing import List, Any, TypeVar, Dict, Callable, Iterable, Optional, Set

V = TypeVar('V')
K = TypeVar('K')
T = TypeVar('T')

def recursive_mut(
            d: Dict[K, Any],
            mutter: Callable[[K, Any], Any],
            predicate: Callable[[Any], bool] = None,
            prefix: str = None) -> None:
    for key, val in d.items():
        if prefix is None:
            _prefix = key
        else:
            _prefix = prefix + ':' + key

        if isinstance(val, dict):
            recursive_mut(val, mutter, predicate, prefix=_prefix)
        elif (predicate is None) or (predicate(val)):
            d[key] = mutter(_prefix, val)

def make_dicts(keys: List[str], vals: List[List[Any]])->dict:
    assert all([len(keys) == len(sub_vals) for sub_vals in vals])
    
    res = []
    for sub_val in vals:
        new_item = {}
        for i, key in enumerate(keys):
            new_item[key] = sub_val[i]

        res.append(new_item)
    return res

def merge(dict0: dict, dict1: dict)->dict:
    interm = dict0.copy()
    interm.update(dict1)
    return interm

def set_chained(dict: dict, keys: List[str], val: Any)->None:
    next = dict
    for key in keys[:-1]:
        if not key in next:
            next[key] = {}

        next = next[key]

    next[keys[-1]] = val

def get_chained(dict: dict, keys: List[str])->Any:
    next = dict
    for key in keys[:-1]:
        next = next[key]

    return next.get(keys[-1])

def auto_dict(*args)->dict:
    return dict({arg:eval(arg) for arg in args})

def vmap(d: Dict[K, V], func: Callable[[V], T])-> Dict[K, T]:
    return {
        key: func(val) for key, val in d.items()
    }

def kmap(d: Dict[K, V], func: Callable[[K], T])-> Dict[T, V]:
    return {
        func(key): val for key, val in d.items()
    }

def notin(a: dict, b: dict | Set[str])->dict:
    return {
        key: val for key, val in a.items() if key not in b
    }

def select(d: dict, keys: Iterable[Any]) -> dict:
    return {
        key: d[key] for key in keys
    }

def find_key_by_val(d: Dict[K, V], v: V) -> Optional[K]:
    for key, val in d.items():
        if val == v:
            return key

    return None

def vfilt(d: Dict[K, V], predicate: Callable[[V], bool]) -> Dict[K, V]:
    return {
        key: val for key, val in d.items() if predicate(val)
    }

def invert(d: Dict[K, V], collect: bool = False) -> Dict[V, K]:
    if not collect:
        return {
            v: k for k, v in d.items()
        }
    else:
        keys = set(d.values())
        res = {key: [] for key in keys}
        for k, v in d.items():
            res[v].append(k)
        return res

def unest(d: Dict[str, Any], delim: str = ':', prefix: str = '') -> Dict[str, Any]:
    result = {}
    for k, v in d.items():
        _k = prefix + k
        if isinstance(v, dict):
            result.update(unest(v, delim, _k + delim))
        else:
            result[_k] = v

    return result

def group(fn: Callable[[V], K], items: Iterable[V]) -> Dict[K, List[V]]:
    d = {}
    for item in items:
        category = fn(item)
        d.setdefault(category, [])
        d[category].append(item)
    return d

def arggroup(fn: Callable[[V], K], items: Iterable[V]) -> Dict[K, List[int]]:
    d = {}
    for i, item in enumerate(items):
        category = fn(item)
        d.setdefault(category, [])
        d[category].append(i)
    return d