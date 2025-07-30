from __future__ import annotations

import pathlib
from pathlib import Path
import typing
from typing import (
                    List,
                    Union,
                    Optional,
                    Tuple,
                    Any,
                    Callable,
                    Dict,
                    OrderedDict,
                    Type,
                    
                    Protocol,
                    Mapping,
                    Iterator,
                    Iterable,
                    Literal,
                    cast,
                    Awaitable,
                    ClassVar,
                    final)

from typing_extensions import (ParamSpec,
Generic,
                               Concatenate,
                               Self,
                               TypeVar,
                               Set,
                               TypeAlias,
                               TypedDict,
                               TypeVarTuple,
                               Unpack,
                               TYPE_CHECKING,
                               NamedTuple,
                               Annotated,
                               NotRequired,
                               overload,
                               override)

from types import ModuleType
from functools import update_wrapper
from numbers import Number
import abc
from abc import ABC, abstractmethod


IParams = Dict[str, Any]

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
P = ParamSpec('P')
Ts = TypeVarTuple('Ts')
NormalizedColor = TypeVar('NormalizedColor', bound=Tuple[float, float, float])

# PathLike = TypeVar('PathLike', pathlib.Path, str, covariant=True)
PathLike = Union[Path, str]
JObject = Dict[str, Union[str, Any]]
JSONSerializable = JObject

# PathOrContent = Union[PathLike, Generic[T]]
JSONPoC = Union[PathLike, JObject]

class Fuck(Exception): pass