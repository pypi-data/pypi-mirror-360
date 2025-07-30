"""
Claude Hooks - A framework for Claude Code hook development.

This library provides a structured way to develop hooks for Claude Code,
including input parsing, output generation, and command execution.

Example:
    >>> from claude_pyhooks import PreToolUseInput, approve, block
    >>>
    >>> # Read input from stdin
    >>> hook_input = PreToolUseInput.from_stdin()
    >>>
    >>> # Process and return decision
    >>> if should_block(hook_input):
    >>>     block("Operation not allowed").execute()
    >>> else:
    >>>     approve().execute()
"""

__version__ = "0.1.0"
__author__ = "Claude Code Hooks Team"

# Import all public APIs for convenience
from claude_pyhooks.commands import (
    DEFAULT_BEEP,
    ERROR_BEEP,
    SUCCESS_BEEP,
    WARNING_BEEP,
    BeepCommand,
    BeepSequence,
    Command,
    CommandQueue,
    PostToolUseDecision,
    PostToolUseOutput,
    PreToolUseDecision,
    PreToolUseOutput,
    SleepCommand,
    StopDecision,
    StopOutput,
    SubagentStopDecision,
    SubagentStopOutput,
)
from claude_pyhooks.inputs import (
    BashInput,
    BashResponse,
    EditInput,
    EditOperation,
    EditResponse,
    GlobInput,
    GlobResponse,
    GrepInput,
    GrepResponse,
    LSInput,
    LSResponse,
    MultiEditInput,
    MultiEditResponse,
    NotificationInput,
    PostToolUseInput,
    PreToolUseInput,
    ReadInput,
    ReadResponse,
    StopInput,
    SubagentStopInput,
    TodoItem,
    TodoReadInput,
    TodoReadResponse,
    TodoWriteInput,
    TodoWriteResponse,
    ToolInput,
    ToolResponse,
    WebFetchInput,
    WebFetchResponse,
    WebSearchInput,
    WebSearchResponse,
    WriteInput,
    WriteResponse,
)

__all__ = [
    "Command",
    "DEFAULT_BEEP",
    "ERROR_BEEP",
    "SUCCESS_BEEP",
    "WARNING_BEEP",
    "BeepCommand",
    "BeepSequence",
    "CommandQueue",
    "SleepCommand",
    "NotificationInput",
    "PostToolUseInput",
    "PreToolUseInput",
    "StopInput",
    "SubagentStopInput",
    "ToolInput",
    "ToolResponse",
    "BashInput",
    "BashResponse",
    "EditInput",
    "EditOperation",
    "EditResponse",
    "GlobInput",
    "GlobResponse",
    "GrepInput",
    "GrepResponse",
    "LSInput",
    "LSResponse",
    "MultiEditInput",
    "MultiEditResponse",
    "ReadInput",
    "ReadResponse",
    "TodoItem",
    "TodoReadInput",
    "TodoReadResponse",
    "TodoWriteInput",
    "TodoWriteResponse",
    "WebFetchInput",
    "WebFetchResponse",
    "WebSearchInput",
    "WebSearchResponse",
    "WriteInput",
    "WriteResponse",
    "PostToolUseOutput",
    "PostToolUseDecision",
    "PreToolUseOutput",
    "PreToolUseDecision",
    "StopOutput",
    "StopDecision",
    "SubagentStopOutput",
    "SubagentStopDecision",
]
