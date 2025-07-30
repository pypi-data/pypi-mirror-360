def protected():
    pass

### KUtils CodeWriter Injection Point Starts
class ContextSetupMixin(Generic[T]):
    _context = None

    def setup_context(self)->T:
        raise NotImplementedError(f'You need to implement setup_context in {self.__class__.__name__}')

    @property
    def context(self)->T:
        if self._context is None:
            self._context = self.setup_context()
        return self._context

class ControllerSetupMixin(Generic[T]):
    _controller = None

    def setup_controller(self)->T:
        raise NotImplementedError(f'You need to implement setup_controller in {self.__class__.__name__}')

    @property
    def controller(self)->T:
        if self._controller is None:
            self._controller = self.setup_controller()
        return self._controller

### KUtils CodeWriter Injection Point Ends