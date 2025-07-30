import functools
from KUtils.Typing import *


def _priv_name(cls: type, var_name: str) -> str:
    return f'_{cls.__name__}__{var_name}'


class BaseMixin:
    __mixin_initters__: List[Callable] = None

    def __mixinit(self) -> None:
        raise NotImplementedError()

    def __init_subclass__(cls, **kwargs):
        initters = []

        mixins = cls.all_mixins()
        for mixin in mixins:
            initter = getattr(mixin, _priv_name(mixin, 'mixinit'), None)
            if initter is not None:
                initters.append(initter)

        cls.__mixin_initters__ = initters
        cls.__wrap_init()

    @classmethod
    def __wrap_init(cls) -> None:
        if cls.is_mixin():
            init_name = _priv_name(cls, 'mixinit')

            orig_init = getattr(cls, init_name)

            @functools.wraps(orig_init)
            def init_parent_mixins(self, *args, **kwargs):
                # print('parent mixin called')
                for mixinit in cls.__mixin_initters__:
                    mixinit(self)
                orig_init(self)

            setattr(cls, init_name, init_parent_mixins)
        else:
            orig_init = cls.__init__

            @functools.wraps(orig_init)
            def init_all_mixins(self, *args, **kwargs):
                orig_init(self, *args, **kwargs)
                for mixinit in cls.__mixin_initters__:
                    mixinit(self)

            cls.__init__ = init_all_mixins

    @classmethod
    def is_mixin(cls) -> bool:
        return 'Mixin' in cls.__name__ and cls is not BaseMixin

    @classmethod
    def all_mixins(cls) -> List[Type[Self]]:
        mixins = []
        for base in cls.__bases__:
            if base is cls:
                continue
            if issubclass(base, BaseMixin) and base.is_mixin():
                mixins.append(base)

        # assert not liu.has_dup(mixins)
        return mixins

    def require(self, key: str, val_type: Type[T]) -> T:
        val = getattr(self, key)
        # assert type(val) is val_type
        return val


if __name__ == '__main__':
    class HelloWorldMixin(BaseMixin):
        def __mixinit(self) -> None:
            print('hello world')


    class FuckTheWorldMixin(BaseMixin):
        def __mixinit(self) -> None:
            print('fuck you world')


    class FuckTheWorldTwiceMixin(FuckTheWorldMixin):
        def __mixinit(self) -> None:
            print('fuck you again world')


    class SampleBase(HelloWorldMixin):
        def __init__(self):
            pass


    class Sample2Base(SampleBase, FuckTheWorldTwiceMixin):
        def __init__(self):
            super().__init__()


    sp = Sample2Base()
    pass
