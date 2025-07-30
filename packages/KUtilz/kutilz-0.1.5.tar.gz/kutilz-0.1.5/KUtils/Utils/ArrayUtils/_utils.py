from __future__ import annotations
import numpy as np
from KUtils.Typing import *

ArrayLike = Union[List, np.ndarray]

def flattend(array: ArrayLike) -> List:
    return np.array(array).reshape(-1).tolist()

def rmv_dup(array: ArrayLike) -> List:
    array = np.array(array)
    _, idx = np.unique(array, return_index=True)
    return array[np.sort(idx)].tolist()

def all_equal(array: ArrayLike) -> List:
    return len(set(array)) == 1

def split(arr: T, portions: Tuple[float, ...] | List[float] | float) -> Tuple[T, ...]:
    _type = type(arr)

    if isinstance(portions, float):
        portions = [portions]
    else:
        portions = [float(portion) for portion in portions]

    cnt = len(arr)
    _sum = sum(portions)

    if not np.isclose(_sum, 1):
        portions.append(1 - _sum)

    indices_pairs = []

    start = 0

    cuts = []

    for i in range(len(portions)):
        if i != len(portions) - 1:
            diff = int(cnt * portions[i])
            next = start + diff
        else:
            next = cnt

        cuts.append(arr[start:next])
        start = next

    assert sum([len(cut) for cut in cuts]) == cnt, f'You fucked up'

    return tuple(cuts)

def cutoff_split(arr: Iterable[T], cutoffs: List[Number], key: Callable[[T], Number] = lambda x: x) -> Dict[Number, List[T]]:
    cutoffs = sorted(cutoffs, reverse=True)
    result = {cutoff: [] for cutoff in cutoffs}

    for el in arr:
        for cutoff in cutoffs:
            if key(el) > cutoff:
                result[cutoff].append(el)
                break

    return result
