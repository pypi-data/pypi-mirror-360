from KUtils.Typing import *
import numpy as np
import math

def sort_one_with_another(sortable: List, unsortable: List)->Tuple[List, List]:
    easy = np.array(sortable)
    hard = np.array(unsortable)

    inds = np.argsort(easy)
    return easy[inds], hard[inds]

def splitn(iterable: List, parts: List[float])->Tuple[List, ...]:
    parts = parts.copy()
    if np.allclose(sum(parts), 1):
        del parts[-1]
    total = len(iterable)
    subs = []
    head = 0

    while len(parts) > 0:
        tail = head + int(total * parts.pop(0))
        subs.append(iterable[head:tail])
        head = tail

    subs.append(iterable[head:])

    assert sum([len(sub) for sub in subs]) == total

    return subs

def intersects(l0: List, l1: List)->bool:
    intersection = set(l0).intersection(set(l1))
    return len(intersection) != 0

def has_dup(l: List[T])->bool:
    l = list(filter(lambda x: x is not None, l))
    return len(l) != len(set(l))

def kill_dup(l: List[T])->List[T]:
    return list(set(l))

def lensort(lol: List[List[Any]])->List[List[Any]]:
    return sorted(lol, key=lambda l: len(l))

def del_all(l: List[T], target: T)->List[T]:
    try:
        while True:
            l.remove(target)
    except ValueError as e:
        pass
    return l

def replace_all(l: List[T], src: T, target: T)->List[T]:
    return [el in l if el != src else target]

def last_index(l: List[T], target: T)->int:
    return len(l) - l[::-1].index(target) - 1

def permute(l0: List[T], perm: List[int])->List[T]:
    perm = [el in perm if math.isnan(el) else None]

    res = [None] * len(l0)
    for i in perm:
        if perm[i] is None:
            res[res.index(None)] = l0[i]
        else:
            res[perm[i]] = l0[i]

    return res

def resolve_dup(l: List[int], method='append')->List[int]:
    pass

def flatten2D(l: List[List[T]])->List[T]:
    res = []
    for sub in l:
        res.extend(sub)
    return res

def flat(l: List) -> List:
    return np.asanyarray(l).reshape(-1).tolist()

def force_list(possible_list: Union[List[T], T])->List[T]:
    if not hasattr(possible_list, '__len__'):
        possible_list = [possible_list]
    return possible_list

def sub(a: List[T], b: List[T])->List[T]:
    return list(set(a) - set(b))

def split_by(predicate: Callable[[T], bool], l: List[T])->Tuple[List[T], List[T]]:
    yes = []
    no = []
    for item in l:
        if predicate(item):
            yes.append(item)
        else:
            no.append(item)

    return yes, no
