import functools
import typing

from pydantic import (ConfigDict,
                      BaseModel,
                      Field, computed_field, TypeAdapter, model_validator, field_validator, ValidationError,
                      ValidatorFunctionWrapHandler,
                      Discriminator, Tag,
                      field_serializer,
model_serializer
                      )
from pathlib import Path
from typing import Union, List, Set, Generic
from typing_extensions import NotRequired, Self, Type, TypedDict, Unpack, Any, Literal, Optional, Dict, TypeVar, Annotated, ClassVar

DerivedDataClass = TypeVar('DerivedDataClass', default='DataClass')

import yaml
import json

Extra = Annotated[Dict, Field(default_factory=dict)]
SerializableTags = Annotated[List[str], Field(default=None)]

class DumpArgs(TypedDict):
    include: NotRequired[Any]
    exclude: NotRequired[Any]
    mode: NotRequired[Literal['json', 'python']]
    exclude_unset: NotRequired[bool]
    exclude_defaults: NotRequired[bool]
    exclude_none: NotRequired[bool]
    serialize_as_any: NotRequired[bool]


class DataClass(BaseModel):

    model_config = ConfigDict(extra='forbid',
                              use_enum_values=True)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        pass

    @classmethod
    def deserialize(cls, serialized: Dict[str, Any]) -> Self:
        return cls(**serialized)

    @classmethod
    def default_of(cls, key: str) -> Any:
        field_info = cls.model_fields[key]
        return field_info.default

    @classmethod
    def build_default(cls) -> Self:
        return cls()

    @classmethod
    def from_yaml(cls, path: Union[Path, str]) -> Self:
        with open(path, 'r') as file:
            y = yaml.safe_load(file)

        if y is None:
            y = {}

        return cls(**y)

    @classmethod
    def from_json(cls, path: Union[Path, str]) -> Self:
        with open(path, 'r') as file:
            y = json.load(file)

        return cls(**y)

    def to_dict(self, **dumpargs: Unpack[DumpArgs]) -> Dict[str, Any]:
        dumpargs = dumpargs or {}
        dumpargs.setdefault('include', None)
        dumpargs.setdefault('exclude', None)
        dumpargs.setdefault('mode', 'python')
        dumpargs.setdefault('exclude_unset', True)
        dumpargs.setdefault('exclude_none', False)
        dumpargs.setdefault('exclude_defaults', False)
        dumpargs.setdefault('serialize_as_any', True)
        return self.model_dump(**dumpargs)

    def stringify(self, **dumpargs: Unpack[DumpArgs]) -> str:
        return json.dumps(self.to_dict(dumpargs))

    def to_yaml(self, path: Union[Path, str], **dumpargs: Unpack[DumpArgs]) -> None:
        dumpargs['mode'] = 'json'
        serialized = self.to_dict(**dumpargs)

        with open(path, 'w') as file:
            yaml.dump(serialized, file)

    def to_json(self, path: Union[Path, str], pretty: bool = False, **dumpargs: Unpack[DumpArgs]) -> None:
        serialized = self.to_dict(**dumpargs)

        with open(path, 'w') as file:
            json.dump(serialized, file, indent=2 if pretty else None)

    def freeze(self) -> None:
        pass

    def reduce_to(self, other: Type['DataClass']) -> 'DataClass':
        keys = other.model_fields.keys()
        me = self.to_dict()


        inst = other(**{
            key: me[key] for key in keys if key in me
        })

        return inst

def generic_dataclass_builder():
    import inspect
    code = inspect.getsource(DataClass)
    code = code.replace('DataClass', 'GenericDataClass')
    code = code.replace('GenericDataClass(BaseModel)', 'GenericDataClass(BaseModel, Generic[_PLACEHOLDER])')
    return functools.partial(exec, code)

# DerivedGenericDataClass = TypeVar('DerivedGenericDataClass')
# _PLACEHOLDER = TypeVar('_PLACEHOLDER')
# generic_dataclass_builder()()
# if typing.TYPE_CHECKING:
#     GenericDataClass = DataClass
