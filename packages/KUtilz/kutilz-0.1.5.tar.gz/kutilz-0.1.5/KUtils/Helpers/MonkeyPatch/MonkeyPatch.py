from KUtils.Typing import *
from KUtils.Utils import DevUtils as devu

class MonkeyPatch(Generic[T]):
    __TARGET__: Type[T] = None

    def __init_subclass__(cls, **kwargs):
        cls.__TARGET__ = devu.generic_args(cls, 1)[0]
        for name, value in cls.__dict__.items():
            if not name.startswith('__') and not name.endswith('__'):
                # Set the attribute on the target class, overwriting if exists
                setattr(cls.__TARGET__, name, value)