from __future__ import annotations
import dataclasses
import typing

# This is a protocol. It doesn't do anything, it's only for the type-checker. 
# The `modify` function only works on dataclass types (since they have a `__dataclass_fields__` attribute)
class IsDataclass(typing.Protocol):
    __dataclass_fields__: typing.ClassVar[dict[str, dataclasses.Field[typing.Any]]]


# The syntax `[T: IsDataclass]` tells the type-checker that modify is a *generic* function.
# When calling this function, the `self` parameter can be any type that follows the `IsDataclass` protocol,
# and the return value will have the same type.
def modify[T: IsDataclass](self: T, **kwargs) -> T:
    assert "id" not in kwargs, "Cannot modify id of existing database entry"
    return dataclasses.replace(self, **kwargs)
