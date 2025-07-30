from KUtils.Typing import *

class SomeSetupMixin(Generic[T]):
    _some = None

    def setup_some(self)->T:
        raise NotImplementedError(f'You need to implement setup_some in {self.__class__.__name__}')

    @property
    def some(self)->T:
        if self._some is None:
            self._some = self.setup_some()
        return self._some