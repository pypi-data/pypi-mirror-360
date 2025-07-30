from KUtils.Typing import *

class Namespace(Generic[T]):
    # __T__: Type[T] = None
    #
    # def __init_subclass__(cls, **kwargs):

    def __init__(self, v: Any = None):
        self.__v = v
        self.__d: Dict[str, Namespace[T]] = {}

    def __set(self, key, val):
        self.__d[key] = val

    def __get(self, key):
        v = self.__d.get(key, None)
        if not v:
            v = Namespace()
            self.__set(key, v)

        return v

    def __setitem__(self, key, value):
        if isinstance(value, Namespace):
            self.__set(key, val)
        else:
            namespace = self.__get(key)
            namespace.__v = value

    def __getitem__(self, item) -> 'Namespace[T]':
        return self.__get(item)

    @property
    def val(self) -> Optional[T]:
        return self.__v

