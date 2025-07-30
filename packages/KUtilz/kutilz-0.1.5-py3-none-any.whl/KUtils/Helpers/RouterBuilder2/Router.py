from KUtils.Helpers.Trees import TreeNodeMixin
from KUtils.Typing import *
from KUtils import devu

class AbstractRouter(Generic[T, P], TreeNodeMixin):
    T: Type[T]

    def __init_subclass__(cls, **kwargs):
        cls.T = devu.generic_args(cls, 1)[0]


