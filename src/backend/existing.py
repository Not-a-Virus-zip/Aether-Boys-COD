from __future__ import annotations
import dataclasses
import typing

class IsDataclass(typing.Protocol):
    __dataclass_fields__: typing.ClassVar[dict[str, dataclasses.Field[typing.Any]]]

def modify[T: IsDataclass](self: T, **kwargs) -> T:
    assert "id" not in kwargs, "Cannot modify id of existing database entry"
    return dataclasses.replace(self, **kwargs)