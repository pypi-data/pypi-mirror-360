"""Utilities for converting string values to typed Python objects."""

# flake8: noqa: D103

from __future__ import annotations

import ast
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Literal, Type, cast, get_args, get_origin

from pydantic import BaseModel

from datarush.core.types import ColumnStr, StringMap, TableStr, TextStr


def convert_to_type[T](value: str, to_type: type[T] | None) -> T:
    """Convert a string value to the specified type."""
    if is_string_enum(to_type):
        return to_type(value)  # type: ignore

    if is_literal(to_type):
        if value not in get_args(to_type):
            raise ValueError(f"Value '{value}' is not a valid literal for type {to_type}")
        return value  # type: ignore

    if to_type is not None and issubclass(to_type, BaseModel):
        return to_type.model_validate_json(value)  # type: ignore

    if to_type not in _TYPE_PARSERS:
        raise ValueError(f"Unsupported type {to_type} for conversion")
    parser = _TYPE_PARSERS[to_type]
    return cast(T, parser(value))


def is_string_enum(type_: Type | None) -> bool:
    """Check if the type is a string-based enum."""
    if type_ is None:
        return False
    origin_cls = get_origin(type_) or type_
    try:
        return issubclass(origin_cls, str) and issubclass(origin_cls, Enum)
    except TypeError:
        # If type_ is not a class or does not support subclassing, return False
        return False


def is_literal(type_: Type | None) -> bool:
    """Check if the type is a Literal."""
    if type_ is None:
        return False

    return get_origin(type_) is Literal


def types_are_equal(type1: Type | None, type2: Type | None) -> bool:
    """Check if two generic types are structurally equal."""
    origin1, origin2 = get_origin(type1), get_origin(type2)
    args1, args2 = get_args(type1), get_args(type2)

    if origin1 is None or origin2 is None:
        return type1 is type2

    return origin1 == origin2 and args1 == args2


def _to_bool(value: str) -> bool:
    """Convert string to boolean."""
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"Cannot convert {value} to boolean")


_TYPE_PARSERS: dict[type, Callable[[str], Any]] = {
    bool: _to_bool,
    str: str,
    TableStr: str,
    ColumnStr: str,
    int: int,
    float: float,
    date: lambda v: datetime.fromisoformat(v).date(),
    datetime: datetime.fromisoformat,
    list[str]: lambda v: [item.strip().strip("'").strip('"') for item in v.strip("[]").split(",")],
    list[int]: lambda v: [int(item.strip()) for item in v.strip("[]").split(",")],
    list[float]: lambda v: [float(item.strip()) for item in v.strip("[]").split(",")],
    TextStr: str,
    StringMap: ast.literal_eval,
    dict: ast.literal_eval,
}
