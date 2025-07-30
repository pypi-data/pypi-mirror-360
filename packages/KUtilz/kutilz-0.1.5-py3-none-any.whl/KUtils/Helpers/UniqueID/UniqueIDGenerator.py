import types

from KUtils.Typing import *
from .UniqueIDMixin import UniqueIDMixin

class UniqueIDGenerator(ABC):
    @abstractmethod
    def new(self): ...

    @abstractmethod
    def rmv(self, x: str): ...

    def __init__(self, name: str):
        self.name = name
        self.__MIXIN = None

    def Mixin(self) -> Type[UniqueIDMixin]:
        if self.__MIXIN is None:
            self.__MIXIN = type(
                self.name + '_MIXIN',
                (UniqueIDMixin, ),
                {}
            )
            self.__MIXIN._UniqueIDMixin__id_generator = self
        return self.__MIXIN

class SimpleUniqueIDGenerator(UniqueIDGenerator):
    def __init__(self, name: str, max: int = 9999999999999):
        super().__init__(name)
        self.counter = 0
        self.recycled = set()

    def new(self):
        if self.recycled:
            return self.recycled.pop()
        else:
            return self.counter + 1

    def rmv(self, x: str):
        self.recycled.add(x)