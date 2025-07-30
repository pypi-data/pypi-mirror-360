from KUtils.Typing import *
from enum import Enum

class ToothType(str, Enum):
    INCISOR = 'incisor'
    CANINE = 'canine'
    PREMOLAR = 'pre-molar'
    MOLAR = 'molar'

    @classmethod
    def FromFDI(cls, fdi: int):
        tid = int(fdi)
        a, b = tid // 10, tid % 10
        if b in [1, 2]:
            k = ToothType.INCISOR
        elif b in [3]:
            k = ToothType.CANINE
        elif b in [4, 5]:
            k = ToothType.PREMOLAR
        elif b in [6, 7, 8]:
            k = ToothType.MOLAR
        else:
            raise ValueError(f'Invalid FDI designation: {tid}')
        return k

def _teeth_upto(qudrant: int, upto: int)->List[int]:
    return [qudrant*10 + tooth_num for tooth_num in range(1, upto+1)]

def get_all(permanent=True,
            deciduous=False,
            supernumerary=False,
            dtype: Type[T] = int)->List[T]:
    fdis = []
    if permanent:
        for quadrant in range(1, 4 + 1):
            fdis.extend(_teeth_upto(quadrant, 8))

    if deciduous:
        for quadrant in range(5, 8 + 1):
            fdis.extend(_teeth_upto(quadrant, 5))

    fdis = [dtype(i) for i in fdis]

    return fdis

def is_legal(fdi: int):
    if not 10 < fdi < 100:
        return False
    else:
        quad = fdi // 10
        num = fdi % 10
        
        return 0 < quad < 9 and 0 < num < 9

def opposite_quadrant(fdi: int) -> int:
    candidates = [
        set([1, 4]),
        set([2, 3]),
        set([5, 8]),
        set([6, 7])
    ]
    
    if fdi < 10:
        quadrant = fdi
    else:
        quadrant = fdi // 10
    
    for c in candidates:
        if quadrant in c:
            pair = c
            break
    else:
        raise ValueError(f'Bad FDI value {fdi} with quadrant {quadrant}')
    
    for el in pair:
        if quadrant != el:
            return el
    
    raise RuntimeError(f'This shouldnt happen!')

def all_fdis_in_quadrant(quadrant: int) -> List[int]:
    res = []
    for i in range(1, 9):
        res.append(quadrant * 10 + i)
    
    return res
        