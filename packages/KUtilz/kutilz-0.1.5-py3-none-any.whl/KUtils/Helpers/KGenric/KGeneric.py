from KUtils.Typing import *
from KUtils.Utils import devu

class KGeneric():
    __generic_var_names__: List[str] = None

    def __init_subclass__(cls, **kwargs):
        if cls.__generic_var_names__ is None:
            return

        args = devu.generic_args(cls)

        assert len(args) >= cls.__generic_var_names__

        for i, name in enumerate(cls.__generic_var_names__):
            setattr(cls, name, args[i])

