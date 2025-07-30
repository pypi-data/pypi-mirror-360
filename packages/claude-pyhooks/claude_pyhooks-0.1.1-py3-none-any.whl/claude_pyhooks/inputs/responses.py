"""
Tool-specific response models for Claude Code tools.

This module defines the data structures for parsing tool response data
for each specific tool type supported by Claude Code.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from claude_pyhooks.inputs.base import HookInput
from claude_pyhooks.inputs.tools import EditOperation
from claude_pyhooks.utils.json_element import DictFrozenElement, ListFrozenElement


# Generic converter functions
def _convert_dataclass_list(dataclass_type: type) -> Callable[[Any], list]:
    """Create a converter function for lists of dataclass objects."""

    def converter(value: Any) -> list:
        if not isinstance(value, list):
            return []
        return [
            dataclass_type(**item) if isinstance(item, dict) else item for item in value
        ]

    return converter


def _convert_dataclass(dataclass_type: type) -> Callable[[Any], Any]:
    """Create a converter function for a single dataclass object."""

    def converter(value: Any) -> Any:
        if isinstance(value, dict):
            return dataclass_type(**value)
        elif value is None:
            return None
        return dataclass_type()

    return converter


def _convert_ls_items(value: Any) -> list[str]:
    """Convert LS response format to list of items."""
    if isinstance(value, str):
        lines = value.strip().split("\n")
        items = []
        for line in lines:
            item = line.lstrip("- ").strip()
            if item:
                items.append(item)
        return items
    elif isinstance(value, list):
        return value
    return []


@dataclass(frozen=True, slots=True)
class ToolResponse(HookInput):
    """Base class for all tool responses."""


@dataclass(frozen=True, slots=True)
class BashResponse(ToolResponse, DictFrozenElement):
    stdout: str | None = field(default=None)
    stderr: str | None = field(default=None)
    interrupted: str | None = field(default=None)
    isImage: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class EditPatch(HookInput, DictFrozenElement):
    """Represents an edit patch."""

    oldStart: int | None = field(default=None)
    oldLines: int | None = field(default=None)
    newStart: int | None = field(default=None)
    newLines: int | None = field(default=None)
    lines: list[str] | None = field(default=None)


@dataclass(frozen=True, slots=True)
class EditResponse(ToolResponse, DictFrozenElement):
    filePath: Path = field(
        default_factory=lambda: Path(""), metadata={"converter": Path}
    )
    oldString: str = ""
    newString: str = ""
    originalFile: str = ""
    structuredPatch: list[EditPatch] = field(
        default_factory=list, metadata={"converter": _convert_dataclass_list(EditPatch)}
    )
    userModified: bool = False
    replaceAll: bool = False


@dataclass(frozen=True, slots=True)
class WriteResponse(ToolResponse, DictFrozenElement):
    type: str = ""
    filePath: Path = field(
        default_factory=lambda: Path(""), metadata={"converter": Path}
    )
    content: str = ""
    structuredPatch: list = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ReadFileInfo(HookInput, DictFrozenElement):
    filePath: Path = field(
        default_factory=lambda: Path(""), metadata={"converter": Path}
    )
    content: str | None = field(default=None)
    numLines: int | None = field(default=None)
    startLine: int | None = field(default=None)
    totalLines: int | None = field(default=None)


@dataclass(frozen=True, slots=True)
class ReadResponse(ToolResponse, DictFrozenElement):
    type: str = ""
    file: ReadFileInfo = field(
        default_factory=lambda: ReadFileInfo(),
        metadata={"converter": _convert_dataclass(ReadFileInfo)},
    )


# Import EditOperation converter function
def _convert_edit_operations(value: Any) -> list[EditOperation]:
    """Convert edit operation dicts to EditOperation objects."""
    if not isinstance(value, list):
        return []
    from claude_pyhooks.inputs.tools import EditOperation

    return [EditOperation(**edit) if isinstance(edit, dict) else edit for edit in value]


@dataclass(frozen=True, slots=True)
class MultiEditResponse(ToolResponse, DictFrozenElement):
    filePath: Path = field(
        default_factory=lambda: Path(""), metadata={"converter": Path}
    )
    edits: list[EditOperation] = field(
        default_factory=list, metadata={"converter": _convert_edit_operations}
    )
    originalFileContents: str = ""
    structuredPatch: list[EditPatch] = field(
        default_factory=list, metadata={"converter": _convert_dataclass_list(EditPatch)}
    )
    userModified: bool = False


@dataclass(frozen=True, slots=True)
class GlobResponse(ToolResponse, DictFrozenElement):
    filenames: list[str] | None = field(default=None)
    durationMs: int | None = field(default=None)
    numFiles: int | None = field(default=None)
    truncated: bool | None = field(default=None)


@dataclass(frozen=True, slots=True)
class GrepResponse(ToolResponse, DictFrozenElement):
    filenames: list[str] = field(default_factory=list)
    numFiles: int = 0


@dataclass(frozen=True, slots=True)
class LSResponse(ToolResponse, DictFrozenElement):
    items: list[str] = field(
        default_factory=list, metadata={"converter": _convert_ls_items}
    )


@dataclass(frozen=True, slots=True)
class WebFetchResponse(ToolResponse, DictFrozenElement):
    bytes: int = 0
    code: int = 200
    codeText: str = "OK"
    result: str = ""
    durationMs: int = 0
    url: str = ""


@dataclass(frozen=True, slots=True)
class WebSearchResponse(ToolResponse, DictFrozenElement):
    query: str = ""
    results: list = field(default_factory=list)
    durationSeconds: float = 0.0


@dataclass(frozen=True, slots=True)
class TodoReadResponse(ToolResponse, DictFrozenElement):
    success: bool | None = field(default=None)
    todos: list[dict] | None = field(default=None)
    total_todos: int | None = field(default=None)


@dataclass(frozen=True, slots=True)
class TodoWriteResponse(ToolResponse, DictFrozenElement):
    success: bool | None = field(default=None)
    message: str | None = field(default=None)
    todos_written: int | None = field(default=None)


@dataclass(frozen=True, slots=True)
class NotebookCell(HookInput, DictFrozenElement):
    cellType: str | None = field(default=None)
    source: str | None = field(default=None)
    execution_count: int | None = field(default=None)
    cell_id: str | None = field(default=None)
    language: str | None = field(default=None)

    def to_json(self, *, convert_path_to_str: bool = True) -> dict[str, Any]:
        """Convert to dict, preserving original JSON structure."""
        result: dict[str, Any] = {}

        # Always include these fields
        result["cellType"] = self.cellType
        result["source"] = self.source

        # For code cells, include execution_count (even if None) and language if present
        if self.cellType == "code":
            result["execution_count"] = self.execution_count
            if self.language is not None:
                result["language"] = self.language

        # Always include cell_id if present
        if self.cell_id is not None:
            result["cell_id"] = self.cell_id

        return result


@dataclass(frozen=True, slots=True)
class NotebookReadResponse(ToolResponse, ListFrozenElement):
    _ElementType: type = list[dict[str, Any]]
    items: list[NotebookCell] = field(
        default_factory=list,
        metadata={"converter": _convert_dataclass_list(NotebookCell)},
    )

    def to_json(self, *, convert_path_to_str: bool = True) -> list[dict[str, Any]]:
        """Convert to list format (special case for NotebookRead)."""
        return [
            cell.to_json(convert_path_to_str=convert_path_to_str) for cell in self.items
        ]


@dataclass(frozen=True, slots=True)
class NotebookEditResponse(ToolResponse, DictFrozenElement):
    new_source: str | None = field(default=None)
    cell_type: str | None = field(default=None)
    language: str | None = field(default=None)
    edit_mode: str | None = field(default=None)
    error: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class TaskUsage(HookInput, DictFrozenElement):
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    service_tier: str = "standard"


@dataclass(frozen=True, slots=True)
class TaskContent(HookInput, DictFrozenElement):
    type: str | None = field(default=None)
    text: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class TaskResponse(ToolResponse, DictFrozenElement):
    content: list[TaskContent] = field(
        default_factory=list,
        metadata={"converter": _convert_dataclass_list(TaskContent)},
    )
    totalDurationMs: int | None = field(default=None)
    totalTokens: int | None = field(default=None)
    totalToolUseCount: int | None = field(default=None)
    usage: TaskUsage | None = field(
        default=None, metadata={"converter": _convert_dataclass(TaskUsage)}
    )
    wasInterrupted: bool = False


@dataclass(frozen=True, slots=True)
class ExitPlanModeResponse(ToolResponse, DictFrozenElement):
    plan: str | None = field(default=None)
    isAgent: bool = False


# Tool response type mapping
TOOL_RESPONSE_CLASSES = {
    "Bash": BashResponse,
    "Edit": EditResponse,
    "Write": WriteResponse,
    "Read": ReadResponse,
    "MultiEdit": MultiEditResponse,
    "Glob": GlobResponse,
    "Grep": GrepResponse,
    "LS": LSResponse,
    "WebFetch": WebFetchResponse,
    "WebSearch": WebSearchResponse,
    "TodoRead": TodoReadResponse,
    "TodoWrite": TodoWriteResponse,
    "NotebookRead": NotebookReadResponse,
    "NotebookEdit": NotebookEditResponse,
    "Task": TaskResponse,
    "exit_plan_mode": ExitPlanModeResponse,
}
