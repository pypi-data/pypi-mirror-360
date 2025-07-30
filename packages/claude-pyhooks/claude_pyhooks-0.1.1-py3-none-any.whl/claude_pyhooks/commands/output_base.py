"""
Base classes for commands and outputs in Claude Code hooks.
"""

import sys
from dataclasses import dataclass, field
from typing import Any, ClassVar, Type, TypeVar

from claude_pyhooks.utils.json_element import DictElement


class Command:
    def execute(self) -> None:
        """Execute the command."""
        raise NotImplementedError("Subclasses must implement execute()")


T = TypeVar("T", bound="HookOutput")


@dataclass(slots=True)
class HookOutput(Command, DictElement):
    DICT_NAME_MAPPING: ClassVar[dict[str, str]] = DictElement.DICT_NAME_MAPPING | {
        "is_continue": "continue"
    }
    # Common fields for all hook outputs
    is_continue: bool | None = field(default=None)
    stopReason: str | None = field(default=None)
    suppressOutput: bool | None = field(default=None)
    _exit_code: int | None = field(default=None)

    @classmethod
    def create(cls: Type[T], **kwargs: Any) -> T:
        # Filter out None values
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return cls(**filtered_kwargs)  # type: ignore[arg-type]

    def _get_output_fields(self) -> dict[str, str]:
        # Base field mapping for common fields
        fields_map = {
            "is_continue": "continue",
            "stop_reason": "stopReason",
            "suppress_output": "suppressOutput",
        }

        # Add class-specific fields if they exist
        if hasattr(self.__class__, "OUTPUT_FIELDS"):
            fields_map.update(getattr(self.__class__, "OUTPUT_FIELDS"))

        return fields_map

    def execute(self) -> None:
        """
        Execute the output command by printing JSON to stdout.

        This is the primary method hooks should call to send their response.
        """
        self._pre_execute()
        output_file = sys.stdout
        if self._exit_code == 2:
            output_file = sys.stderr
        print(self.to_json(), file=output_file)
        if self._exit_code is not None:
            sys.exit(self._exit_code)

    def _pre_execute(self) -> None:
        if self.is_continue is False:
            self._exit_code = 2
