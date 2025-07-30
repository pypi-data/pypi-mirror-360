import abc

from KUtils.Typing import *

class IsMixin(metaclass=abc.ABCMeta):
    def safe_getattr(self, key: str)->Any:
        #todo: implement it
        #safe get attr method that skips __getatrribute__ implementation
        return getattr(self, key, None)