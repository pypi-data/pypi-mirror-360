"""Tests for utility functions."""

from claude_pyhooks import (
    PostToolUseDecision,
    PostToolUseOutput,
    PreToolUseDecision,
    PreToolUseOutput,
    StopDecision,
    StopOutput,
    SubagentStopDecision,
    SubagentStopOutput,
)


class TestShortcuts:
    def test_pretool_approve(self):
        result = PreToolUseOutput.approve()
        assert isinstance(result, PreToolUseOutput)
        assert result.decision == PreToolUseDecision.approve
        assert result.reason is None

        data = result.to_json()
        assert data["decision"] == "approve"

    def test_pretool_block(self):
        reason = "Operation not allowed"
        result = PreToolUseOutput.block(reason)
        assert isinstance(result, PreToolUseOutput)
        assert result.decision == PreToolUseDecision.block
        assert result.reason == reason

        data = result.to_json()
        assert data["decision"] == "block"
        assert data["reason"] == reason

    def test_posttool_block(self):
        reason = "Command failed"
        result = PostToolUseOutput.block(reason)
        assert isinstance(result, PostToolUseOutput)
        assert result.decision == PostToolUseDecision.block
        assert result.reason == reason

        data = result.to_json()
        assert data["decision"] == "block"
        assert data["reason"] == reason

    def test_stop_block(self):
        reason = "Stopping process"
        result = StopOutput.block(reason)
        assert isinstance(result, StopOutput)
        assert result.decision == StopDecision.block
        assert result.reason == reason

        data = result.to_json()
        assert data["decision"] == "block"
        assert data["reason"] == reason

    def test_subagent_stop_block(self):
        reason = "Subagent stopping"
        result = SubagentStopOutput.block(reason)
        assert isinstance(result, SubagentStopOutput)
        assert result.decision == SubagentStopDecision.block
        assert result.reason == reason

        data = result.to_json()
        assert data["decision"] == "block"
        assert data["reason"] == reason
