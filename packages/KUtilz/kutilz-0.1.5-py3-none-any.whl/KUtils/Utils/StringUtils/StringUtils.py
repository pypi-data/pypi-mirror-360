from KUtils.Typing import *
import re

def parse_eq_expr(expr: str):
    pair = expr.split('=')
    return pair[0], pair[1]

def all_indices(s: str, target: str)->List[int]:
    indices = [i for i, x in enumerate(s) if x == target]
    return indices

def rm(s: str, target: str)->str:
    return s.replace(target, '') if target in s else s

def rm_all(s: str, targets: List[str])->str:
    while len(targets) > 0:
        s = rm(s, targets.pop(0))
    return s

def parse_int(s: str)->Union[int, str]:
    try:
        return int(s)
    except ValueError as e:
        return s

def parse_dom_attribs(attribs: str, delim: str = ',')->Dict[str, str]:
    res = {}
    for items in attribs.split(delim):
        pair = items.split('=')
        res[pair[0]] = pair[1]
    
    return res

def split_capital(s: str) -> List[str]:
    return re.split('(?<=.)(?=[A-Z])', s)

def strip_all_including_first_of(s: str, target: str) -> str:
    try:
        pos = s.index(target) + len(target)
        return s[pos:]
    except ValueError as e:
        return s

def camel_to_snake(s):
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()

def snake_to_camel(s):
    return "".join(x.capitalize() for x in s.lower().split("_"))