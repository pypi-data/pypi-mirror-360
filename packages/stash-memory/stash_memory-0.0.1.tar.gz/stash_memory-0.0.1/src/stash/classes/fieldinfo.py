#-------------------- Imports --------------------

from typing import Optional, Any

#-------------------- FieldInfos Class --------------------

class FieldInfo():
    __slots__ = ("value_name", "type_annotation", "has_default", "default_value")

    def __init__(self, value_name: str, type_annotation: Any, has_default: bool, default_value: Optional[Any]):
        self.value_name = value_name
        self.type_annotation = type_annotation
        self.has_default = has_default
        self.default_value = default_value