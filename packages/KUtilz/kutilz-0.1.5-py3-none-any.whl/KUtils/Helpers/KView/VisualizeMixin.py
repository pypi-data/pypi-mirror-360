import copy
import dataclasses

import numpy as np
from KUtils.Typing import *
from KUtils import DataClass

from KUtils.Typing import *
from PIL.ImageColor import getrgb
from KUtils import KBuf, KDim

class ColorParsingError(Exception):
    pass

class Color(KBuf[np.uint8, KDim('C:-1')]):
    def __init__(self, *args):
        if len(args) == 1 and not isinstance(args[0], (list, tuple, np.ndarray)):
            try:
                val = getrgb(args[0])
            except Exception as e:
                raise ColorParsingError(e)
        else:
            val = np.array(args)

        super().__init__(val)

    def rgba(self, alpha = 255):
        return np.array([
            *self[:3], alpha
        ])

    @property
    def opencv(self):
        return tuple(self.buf.astype(int).tolist())

    @classmethod
    def Grey(cls) -> Self:
        return Color(122, 122, 122)

    @classmethod
    def Black(cls) -> Self:
        return Color(0, 0, 0)

    def __repr__(self):
        return f'Color@{self.buf}'


class TextParams(TypedDict):
    content: NotRequired[str]
    color: NotRequired[Color]
    align: NotRequired[Literal['bm', 'tm']]
    bgrd: NotRequired[Literal['box', 'none']]


@dataclasses.dataclass
class VisParams:
    name: Optional[str] = ''
    name_color: Optional[Color] = Color.Grey()

    color: Optional[Color] = Color.Grey()
    border_color: Optional[Color] = Color.Black()
    thickness: Optional[float] = None
    matrix: Optional[np.ndarray] = None
    fill: Optional[Color] = None
    texts: Optional[List[TextParams]] = None
    radius: Optional[float] = None

    instances: Optional[List[Self]] = None

    def __post_init__(self):
        self.texts = self.texts or []

    @property
    def is_dupped(self) -> bool:
        return self.instances is not None

    def overwrite(self, other: Self):
        for key, value in dataclasses.asdict(other).items():
            setattr(self, key, value)

class VisParamsMixin:
    def visualized(self, **kwargs: Unpack[VisParams.__init__]):
        if 'color' in kwargs:
            kwargs['color'] = Color(kwargs['color'])
        self.vparams.overwrite(VisParams(**kwargs))
        return self

    def vis_with(self, key: Union[VisParams, str], val: Any = None) -> Self:
        vp = self.vparams

        if val is None:
            if isinstance(key, VisParams):
                self.vparams.overwrite(key)
                return self

        if isinstance(val, list):
            count = len(val)
            assert count == len(vp.instances)

            for i in range(count):
                setattr(vp.instances[i], key, val[i])

        else:
            setattr(vp, key, val)
        return self

    @property
    def vparams(self) -> VisParams:
        params = getattr(self, '___v_params', None)
        if params is None:
            params = VisParams()
            setattr(self, '___v_params', params)
        return params

    @vparams.deleter
    def vparams(self) -> None:
        delattr(self, '___v_params')

    def caption(self, _c: Any, **kwargs: Unpack[TextParams]) -> Self:
        kwargs['content'] = str(_c)
        kwargs.setdefault('color', 'white')
        kwargs['color'] = Color(kwargs['color'])
        kwargs.setdefault('align', 'bm')
        kwargs.setdefault('bgrd', 'none')
        self.vparams.texts.append(kwargs)
        return self

    def named(self, name: str = None, color: Any = None) -> Self:
        return self.vis_with('name', name).vis_with('name_color', Color(color) if color else Color.Grey())

    def colored(self, color: Any = None) -> Self:
        return self.vis_with('color', Color(color) if color else Color.Grey())

    def thick(self, thickness: float = None) -> Self:
        return self.vis_with('thickness', thickness)

    def mode(self, mode: str) -> Self:
        return self.vis_with('mode', mode)

    def transformed(self, matrix: Union[np.ndarray, List[np.ndarray]]) -> Self:
        return self.vis_with('matrix', matrix)

    def moved(self, *args: float) -> Self:
        return self.transformed(Matrix.TRS(translate=np.array(args)).buf)

    def dups(self, cnt: int) -> Self:
        vp = self.vparams
        vp.instances = [
            copy.deepcopy(vp) for _ in range(cnt)
        ]
        return self

    def fill(self, val: Any) -> Self:
        if val is not None:
            val = Color(val)
        return self.vis_with('fill', val)

    def err(self, key: str) -> None:
        raise ValueError(
            f'Object {type(self)} received illegal draw param {key}:{self.vparams.get(key, None)}!')