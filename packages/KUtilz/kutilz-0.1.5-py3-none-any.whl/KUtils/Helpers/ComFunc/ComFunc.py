from KUtils.Typing import *

DerivedP = ParamSpec('DerivedP')
DerivedR = TypeVar('DerivedR')

class SanityCheckFailed(Exception): pass

class ComFunc(Generic[DerivedP, DerivedR]):
    Instance: Self
    
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.Instance = cls()
    
    @classmethod
    def __invertfunc__(cls, ret: DerivedR) -> DerivedR:
        raise NotImplementedError()

    def apply(self, *args: DerivedP.args, **kwargs: DerivedP.kwargs) -> DerivedR:
        raise NotImplementedError(f'{self.__class__.__name__} needs to implement the apply method!!')

    def __call__(self, *args: DerivedP.args, **kwargs: DerivedP.kwargs) -> DerivedR:
        return self.apply(*args, **kwargs)

    def __invert__(self) -> Self:
        assert hasattr(self.__class__, '__invertfunc__')
        orig_apply = self.apply
        self.apply = lambda *args, **kwargs: self.__class__.__invertfunc__(orig_apply(*args, **kwargs))
        return self
        
    def sanity_check(self, *args: DerivedP.args, **kwargs: DerivedP.kwargs) -> DerivedR:
        try:
            res = self.__call__(*args, **kwargs)
        except Exception as e:
            raise SanityCheckFailed(e)
        return res
    
def BuildComFunc(template: Callable[DerivedP, DerivedR]) -> Type[ComFunc[DerivedP, DerivedR]]:
    return ComFunc

