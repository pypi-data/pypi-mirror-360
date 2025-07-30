from typing import TypeVar, Generic
from typing_extensions import Self

L = TypeVar('L')


class LayerMask(int, Generic[L]):
    def accepts(self, other: int) -> bool:
        return self & other != 0


class LayerManager:
    @classmethod
    def create(cls, *args) -> LayerMask[Self]:
        raise NotImplementedError()

    @classmethod
    def none(cls) -> LayerMask[Self]:
        return cls.create()

    @classmethod
    def all(cls) -> LayerMask[Self]:
        return LayerMask(1111111111111)


