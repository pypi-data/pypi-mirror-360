import dataclasses

from KUtils.Typing import *

_Self = TypeVar('_Self')

@dataclasses.dataclass
class KProperty(Generic[_Self, T]):
    realkey: str
    fget: Callable[[_Self], T]
    fset: Callable[[_Self, T], None]
    fdel: Callable[[_Self], None]

    def __get__(self, instance, owner) -> T:
        return self.fget(instance)

    def __set__(self, instance, value):
        self.fset(instance, value)

    def __delete__(self, instance):
        self.fdel(instance)


_PROP_DECORATOR = Callable[[Callable[[_Self], T]], KProperty[_Self, T]]

class prop:
    @staticmethod
    def cached(key: str) -> _PROP_DECORATOR:
        def wrap(fn):
            return KProperty(
                key, fn, None, None
            )
        return wrap