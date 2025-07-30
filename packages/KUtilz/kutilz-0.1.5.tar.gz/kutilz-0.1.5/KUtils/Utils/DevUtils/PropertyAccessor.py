from KUtils.Typing import *

class PropertyAccessor(Generic[T], ABC):
    path: List[str]
    type: Type

    def __init__(self, path: Union[str, List[str]], type: Type = Any):
        self.path = path.split('.') if isinstance(path, str) else path
        self.type = type

    def _getobject(self, target: object) -> object:
        for p in path:
            target = getattr(target, p)
        return target

    def _setobject(self, target: object, val: object) -> object:
        for p in path[:-1]:
            target = getattr(target, p)
        setattr(target, path[-1], val)

    @abstractmethod
    def fget(self, target: object, *args) -> T: ...

    @abstractmethod
    def fset(self, target: object, val: T, *args) -> None: ...

class DictAccessor(PropertyAccessor[T]):
    def fget(self, target: object, key: str, *args) -> T:
        return self._getobject(target)[key]

    def fset(self, target: object, key: str, val: T, *args) -> None:
        self._getobject(target)[key] = val

class DirectAccessor(PropertyAccessor[T]):
    fget = PropertyAccessor._getobject
    fset = PropertyAccessor._setobject