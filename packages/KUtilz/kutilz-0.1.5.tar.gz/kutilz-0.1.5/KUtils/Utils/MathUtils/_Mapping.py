from ..ListUtils import ListUtils as liu
from KUtils.Typing import *

class _Mapping:
    def __init__(self, x=List[Any], y=List[Any], mapper:Callable[[Any], Any]=None):
        self.x = x
        self.y = y
        if mapper is None:
            self.mapper = self.resolve_mapper()

        self.inverter = self.resolve_inverter()

    def resolve_mapper(self)->Callable[[Any], Any]:
        pass

    def resolve_inverter(self)->Callable[[Any], Any]:
        pass

    def get(self, x: Any)->Any:
        return self.mapper(x)

    def revert(self, y: Any)->Any:
        return self.inverter(y)