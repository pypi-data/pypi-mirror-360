"""
Command execution and output generation for Claude Code hooks.

This module provides all command-related functionality including base classes,
output models, audio commands, and command queues.
"""

from claude_pyhooks.commands.audio import (
    DEFAULT_BEEP,
    ERROR_BEEP,
    SUCCESS_BEEP,
    WARNING_BEEP,
    BeepCommand,
    BeepSequence,
    SleepCommand,
)
from claude_pyhooks.commands.output_base import Command
from claude_pyhooks.commands.outputs import (
    PostToolUseDecision,
    PostToolUseOutput,
    PreToolUseDecision,
    PreToolUseOutput,
    StopDecision,
    StopOutput,
    SubagentStopDecision,
    SubagentStopOutput,
)
from claude_pyhooks.commands.queue import CommandQueue

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
    "PostToolUseOutput",
    "PostToolUseDecision",
    "PreToolUseOutput",
    "PreToolUseDecision",
    "StopOutput",
    "StopDecision",
    "SubagentStopOutput",
    "SubagentStopDecision",
]
