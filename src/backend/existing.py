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

def type_check[T: IsDataclass](dataclass: type[T], values: tuple[typing.Any, ...]):
    """
    Check the types of the objects in values against the fields of the dataclass
    and raise an exception if they don't match
    """
    hints = typing.get_type_hints(dataclass.__init__)
    for (field_name, expected_type), actual_value in zip(hints.items(), values):
        if not isinstance(actual_value, expected_type):
            raise TypeError(f"Expected {expected_type}, found {type(actual_value)} for {dataclass.__name__}.{field_name}")
