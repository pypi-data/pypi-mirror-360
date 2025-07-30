from KUtils.Typing import *

from ._Mapping import _Mapping

class ContinuousToDiscreteMapping(_Mapping):
    def __init__(self, discrete_set: List[int]):
        x = range(0, len(discrete_set))
        super().__init__(x, discrete_set)

    def resolve_mapper(self) ->Callable[[int], int]:
        return lambda x: self.y[x]

    def resolve_inverter(self) ->Callable[[int], int]:
        return lambda y: self.y.index(y)

    def to_dict(self,
                apply_on_x: Callable[[int], any]=None,
                apply_on_y: Callable[[int], any]=None):

        return dict(
            zip(
                [x if apply_on_x is None else apply_on_x(x) for x in self.x],
                [y if apply_on_y is None else apply_on_y(y) for y in self.y]
            )
        )

    def __len__(self):
        return self.x.__len__()