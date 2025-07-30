from KUtils.MetaProgramming.Injector.BaseInjector import *

class HooksInjectionDecorator(BaseInjectionDecorator):
    def validate(self, item) ->bool:
        return '__call__' in item

class HooksInjector(BaseInjector):
    Inject = HooksInjectionDecorator
    def __call__(self, *args, **kwargs):
        self.call_all(*args, **kwargs)
