from __future__ import annotations

import pydantic
from pydantic import Field
from KUtils.Typing import *
import inspect
from typing import get_type_hints
from inspect import signature
import functools

class Argpack:
    def __str__(self):
        out = self.args.__str__() + '\n' + self.kwargs.__str__()
        return out

    def __init__(self, *args, **kwargs):
        self.args = list(args) or []
        self.kwargs = kwargs or {}

    def add(self, value: Any, keyword: str =None):
        if None is keyword:
            self.args.append(value)
        else:
            self.kwargs[keyword]=value

    def call(self, fun: Callable[..., T]) -> T:
        return fun(*self.args, **self.kwargs)

class Parameter(inspect.Parameter):
    def __init__(self, orig: inspect.Parameter):
        for slot_name in inspect.Parameter.__slots__:
            setattr(self, slot_name, getattr(orig, slot_name))

        if self.annotation == self.empty:
            setattr(self, '_annotation', typing.Any)

    def validate(self, val) -> bool:
        if inspect.getmodule(type(self.annotation)) is typing:
            return True

        return (not self.typed) or isinstance(val, self.annotation)

    def coarse(self, val):
        if self.validate(val) is True:
            return val
        else:
            return self.annotation(val)

    @property
    def typed(self) -> bool:
        return self.annotation is not typing.Any

    @property
    def has_default(self) -> bool:
        return self.default != self.empty

    @property
    def has_name(self) -> bool:
        return self.name != self.empty

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def pd_field(self) -> pydantic.Field:
        from KUtils import devu

        type, field = devu.strip_if_annotated(self.annotation)
        if field is not None and isinstance(field, pydantic.Field):
            return self.annotation
        else:
            return Annotated[
                type,
                pydantic.Field(
                default=self.default,
            )]

class Argspec:
    @property
    def allow_var_pos(self) -> bool:
        return self.var_pos is not None

    @property
    def allow_var_kwd(self) -> bool:
        return self.var_kwd is not None

    
    def __init__(self,
                 signature: inspect.Signature,
                 strict: bool = True):
        self.params = [
            Parameter(param) for _, param in signature.parameters.items()
        ]
        self.ret = signature.return_annotation
        kw_only = {}
        by_name = {}
        
        self.var_pos = None
        self.var_kwd = None
        
        if strict:
            for param in self.params:
                if not param.typed and param.name not in {'self', 'args', 'kwargs'}:
                    assert param.typed, f'Parameter {param.name} has no type hint, this is not allowed.'

        for i, param in enumerate(self.params):
            if param.kind is param.KEYWORD_ONLY:
                kw_only[param.name] = param
            elif (param.kind is param.POSITIONAL_ONLY) and (param.name == param.empty):
                param.name = f'_anoynmous_arg_{i}'
            elif (param.kind is param.VAR_POSITIONAL):
                self.var_pos = param.name
                continue
            elif (param.kind is param.VAR_KEYWORD):
                self.var_kwd = param.name
                continue
            
            by_name[param.name] = param
        
        self.__kw_only = kw_only
        self.__by_name = by_name

    @functools.cached_property
    def pos_count(self) -> int:
        return len([param for param in self.params if param.kind is not param.KEYWORD_ONLY])

    def by_pos(self, index: int):
        return self.params[index]

    def by_name(self, name: str):
        return self.__by_name[name]

    def kwargs_to_argpack(self, kwargs: dict):
        args = []
        for param in self.params:
            if param.kind in { param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD }:
                args.append(kwargs.pop(param.name))

        return Argpack(*args, **kwargs)

    def validate(self, *args, **kwargs) -> Argpack:
        if len(args) > 0 and isinstance(args[0], Argpack):
            return self.validate(*args[0].args, **args[0].kwargs)

        _kwargs = self.to_kwargs(*args, **kwargs)
        for name, param in self.__by_name.items():
            if name not in _kwargs:
                if param.has_default:
                    _kwargs[name] = param.default
                else:
                    raise KeyError(f'Missing keyword argument {name}')
            else:
                _kwargs[name] = param.coarse(_kwargs[name])

        return self.kwargs_to_argpack(_kwargs)


    def coarse(self, *args, **kwargs) -> Argpack:
        return self.validate(*args, **kwargs)

    @classmethod
    def Extract(cls, fun: Callable | type, strict: bool = False) -> Self:
        if isinstance(fun, type):
            #Remove self from signature and make return type the type
            sig = signature(functools.partial(fun.__init__, None))
            setattr(sig, '_return_annotation', fun)
        else:
            sig = signature(fun)
        return Argspec(sig, strict)

    @functools.cached_property
    def name2type(self) -> Dict[str, type]:
        return {
            name: param.annotation for name, param in self.__by_name.items()
        }

    @functools.cached_property
    def name2defaults(self) -> Dict[str, Any]:
        return {
            param.name: param.default for param in self.params if param.has_default
        }

    @functools.cached_property
    def named(self) -> Dict[str, Parameter]:
        return {
            param.name: param for param in self.params if param.has_name
        }

    def to_kwargs(self, *args, **kwargs) -> dict:
        full_kwargs = {}

        for i, arg in enumerate(args):
            if i > len(self.params) - 1:
                break
            argname = self.params[i].name
            full_kwargs[argname] = arg

        # Add explicitly passed keyword arguments
        for name, value in kwargs.items():
            if name in self.__by_name:
                full_kwargs[name] = value
            else:
                if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in self.params):
                    full_kwargs[name] = value
                else:
                    continue

        for name, default in self.name2defaults.items():
            if name not in full_kwargs:
                full_kwargs[name] = default

        return full_kwargs

class PydanticArgspec(Argspec):
    def __init__(self, signature: inspect.Signature, name: str = None):
        super().__init__(signature, strict=True)
        self.schema = pydantic.create_model(
            name,
            **{
                pn: param.pd_field for pn, param in self.named.items()
            },
            __config__={
                'extra': 'ignore'
            }
        )

    def coarse(self, *args, **kwargs) -> Argpack:
        kwargs = self.to_kwargs(*args, **kwargs)
        model = self.schema(**kwargs)
        return Argpack(**model.model_dump())

    @classmethod
    def Extract(cls, fun: Callable | type, name: str = None) -> Self:
        if isinstance(fun, type):
            sig = signature(functools.partial(fun.__init__, None))
            setattr(sig, '_return_annotation', fun)
        else:
            sig = signature(fun)
        return cls(sig, name=fun.__name__ + '_PYDANTIC_GEN')



def argkeys(f: object)->List[str]:
    spec = inspect.getfullargspec(f)
    signature = inspect.signature(f).parameters
    sig_keys = list(signature.keys())
    return list(set(spec.args + spec.kwonlyargs + sig_keys))