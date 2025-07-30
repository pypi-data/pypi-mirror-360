import functools
from KUtils.Typing import *
from KUtils.Utils.DevUtils.BasePropertyWrapper import BaseProperptyWrapper

class accessor(BaseProperptyWrapper):
    @classmethod
    def ondict(cls,
               target: str,
               key: str = None
               ) -> Type[property]:
        return functools.partial(cls, target=target, key=key)

    @classmethod
    def inits(cls, const: bool = False) -> Type[property]:
        return functools.partial(cls, key_maker = lambda s: '__' + s, readonly = const)

    # if TYPE_CHECKING:
    #     ondict = property
    #     inits = property

    def __init__(self,
                 initializer: Callable[[Any], T],
                 target: str = None,
                 key: str = None,
                 key_maker: Callable[[str], str] = lambda s: s,
                 readonly: bool = False,
                 default: T = None,
                 on_dict: bool = False):

        if on_dict:
            assert target is not None
            key = key or key_maker(initializer.__name__)



            def get_field(slf, key):
                keys: list = key.split('.')
                item = slf
                while len(keys) != 0:
                    key = keys.pop(0)
                    item = getattr(item, key)

                return item

            if not readonly:
                fset = lambda slf, item: (get_field(slf, target).__setitem__(key, item))
            else:
                fset = lambda slf, item: eval('raise ValueError(f\'Property {key} is readonly!\')')
            fdel = lambda slf: get_field(slf, target).__delitem__(key)
            fget = lambda slf: get_field(slf, target).get(key, default)
        else:
            real_key = key_maker(key or initializer.__name__)
            if not readonly:
                fset = lambda slf, item: setattr(slf, real_key, item)
            else:
                fset = lambda slf, item: eval('raise ValueError(f\'Property {key} is readonly!\')')
            fdel = lambda slf: delattr(slf, real_key)

            def fget(slf):
                res = getattr(slf, real_key, None)
                if res is None:
                    res = initializer(slf)
                    if not readonly:
                        fset(slf, res)
                    else:
                        setattr(slf, real_key, res)
                return res
        super().__init__(fget, fset, fdel)

    def setter(self, trsfmer):
        return property(
            self.fget,
            lambda slf, val: self.fset(slf, trsfmer(slf, val)),
            self.fdel
        )

    def getter(self, __fget):
        return property(
            functools.update_wrapper(__fget, self.get),
            self.fset,
            self.fdel
        )

    def deleter(self, __fdel):
        return property(
            self.fget,
            self.fset,
            functools.update_wrapper(__fdel, self.fdel),
        )

if TYPE_CHECKING:
    accessor = property

if __name__ == '__main__':
    class Dumpy:
        @accessor.ondict('dummy')
        def fucker(self) -> str: ...

        def __init__(self):
            self.dummy = {}


    dd = Dumpy()
    dd.fucker = 'shit'
    print(dd.fucker)

    print(dd.dummy)
    del dd.fucker
    print(dd.dummy)