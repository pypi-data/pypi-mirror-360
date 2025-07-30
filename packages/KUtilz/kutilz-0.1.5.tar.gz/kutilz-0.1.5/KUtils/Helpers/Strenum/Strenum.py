from enum import Enum, IntEnum
from typing_extensions import Self, Union, Generic, TypeVar

LITERALS = TypeVar('LITERALS')

__all__ = ['Strenum', 'Intenum']

class Strenum(str, Enum):
    @classmethod
    def IsLegal(cls, value: str) -> bool:
        return value in cls
    pass

    @classmethod
    def Parse(cls, value: Union[str, Self]) -> Self:
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError(f"Expected str or {cls.__name__}, got {type(value).__name__}")
        value_lower = value.lower()
        for member in cls:
            if member.value.lower() == value_lower:
                return member
        legal_values = [member.value for member in cls]
        raise ValueError(
            f"'{value}' is not a valid {cls.__name__} (case-insensitive). "
            f"Legal values are: {', '.join(legal_values)}"
        )

    # @classmethod
    # def TypeHint(cls) -> Type[Union[Self, Type[LITERALS]]]:
    #     pass

class Intenum(IntEnum):
    @classmethod
    def _missing_(cls, value):
        # Handle string values (case-insensitive match to member names)
        if isinstance(value, str):
            normalized = value.lower()
            for member in cls:
                if member.name.lower() == normalized:
                    return member
        # Fall back to default IntEnum handling for integers
        return super()._missing_(value)