"""
Hook input models for all Claude Code hook types.

This module defines the data structures for parsing JSON input from Claude Code
for each supported hook type.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from claude_pyhooks.inputs.base import HookInput
from claude_pyhooks.inputs.responses import TOOL_RESPONSE_CLASSES
from claude_pyhooks.inputs.tools import TOOL_INPUT_CLASSES
from claude_pyhooks.utils.json_element import DictFrozenElement

if TYPE_CHECKING:
    from claude_pyhooks.inputs.responses import ToolResponse
    from claude_pyhooks.inputs.tools import ToolInput


@dataclass(frozen=True, slots=True)
class PreToolUseInput(HookInput, DictFrozenElement):
    session_id: str | None = field(default=None)
    transcript_path: Path | None = field(default=None, metadata={"converter": Path})
    tool_name: str | None = field(default=None)
    tool_input: "ToolInput | dict[str, Any] | None" = field(default=None)
    hook_event_name: str | None = field(default=None)

    def __post_init__(self):
        """Convert tool input to appropriate class based on tool_name."""
        if isinstance(self.tool_input, dict) and self.tool_name:
            input_class = TOOL_INPUT_CLASSES.get(self.tool_name)
            if input_class:
                converted_input = input_class.from_json(self.tool_input)
                object.__setattr__(self, "tool_input", converted_input)


@dataclass(frozen=True, slots=True)
class PostToolUseInput(HookInput, DictFrozenElement):
    session_id: str | None = field(default=None)
    transcript_path: Path | None = field(default=None, metadata={"converter": Path})
    tool_name: str | None = field(default=None)
    tool_input: "ToolInput | dict[str, Any] | None" = field(default=None)
    tool_response: "ToolResponse | dict[str, Any] | str | list[dict[str, Any]] | None" = field(
        default=None
    )
    hook_event_name: str | None = field(default=None)

    def __post_init__(self):
        """Convert tool input and response to appropriate classes based on tool_name."""
        if isinstance(self.tool_input, dict) and self.tool_name:
            input_class = TOOL_INPUT_CLASSES.get(self.tool_name)
            if input_class:
                converted_input = input_class.from_json(self.tool_input)
                object.__setattr__(self, "tool_input", converted_input)

        if isinstance(self.tool_response, (dict, str, list)) and self.tool_name:
            response_class = TOOL_RESPONSE_CLASSES.get(self.tool_name)
            if response_class:
                response_data = self.tool_response

                if not isinstance(response_data, dict):
                    response_data = {"items": response_data}

                converted_response = response_class.from_json(response_data)
                object.__setattr__(self, "tool_response", converted_response)


@dataclass(frozen=True, slots=True)
class NotificationInput(HookInput, DictFrozenElement):
    session_id: str | None = field(default=None)
    transcript_path: Path | None = field(default=None, metadata={"converter": Path})
    message: str | None = field(default=None)
    title: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class StopInput(HookInput, DictFrozenElement):
    session_id: str | None = field(default=None)
    transcript_path: Path | None = field(default=None, metadata={"converter": Path})
    stop_hook_active: bool | None = field(default=None)


@dataclass(frozen=True, slots=True)
class SubagentStopInput(HookInput, DictFrozenElement):
    session_id: str | None = field(default=None)
    transcript_path: Path | None = field(default=None, metadata={"converter": Path})
    stop_hook_active: bool | None = field(default=None)
