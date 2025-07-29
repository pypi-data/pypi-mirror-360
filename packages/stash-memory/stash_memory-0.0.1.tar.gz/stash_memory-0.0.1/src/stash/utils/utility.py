#-------------------- Imports --------------------

from typing import Type, List
from ..classes.fieldinfo import FieldInfo

#-------------------- Utility Functions --------------------

def check_metadata(source_cls: Type, target_cls: Type):
    for attr in ("__doc__", "__module__", "__annotations__", "__qualname__"):
        if hasattr(source_cls, attr):
            setattr(target_cls, attr, getattr(source_cls, attr))


def conserve_methods(source_cls: Type, target_cls: Type) -> None:
    for base_cls in reversed(source_cls.__mro__):
        for attr_name in dir(base_cls):
            attr = getattr(base_cls, attr_name)
            func = attr
            if isinstance(attr, (staticmethod, classmethod)):
                func = attr.__func__
            if getattr(func, "_conserve", False):
                setattr(target_cls, attr_name, attr)


def get_annotations(cls: Type) -> List[FieldInfo]:
    results = []
    for param, anno in cls.__annotations__.items():
        default = cls.__dict__.get(param, None)
        results.append(FieldInfo(
            value_name=param,
            type_annotation=anno,
            has_default=param in cls.__dict__,
            default_value=default
        ))
        
    return results


def create_cache_key(cls: Type, freeze: bool):
    fields = get_annotations(cls)
    field_key = tuple(
        (f.value_name, f.type_annotation, f.default_value if f.has_default else None) for f in fields)
    return(
        cls.__module__,
        cls.__qualname__,
        field_key,
        freeze
    )

        