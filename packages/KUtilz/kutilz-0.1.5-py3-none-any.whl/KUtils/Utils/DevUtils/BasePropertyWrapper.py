from typing import Callable
from typing_extensions import TypeVar, Generic, Any

T = TypeVar('T')

class BaseProperptyWrapper(property):
    @classmethod
    def wraps(cls, initializer: Callable[[Any], T]) -> T:
        return cls(initializer)
