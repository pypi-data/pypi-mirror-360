from typing import Callable, TYPE_CHECKING
from typing_extensions import TypeVar, Generic, Any

T = TypeVar('T')
class simprop(property):
    @classmethod
    def wraps(cls, initializer: Callable[[Any], T]) -> T:
        return cls(initializer)
    
    def __init__(self, initializer: Callable[[Any], T]):
        self.propname = f'__kutils_{initializer.__name__}'
        self.initializer = initializer

        fset = self.make_set()
        fdel = self.make_del()
        fget = self.make_get(fset=fset)
        super().__init__(fget, fset, fdel)

    def make_get(self, fset):
        def fget(obj):
            try:
                return getattr(obj, self.propname)
            except AttributeError as e:
                fset(obj, self.initializer(obj))
            finally:
                return getattr(obj, self.propname)

        return fget

    def make_set(self):
        def fset(obj, val):
            return setattr(obj, self.propname, val)

        return fset

    def make_del(self):
        def fdel(obj):
            return delattr(obj, self.propname)
        return fdel

if TYPE_CHECKING:
    simprop = property

if __name__ == '__main__':
    class Dummy:
        @simprop
        def x(self) -> int:
            return 233

    print(getattr(Dummy(), 'x'))