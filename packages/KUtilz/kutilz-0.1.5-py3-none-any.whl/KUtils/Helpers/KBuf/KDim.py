import functools

from KUtils.Typing import *
from KUtils.Utils import devu, stru, du
import numpy as np

if TYPE_CHECKING:
    from numpy import ndarray
    from torch import Tensor

class KVar:
    def __init__(self, symbol: str, initial_val: Number):
        self.symbol = symbol
        self.initial_val = initial_val

class KDim:
    def __init__(self, *args: Union[str, int]):
        self._orig_literal = args
        self._literals = []
        self._vars = {}

        for token in args:
            if isinstance(token, str):
                if ':' in token:
                    sym, initial_v = token.split(':')
                else:
                    sym = token
                    initial_v = 0
                self._literals.append(sym)
                self._vars[sym] = KVar(sym, int(initial_v))
            else:
                self._literals.append(int(token))
        self._inits = {
            k: v.initial_val for k, v in self._vars.items()
        }

    def solv(self, **kwargs) -> Tuple[int, ...]:
        vals = du.merge(self._inits, kwargs)
        return tuple(
            map(lambda v: v if isinstance(v, int) else vals[v], self._literals)
        )

    @functools.cached_property
    def default(self) -> Tuple[int, ...]:
        return self.solv()