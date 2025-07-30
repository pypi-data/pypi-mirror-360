from KUtils.Typing import *

__all__ = ['SafeContainer']

class NULL_TYPE:
    pass

class SafeContainer:

    @classmethod
    def Dict(cls):
        return cls({})

    def __init__(self, internal: object):
        self.__internal = internal
        if isinstance(internal, dict):
            self.fget = dict.get
            self.fset = dict.__setitem__
        else:
            self.fget = getattr
            self.fset = setattr

    def optional(self, key: str, default: T = None) -> T:
        item = self.fget(self.__internal, key, NULL_TYPE)
        if item is NULL_TYPE:
            return default
        else:
            return item
        
    def default(self, key: str, default: T) -> T:
        if self.optional(key, None) is None:
            self[key] = default
        return self[key]

    def required(self, key: str, type: Type[T] = None) -> T:
        try:
            item = self.fget(self.__internal, key, NULL_TYPE)
            if item is NULL_TYPE:
                raise KeyError(f'Key {key} is not found.')

        except:
            raise

        assert type is None or isinstance(item, type), f'Object {item} is not of type {type}'

        return item

    def update(self, **kwargs) -> Self:
        for key, val in kwargs.items():
            self.fset(self.__internal, key, val)
        return self

    def __getitem__(self, item):
        return self.fget(self.__internal, item)

    def __setitem__(self, key, value):
        self.fset(self.__internal, key, value)