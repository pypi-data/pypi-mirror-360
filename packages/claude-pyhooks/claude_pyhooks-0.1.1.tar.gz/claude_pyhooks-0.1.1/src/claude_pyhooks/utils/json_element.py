"""
Base classes for JSON elements.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, ClassVar


class JSONElement(ABC):
    """Base class for elements that can be converted to JSON."""

    def _convert_value(self, value: Any, *, convert_path_to_str: bool = True) -> Any:
        if isinstance(value, Path):
            return str(value) if convert_path_to_str else value

        if hasattr(value, "to_json") and callable(getattr(value, "to_json")):
            try:
                return value.to_json(convert_path_to_str=convert_path_to_str)
            except TypeError:
                return value.to_json()

        if isinstance(value, str):
            return value

        if isinstance(value, dict):
            return {
                k: self._convert_value(v, convert_path_to_str=convert_path_to_str)
                for k, v in value.items()
            }

        if hasattr(value, "__iter__"):
            try:
                converted_items = [
                    self._convert_value(item, convert_path_to_str=convert_path_to_str)
                    for item in value
                ]

                if isinstance(value, tuple):
                    return tuple(converted_items)
                elif isinstance(value, set):
                    return set(converted_items)
                else:
                    return converted_items
            except (TypeError, ValueError):
                pass

        return value


@dataclass(slots=True)
class DictElement(JSONElement):
    DICT_NAME_MAPPING: ClassVar[dict[str, str]] = {}

    def to_json(self, *, convert_path_to_str: bool = True) -> dict[str, Any]:
        return {
            (
                self.DICT_NAME_MAPPING[field.name]
                if field.name in self.DICT_NAME_MAPPING
                else field.name
            ): v
            for field in fields(self)
            if not field.name.startswith("_")
            and (
                v := self._convert_value(
                    getattr(self, field.name), convert_path_to_str=convert_path_to_str
                )
            )
            is not None
        }


@dataclass(frozen=True, slots=True)
class DictFrozenElement(JSONElement):
    DICT_NAME_MAPPING: ClassVar[dict[str, str]] = {}

    def to_json(self, *, convert_path_to_str: bool = True) -> dict[str, Any]:
        return {
            (
                self.DICT_NAME_MAPPING[field.name]
                if field.name in self.DICT_NAME_MAPPING
                else field.name
            ): v
            for field in fields(self)
            if not field.name.startswith("_")
            and (
                v := self._convert_value(
                    getattr(self, field.name), convert_path_to_str=convert_path_to_str
                )
            )
            is not None
        }


@dataclass(frozen=True, slots=True)
class ListFrozenElement(JSONElement):
    @abstractmethod
    def to_json(self, *, convert_path_to_str: bool = True) -> list[Any]:
        pass


@dataclass(frozen=True, slots=True)
class StrFrozenElement(JSONElement):
    @abstractmethod
    def to_json(self, *, convert_path_to_str: bool = True) -> str:
        pass


class StrElementFromEnum:
    @abstractmethod
    def to_json(self, *, convert_path_to_str: bool = True) -> str:
        pass
