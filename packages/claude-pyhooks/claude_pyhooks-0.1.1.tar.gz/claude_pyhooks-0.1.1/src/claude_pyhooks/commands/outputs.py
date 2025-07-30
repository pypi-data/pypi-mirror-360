"""
Output models for all Claude Code hook types.
"""

from dataclasses import dataclass, field
from enum import Enum, auto

from claude_pyhooks.commands.output_base import HookOutput
from claude_pyhooks.utils.json_element import StrElementFromEnum

# ============================================================================
# Decision Enums
# ============================================================================


class PreToolUseDecision(StrElementFromEnum, Enum):
    approve = auto()
    block = auto()

    def to_json(self, *, convert_path_to_str: bool = True) -> str:
        if self == PreToolUseDecision.approve:
            return "approve"
        return "block"


class PostToolUseDecision(StrElementFromEnum, Enum):
    block = auto()

    def to_json(self, *, convert_path_to_str: bool = True) -> str:
        return "block"


class StopDecision(StrElementFromEnum, Enum):
    block = auto()

    def to_json(self, *, convert_path_to_str: bool = True) -> str:
        return "block"


class SubagentStopDecision(StrElementFromEnum, Enum):
    block = auto()

    def to_json(self, *, convert_path_to_str: bool = True) -> str:
        return "block"


# ============================================================================
# Output Models
# ============================================================================


@dataclass(slots=True)
class PreToolUseOutput(HookOutput):
    decision: PreToolUseDecision | None = field(default=None)
    reason: str | None = field(default=None)

    @classmethod
    def approve(cls) -> "PreToolUseOutput":
        return cls(decision=PreToolUseDecision.approve)

    @classmethod
    def block(cls, reason: str | None = None) -> "PreToolUseOutput":
        return cls(decision=PreToolUseDecision.block, reason=reason)

    def _pre_execute(self) -> None:
        HookOutput._pre_execute(self)
        if self.decision == PreToolUseDecision.block:
            self._exit_code = 2


@dataclass(slots=True)
class PostToolUseOutput(HookOutput):
    decision: PostToolUseDecision | None = field(default=None)
    reason: str | None = field(default=None)

    @classmethod
    def block(cls, reason: str | None = None) -> "PostToolUseOutput":
        return cls(decision=PostToolUseDecision.block, reason=reason)

    def _pre_execute(self) -> None:
        HookOutput._pre_execute(self)
        if self.decision == PostToolUseDecision.block:
            self._exit_code = 2


@dataclass(slots=True)
class StopOutput(HookOutput):
    decision: StopDecision | None = field(default=None)
    reason: str | None = field(default=None)

    @classmethod
    def block(cls, reason: str | None = None) -> "StopOutput":
        return cls(decision=StopDecision.block, reason=reason)

    def _pre_execute(self) -> None:
        HookOutput._pre_execute(self)
        if self.decision == StopDecision.block:
            self._exit_code = 2


@dataclass(slots=True)
class SubagentStopOutput(HookOutput):
    decision: SubagentStopDecision | None = field(default=None)
    reason: str | None = field(default=None)

    @classmethod
    def block(cls, reason: str | None = None) -> "SubagentStopOutput":
        return cls(decision=SubagentStopDecision.block, reason=reason)

    def _pre_execute(self) -> None:
        HookOutput._pre_execute(self)
        if self.decision == SubagentStopDecision.block:
            self._exit_code = 2
