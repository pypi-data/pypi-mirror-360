#-------------------- Imports --------------------

from typing import List, Callable
from ..classes.fieldinfo import FieldInfo
from ..errors import FreezeAttributeException
import sys

#-------------------- Dynamic Method Creation --------------------

def create_init(fields_info: List[FieldInfo], freeze: bool) -> Callable:
    def __init__(self, *args, **kwargs):
        for i, field in enumerate(fields_info):
            if field.value_name in kwargs:
                value = kwargs[field.value_name]
            elif i < len(args):
                value = args[i]
            elif field.has_default:
                value = field.default_value
            else:
                raise TypeError(f"Missing required argument: {field.value_name}")

            if isinstance(value, str):
                value = sys.intern(value)
            setattr(self, field.value_name, value)
        if freeze:
            object.__setattr__(self, "_frozen", True)
    return __init__


def create_repr(class_name: str, field_info: List[FieldInfo]) -> Callable:
    def __repr__(self):
        values = ", ".join(f"{f.value_name}={repr(getattr(self, f.value_name))}" for f in field_info)
        return f"{class_name}({values})"
    return __repr__


def create_eq(field_info: List[FieldInfo]) -> Callable:
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all(getattr(self, f.value_name) == getattr(other, f.value_name) for f in field_info)
    return __eq__


def create_frozen_setattr() -> Callable:
    def __setattr__(self, key, value):
        if getattr(self, "_frozen", False):
            raise FreezeAttributeException(f"Cannot modify {key}, instance is Frozen")
        object.__setattr__(self, key, value)
    return __setattr__