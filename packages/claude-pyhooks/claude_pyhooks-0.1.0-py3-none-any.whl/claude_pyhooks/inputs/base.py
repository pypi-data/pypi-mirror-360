"""
Base input class for hook data parsing.

This module defines the abstract base class for all input data structures
that parse JSON input from Claude Code.
"""

import json
import sys
from abc import ABC
from dataclasses import MISSING, dataclass, fields
from typing import Any, Type, TypeVar

T = TypeVar("T", bound="HookInput")


@dataclass(frozen=True, slots=True)
class HookInput(ABC):
    """Base class for all hook inputs."""

    @classmethod
    def from_json(cls: Type[T], data: str | dict[str, Any]) -> T:
        data_dict = json.loads(data) if isinstance(data, str) else dict(data)
        data_dict = cls._apply_converters(data_dict)
        # Only pass fields that are defined in the dataclass
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data_dict.items() if k in field_names}
        return cls(**filtered_data)

    @classmethod
    def from_stdin(cls: Type[T]) -> T:
        try:
            raw = sys.stdin.read()
            return cls.from_json(raw)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)

    @classmethod
    def _apply_converters(cls, data: dict[str, Any]) -> dict[str, Any]:
        result = {}
        for field in fields(cls):
            value = data.get(field.name, MISSING)
            if value is MISSING:
                continue

            converter = field.metadata.get("converter")
            result[field.name] = converter(value) if converter else value

        return {**data, **result}
