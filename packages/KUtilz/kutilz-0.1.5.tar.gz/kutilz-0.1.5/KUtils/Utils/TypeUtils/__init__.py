from KUtils.Typing import *

def is_same(a: Any, b: Any)->bool:
    return type(a) is type(b)

def is_of(a: Any, b: List[Any])->bool:
    for item in b:
        if is_same(a, item): return True

    return False
