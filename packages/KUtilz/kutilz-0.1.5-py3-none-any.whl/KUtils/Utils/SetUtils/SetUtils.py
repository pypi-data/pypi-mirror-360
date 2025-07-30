from KUtils.Typing import *
def union(sets: List[Set[T]])->Set[T]:
    all = set()
    for one in sets:
        all = all.union(one)

    return all

def notin(a: Set[T], b: Set[T]) -> Set[T]:
    return set((item for item in a if item not in b))

def intersection(sets: List[Set[T]])->Set[T]:
    inter = sets[0]
    for one in sets[1:]:
        inter &= one

    return inter