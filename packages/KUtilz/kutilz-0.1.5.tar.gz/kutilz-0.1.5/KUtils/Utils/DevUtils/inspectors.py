import dataclasses
import inspect
import types
import typing
from inspect import signature
from KUtils.Typing import *


def return_of(fun: Callable[P, T]) -> Type[T]:
    sig = signature(fun)
    ret_type = sig.return_annotation
    if ret_type == sig.empty:
        return Any
    else:
        return ret_type

def of_attrs(obj: object, type: Type[T]) -> Dict[str, Type[T]]:
    ret = {}
    for attr, val in obj.__dict__:
        if isinstance(val, type):
            ret[attr] = val

    return ret

def explit_of(cls: type, name: str) -> Optional[Any]:
    return cls.__dict__.get(name, None)

def explicit_attrs(cls: type, excludes: List[str]) -> Dict[str, Any]:
    keys = [key for key in cls.__dict__.keys() if not ( key.startswith('__') or key.startswith('_') )]
    keys = set(keys) - set(excludes)
    return {
        key: cls.__dict__[key] for key in keys
    }

def fki_get(obj: Any, key: str, type: Type[T], default: T = None) -> Optional[None]:
    pass


def bases_that(cls: type, predicate: Callable[[type], bool], include_this: bool = False) -> List[type]:
    res = list(filter(cls.mro(), predicate))
    if not include_this:
        if cls in res:
            res.remove(cls)
            
    return res

def bind(obj: object, name: str, meth: Callable) -> None:
    setattr(obj, name, types.MethodType(meth, obj))

def strip_annotated(obj: Annotated) -> Tuple:
    if typing.get_origin(obj):
        return obj.__metadata__
    else:
        return [obj]

def is_annotated_type(obj: Any) -> bool:
    return 'AnnotatedAlias' in obj.__class__.__name__

def strip_if_annotated(obj: Any) -> Tuple[Type, Optional[Tuple]]:
    if is_annotated_type(obj):
        return typing.get_origin(obj), obj.__metadata__
    else:
        return obj, None
    
def strip_if_is_generic(obj: Any) -> Tuple[Tuple[Type, ...], Optional[Type]]:
    origin = typing.get_origin(obj)
    
    if not origin:
        return (obj), None
    else:
        return origin, typing.get_args(obj)

def caller_file() -> Path:
    frame = inspect.stack()[2]
    return Path(frame.filename)

@dataclasses.dataclass
class ContainerSpec:
    container_type: type
    core: type
    auxt: dict = None

def inspect_container_type(_t: Any) -> Optional[ContainerSpec]:
    origin = typing.get_origin(_t)
    if origin is not None:
        args = typing.get_args(_t)
        if origin is dict:
            return ContainerSpec(container_type=dict, core=args[1], auxt=dict(key=args[0]))
        if origin in (list, set):
            return ContainerSpec(container_type=list, core=args[0])

    return None


def unwrap_t(type: type) -> type:
    _t, _ = strip_if_is_generic(type)
    if type is _t:
        return _t
    else:
        return unwrap_t(_t)