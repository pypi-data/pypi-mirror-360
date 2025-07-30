from KUtils.Typing import *
import pkgutil

def generic_args(cls: type, count: int = None) -> List[Any]:
    if not isinstance(cls, type):
        cls = cls.__class__

    try:
        orig_bases = cls.__orig_bases__
    except AttributeError:
        orig_bases = [cls]
    params = []
    for base in orig_bases:
        params.extend([*typing.get_args(base)])

    if count is not None:
        assert len(params) == count
    return params


def force_list(obj: Union[T, List[T]]) -> List[T]:
    if isinstance(obj, (list, tuple)):
        return [*obj]
    else:
        return [obj]
    
from importlib import import_module
import importlib
def from_import(module_res: str, obj_name: str, default=None, local=False)->Any:
    module = import_module(module_res, package='.' if local else None)
    return getattr(module, obj_name, default)


def Mapper(keys: Generic[K], items: List[T]) -> Dict[K, T]:
    gen_args = generic_args(keys)
    assert len(gen_args) == len(items)

    return dict(zip(gen_args, items))

def object_counter(cls) -> int:
    _NAME = '__KUTILS__OBJECT__COUNTER__FOR__' + cls.__name__
    count = getattr(cls, _NAME, 0)
    setattr(cls, _NAME, count + 1)

    return count