from abc import ABC
from .MixinBase import IsMixin
from KUtils.Typing import *

class Asserts(ABC):
    def _assert(self, condition: bool, msg: str = None):
        assert self.validate and condition, msg

class AssertionGetterMixin(IsMixin):
    def get_unless(self, key: str, unless_is=None)->Any:
        item = self.__dict__[key]
        if item != unless_is and item is not unless_is:
            return item
        else:
            raise KeyError(f'{key} cannot be {unless_is} in {self.__class__.__name__}')

    def cannot_be(self, item: T, unless_is=None)->T:
        if item != unless_is and item is not unless_is:
            return item
        else:
            raise KeyError(f'{item} cannot be {unless_is} in {self.__class__.__name__}')