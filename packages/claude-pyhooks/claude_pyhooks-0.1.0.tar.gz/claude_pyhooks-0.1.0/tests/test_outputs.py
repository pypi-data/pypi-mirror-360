"""Tests for outputs module."""

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


class TestDecisionEnums:
    def test_pre_tool_use_decision_values(self):
        assert PreToolUseDecision.approve.to_json() == "approve"
        assert PreToolUseDecision.block.to_json() == "block"

    def test_post_tool_use_decision_values(self):
        assert PostToolUseDecision.block.to_json() == "block"

    def test_stop_decision_values(self):
        assert StopDecision.block.to_json() == "block"


class TestPreToolUse:
    def test_default_values(self):
        output = PreToolUseOutput()
        assert output.decision is None
        assert output.reason is None
        assert output._exit_code is None

    def test_with_approve_decision(self):
        output = PreToolUseOutput(decision=PreToolUseDecision.approve)
        assert output.decision == PreToolUseDecision.approve
        assert output._exit_code is None

    def test_with_block_decision(self):
        output = PreToolUseOutput(decision=PreToolUseDecision.block, reason="test")
        assert output.decision == PreToolUseDecision.block
        assert output.reason == "test"

    def test_pre_execute_sets_exit_code_for_block(self):
        output = PreToolUseOutput(decision=PreToolUseDecision.block)
        output._pre_execute()
        assert output._exit_code == 2

    def test_pre_execute_no_exit_code_for_approve(self):
        output = PreToolUseOutput(decision=PreToolUseDecision.approve)
        output._pre_execute()
        assert output._exit_code is None

    def test_to_json_with_decision(self):
        output = PreToolUseOutput(decision=PreToolUseDecision.approve)
        data = output.to_json()
        assert data["decision"] == "approve"

    def test_to_json_with_reason(self):
        output = PreToolUseOutput(
            decision=PreToolUseDecision.block, reason="Not allowed"
        )
        data = output.to_json()
        assert data["decision"] == "block"
        assert data["reason"] == "Not allowed"


class TestPostToolUse:
    def test_default_values(self):
        output = PostToolUseOutput()
        assert output.decision is None
        assert output.reason is None
        assert output._exit_code is None

    def test_with_block_decision(self):
        output = PostToolUseOutput(decision=PostToolUseDecision.block, reason="test")
        assert output.decision == PostToolUseDecision.block
        assert output.reason == "test"

    def test_pre_execute_sets_exit_code_for_block(self):
        output = PostToolUseOutput(decision=PostToolUseDecision.block)
        output._pre_execute()
        assert output._exit_code == 2

    def test_to_json_with_decision(self):
        output = PostToolUseOutput(decision=PostToolUseDecision.block)
        data = output.to_json()
        assert data["decision"] == "block"


class TestStop:
    def test_default_values(self):
        output = StopOutput()
        assert output.decision is None
        assert output.reason is None
        assert output._exit_code is None

    def test_with_block_decision(self):
        output = StopOutput(decision=StopDecision.block, reason="test")
        assert output.decision == StopDecision.block
        assert output.reason == "test"

    def test_pre_execute_sets_exit_code_for_block(self):
        output = StopOutput(decision=StopDecision.block)
        output._pre_execute()
        assert output._exit_code == 2

    def test_to_json_with_decision(self):
        output = StopOutput(decision=StopDecision.block)
        data = output.to_json()
        assert data["decision"] == "block"


class TestSubagentStop:
    def test_default_values(self):
        output = SubagentStopOutput()
        assert output.decision is None
        assert output.reason is None
        assert output._exit_code is None

    def test_with_block_decision(self):
        output = SubagentStopOutput(decision=SubagentStopDecision.block, reason="test")
        assert output.decision == SubagentStopDecision.block
        assert output.reason == "test"

    def test_pre_execute_sets_exit_code_for_block(self):
        output = SubagentStopOutput(decision=SubagentStopDecision.block)
        output._pre_execute()
        assert output._exit_code == 2

    def test_to_json_with_decision(self):
        output = SubagentStopOutput(decision=SubagentStopDecision.block)
        data = output.to_json()
        assert data["decision"] == "block"


class TestIntegration:
    def test_create_method_works_for_all_outputs(self):
        pre_tool = PreToolUseOutput.create(decision=PreToolUseDecision.approve)
        assert isinstance(pre_tool, PreToolUseOutput)

        post_tool = PostToolUseOutput.create(decision=PostToolUseDecision.block)
        assert isinstance(post_tool, PostToolUseOutput)

        stop = StopOutput.create(decision=StopDecision.block)
        assert isinstance(stop, StopOutput)

        subagent_stop = SubagentStopOutput.create(decision=StopDecision.block)
        assert isinstance(subagent_stop, SubagentStopOutput)
