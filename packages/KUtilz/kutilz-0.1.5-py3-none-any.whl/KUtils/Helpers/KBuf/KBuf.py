from KUtils.Typing import *
from KUtils.Utils import DevUtils as devu
import numpy as np
from .KDim import KDim
if TYPE_CHECKING:
    from numpy import ndarray
    from torch import Tensor

T_DType = TypeVar('T_DType')
T_Shape = TypeVar('T_Shape')


class KBuf(Generic[T_DType, T_Shape]):
    __datatype__ = None
    __shape_constraint__: KDim = None

    def __init_subclass__(cls, **kwargs):
        cls.__datatype__, _constraint = devu.generic_args(cls, 2)

        if not isinstance(_constraint, KDim):
            raise TypeError(f'Invalid shape constraint {_constraint}')

        cls.__shape_constraint__ = _constraint

    @property
    def shape(self) -> Tuple[int, ...]:
        return self.buf.shape

    @property
    def buf(self) -> np.ndarray:
        return self._data

    @buf.setter
    def buf(self, data: Union[np.ndarray, list, 'Tensor']) -> None:
        _data = np.array(data, dtype=self.__datatype__)
        if self.__shape_constraint__ is not None:
            _data = np.reshape(_data, self.__shape_constraint__.solv(**self.vars))
        self._data = _data

    @property
    def vars(self) -> Dict[str, Number]:
        _val = getattr(self, '__vars', None)
        if _val is None:
            _val = {}
            setattr(self, '__vars', _val)
        return _val

    def copy(self) -> Self:
        return type(self)(self.buf.copy())

    def __init__(self, data: Union[np.ndarray, list, 'Tensor', None]):
        self.buf = np.array(data)

    def __getitem__(self, item) -> np.ndarray:
        return self.buf[item]

    def __array__(self, dtype: str = None, copy: bool = None):
        new = self._data
        if dtype != self._data.dtype:
            new = new.astype(dtype)

        if copy is True:
            raise NotImplementedError()

        return new

    def __repr__(self):
        return f'Buffer@[shape={self.shape}][type={self.__datatype__}]'

    def __sub__(self, other):
        return self.__class__(self.buf - other)

    def __add__(self, other):
        return self.__class__(self.buf + other)

    def __truediv__(self, other):
        return self.__class__(self.buf / other)

    def __mul__(self, other):
        return self.__class__(self.buf * other)

# if TYPE_CHECKING:
#     KBuf = KBuf