#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import inspect
import sys
from datetime import datetime
from typing import Any, Generic, TypeVar

from typing_extensions import get_args, get_origin

from pendingai.exceptions import ValidationError

Union: Any
if sys.version_info.minor < 10:
    from typing import Union as tUnion  # type: ignore

    Union = tUnion
else:
    from types import UnionType  # type: ignore

    Union = UnionType


__supported_builtins__: tuple[type] = (datetime,)

T = TypeVar("T", bound="Object")


class Object(dict):
    def __init__(self, **fields: Any):
        super().__init__(**fields)
        annotations: dict[str, type] = self.__parsed_annotations__
        fields = self.__defaults__ | fields

        # enforce all required fields defined as resource fields from
        # class attributes to be required in the provided fields if the
        # attribute type hint is non-nullable
        for field_name, field_type in annotations.items():
            if (
                field_name not in fields
                and type(None) not in get_args(field_type)
                and field_type is not None
            ):
                raise TypeError(f"Missing required field '{field_name}'.")

        for field_name, field_type in annotations.items():
            try:
                setattr(self, field_name, self._cast(field_type, fields[field_name]))
            except TypeError as e:
                raise ValidationError(field_name, fields[field_name], field_type) from e

    @classmethod
    def _cast(cls, obj_type: type[Any], obj: Any) -> Any:
        if obj_type == datetime:
            return datetime.fromisoformat(obj)
        if get_origin(obj_type) is Union:
            for union_type in get_args(obj_type):
                try:
                    return union_type(obj)
                except Exception:
                    pass
            raise TypeError("Unable to cast to union type.")
        return obj_type(obj)

    @property
    def __defaults__(self) -> dict[str, Any]:
        return dict(
            [
                a
                for a in inspect.getmembers(
                    self.__class__, lambda x: not inspect.isroutine(x)
                )
                if not (a[0].startswith("__") and a[0].endswith("__"))
            ]
        )

    @property
    def __parsed_annotations__(self) -> dict[str, type]:
        annotations: dict[str, type | str] = (
            self.__dict__.get("__annotations__", None)
            if isinstance(self, type)
            else getattr(self, "__annotations__", {})
        )
        _annotations: dict[str, type] = {}
        for field_name, field_type in annotations.items():
            if isinstance(field_type, str):
                _annotations[field_name] = eval(field_type)
            else:
                _annotations[field_name] = field_type
        return _annotations

    def __getitem__(self, key: str):
        if not hasattr(self, key):
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if not hasattr(self, key) or key not in self.__parsed_annotations__:
            raise KeyError(key)
        if not isinstance(value, (dt := self.__parsed_annotations__.get(key, None))):  # type: ignore
            raise ValueError(f"'{key}' requires type '{dt.__name__ if dt else dt}'.")
        setattr(self, key, value)


class ListObject(Generic[T], Object):
    object: str = "list"
    data: list[T]
    has_more: bool
