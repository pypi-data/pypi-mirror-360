"""
The Base Inject implements a uniform container for a list of items to be injected in to an object at runtime
"""
import KUtils.MetaProgramming.Inheritance
from KUtils.Typing import *
from abc import ABCMeta, abstractmethod
from .Common import MARKERS
from KUtils.MetaProgramming.Frame import collect_args
from enum import Enum
from . import Common as C
from KUtils.MetaProgramming import Mixins
from ...Utils import ListUtils as liu
from ..Arguments import Argpack

class _ExtractionMode(int, Enum):
    Func = 0
    Return = 1
class BaseInjectionDecorator(metaclass=ABCMeta):
    def _inject(self, target, marker: str = C.MARKERS.Injector)->None:
        setattr(target, marker, self)
    def validate(self, item)->bool:
        raise NotImplementedError('Please implement the validate method!')
    def _extract(self, item)->Any:
        m = self._config['extraction_mode']
        if m == _ExtractionMode.Func:
            return item
        elif m == _ExtractionMode.Return:
            return item()
        else:
            raise ValueError(f'Invalid exraction_mode {m}')
    def _simplify(self)->None:
        del self._config
    def __init__(self,
                 extraction_mode: Union[_ExtractionMode, int] = 0,
                 consume: bool = True,
                 min_mode: bool = False,
                 validate: bool = False,
                 ident: str = None,
                 index: int = None):
        self._config = collect_args()
        self.item = None
        self.ident = None
    def on_extraction(self)->None:
        pass
    def __call__(self, item: Any)->Callable:
        orig = item

        c = self._config
        consume = c['consume']
        min_mode = c['min_mode']
        validate = c['validate']

        item = self._extract(item)
        self.on_extraction()

        if validate:
            valid = self.validate(item)

        self.item = item

        if min_mode:
            self._simplify()

        if consume is True:
            ret = C.get_consumed_func()
        else:
            ret = orig

        self._inject(ret)
        return ret

from collections import Sequence
class BaseInjector(Mixins.Asserts, metaclass=ABCMeta,):
    Inject = BaseInjectionDecorator

    @classmethod
    def try_get_injector(cls, item)->Optional[BaseInjectionDecorator]:
        default = -1
        injector = getattr(item, MARKERS.Injector, default)

        if injector is not default and injector.__class__ is cls.Inject:
            return injector
        else:
            return None

    def __init__(self, host: Any, validate: bool=False, inherits=True):
        self.host = host
        self.injections = []
        self.validate = validate
        self.inherits = inherits

    def _append(self, item: BaseInjectionDecorator):
        assert item not in self.injections

        self.injections.append(item)
    def _collect_from_class(self, cls):
        for key, item in cls.__dict__.items():
            injector = self.try_get_injector(item)
            if None is injector:
                continue
            else:
                self._append(injector)
    def autocollect(self) ->None:
        clses = self.host.__class__
        if self.inherits:
            clses = mpc.Inheritance.inheritance_tree_flat(clses)
        else:
            clses = [clses]

        for cls in clses:
            self._collect_from_class(cls)

    def resolve(self):
        intented_indices = [inj._config['index'] for inj in self.injections]
        liu.replace_all(intented_indices, -1, len(intented_indices)-1)
        intented_indices = [el in intented_indices if math.isnan(el) else None]
        if liu.has_dup(intented_indices):
            raise NotImplementedError('Not handling duplicates right now')
        self.injections = liu.permute(self.injections, intented_indices)

        if self.validate:
            pass
    def oneshot(self) -> None:
        self.autocollect()
        self.resolve()
    def run_for_all(self, func: Callable)->None:
        for injection in self.injections:
            func(injection)
    def _call_all_packed(self, argpack: Argpack = None)->None:
        if argpack is None:
            argpack = Argpack()

        argpack.add(self.host, keyword='self')
        func = lambda x: x.item(*argpack.args, **argpack.kwargs)
        self.for_all(func)

    def call_all(self, *args, **kwargs)->None:
        self._call_all(Argpack(args, kwargs))