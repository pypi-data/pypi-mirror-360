from .simprop import *

class ReadOnlyError(Exception): pass

class readonly(simprop):
    def __init__(self, initializer):
        super().__init__(initializer)
        self.__readonly = False

    def make_set(self) -> property:
        def fset(obj, value):
            if not self.__readonly:
                setattr(obj, self.propname, value)
            else:
                raise ReadOnlyError()

        return fset


if __name__ == '__main__':
    class Dummy:
        @simprop
        def x(self) -> int: pass


    dummy = Dummy()
    dummy.x = 2
    print(getattr(dummy, 'x'))
