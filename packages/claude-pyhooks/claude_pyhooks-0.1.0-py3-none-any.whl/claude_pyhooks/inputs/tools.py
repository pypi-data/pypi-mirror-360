"""
Tool-specific input models for Claude Code tools.

This module defines the data structures for parsing tool input data
for each specific tool type supported by Claude Code.
"""

from dataclasses import dataclass, field
from pathlib import Path

from claude_pyhooks.inputs.base import HookInput
from claude_pyhooks.utils.json_element import DictFrozenElement


@dataclass(frozen=True, slots=True)
class ToolInput(HookInput):
    """Base class for all pre-tool inputs."""


@dataclass(frozen=True, slots=True)
class BashInput(ToolInput, DictFrozenElement):
    command: str | None = field(default=None)
    timeout: int | None = field(default=None)
    description: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class EditInput(ToolInput, DictFrozenElement):
    file_path: Path | None = field(default=None, metadata={"converter": Path})
    old_string: str | None = field(default=None)
    new_string: str | None = field(default=None)
    replace_all: bool | None = field(default=None)


@dataclass(frozen=True, slots=True)
class WriteInput(ToolInput, DictFrozenElement):
    file_path: Path | None = field(default=None, metadata={"converter": Path})
    content: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class ReadInput(ToolInput, DictFrozenElement):
    file_path: Path | None = field(default=None, metadata={"converter": Path})
    offset: int | None = field(default=None)
    limit: int | None = field(default=None)


@dataclass(frozen=True, slots=True)
class EditOperation(ToolInput, DictFrozenElement):
    old_string: str | None = field(default=None)
    new_string: str | None = field(default=None)
    replace_all: bool | None = field(default=None)


@dataclass(frozen=True, slots=True)
class MultiEditInput(ToolInput, DictFrozenElement):
    file_path: Path | None = field(default=None, metadata={"converter": Path})
    edits: list[EditOperation] = field(
        default_factory=list,
        metadata={
            "converter": lambda edits_list: [
                EditOperation.from_json(edit) if isinstance(edit, dict) else edit
                for edit in edits_list
            ]
            if edits_list
            else []
        },
    )


@dataclass(frozen=True, slots=True)
class GlobInput(ToolInput, DictFrozenElement):
    pattern: str | None = field(default=None)
    path: Path | None = field(
        default=None, metadata={"converter": lambda x: Path(x) if x else None}
    )


@dataclass(frozen=True, slots=True)
class GrepInput(ToolInput, DictFrozenElement):
    pattern: str | None = field(default=None)
    path: Path | None = field(
        default=None, metadata={"converter": lambda x: Path(x) if x else None}
    )
    include: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class LSInput(ToolInput, DictFrozenElement):
    path: Path | None = field(default=None, metadata={"converter": Path})
    ignore: list[str] | None = field(default=None)


@dataclass(frozen=True, slots=True)
class WebFetchInput(ToolInput, DictFrozenElement):
    url: str | None = field(default=None)
    prompt: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class WebSearchInput(ToolInput, DictFrozenElement):
    query: str | None = field(default=None)
    allowed_domains: list[str] | None = field(default=None)
    blocked_domains: list[str] | None = field(default=None)


@dataclass(frozen=True, slots=True)
class TodoItem(ToolInput, DictFrozenElement):
    id: str | None = field(default=None)
    content: str | None = field(default=None)
    status: str | None = field(default=None)  # "pending", "in_progress", "completed"
    priority: str | None = field(default=None)  # "high", "medium", "low"


@dataclass(frozen=True, slots=True)
class TodoReadInput(ToolInput, DictFrozenElement):
    pass


@dataclass(frozen=True, slots=True)
class TodoWriteInput(ToolInput, DictFrozenElement):
    todos: list[TodoItem] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class NotebookReadInput(ToolInput, DictFrozenElement):
    notebook_path: Path | None = field(default=None, metadata={"converter": Path})
    cell_id: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class NotebookEditInput(ToolInput, DictFrozenElement):
    notebook_path: Path | None = field(default=None, metadata={"converter": Path})
    new_source: str | None = field(default=None)
    cell_id: str | None = field(default=None)
    cell_type: str | None = field(default=None)
    edit_mode: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class TaskInput(ToolInput, DictFrozenElement):
    description: str | None = field(default=None)
    prompt: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class ExitPlanModeInput(ToolInput, DictFrozenElement):
    plan: str | None = field(default=None)


# Tool input type mapping
TOOL_INPUT_CLASSES = {
    "Bash": BashInput,
    "Edit": EditInput,
    "Write": WriteInput,
    "Read": ReadInput,
    "MultiEdit": MultiEditInput,
    "Glob": GlobInput,
    "Grep": GrepInput,
    "LS": LSInput,
    "WebFetch": WebFetchInput,
    "WebSearch": WebSearchInput,
    "TodoRead": TodoReadInput,
    "TodoWrite": TodoWriteInput,
    "NotebookRead": NotebookReadInput,
    "NotebookEdit": NotebookEditInput,
    "Task": TaskInput,
    "exit_plan_mode": ExitPlanModeInput,
}
