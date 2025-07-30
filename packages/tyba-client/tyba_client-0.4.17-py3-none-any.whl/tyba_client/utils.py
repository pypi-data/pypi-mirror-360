from enum import Enum
import typing as t

from marshmallow import fields

T = t.TypeVar("T", bound=Enum)


def string_enum(cls: t.Type[T]) -> t.Type[T]:
    """
    decorator to allow Enums to be used with dataclass_json
    Stolen from:
    https://github.com/lidatong/dataclasses-json/issues/101#issuecomment-506418278""
    """

    class EnumField(fields.Field):
        def _serialize(self, value, attr, obj, **kwargs):
            return value.name

        def _deserialize(self, value, attr, data, **kwargs):
            return cls[value]

    if not hasattr(cls, "__metadata__"):
        setattr(cls, "__metadata__", dict())

    metadata = {
        "dataclasses_json": {
            "encoder": lambda v: v.name,
            "decoder": lambda name: cls[name],
            "mm_field": EnumField(),
        }
    }
    cls.__metadata__.update(metadata)
    return cls
