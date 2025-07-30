"""Tests for output_base module."""

from io import StringIO
from unittest.mock import patch

import pytest

from claude_pyhooks.commands.output_base import Command, HookOutput


class TestCommand:
    def test_execute_not_implemented(self):
        command = Command()
        with pytest.raises(NotImplementedError):
            command.execute()


class MockHookOutput(HookOutput):
    """Mock implementation for testing."""

    pass


class TestHookOutput:
    def test_default_values(self):
        output = MockHookOutput()
        assert output.is_continue is None
        assert output.stopReason is None
        assert output.suppressOutput is None
        assert output._exit_code is None

    def test_create_with_values(self):
        output = MockHookOutput.create(
            is_continue=True, stopReason="test reason", suppressOutput=False
        )
        assert output.is_continue is True
        assert output.stopReason == "test reason"
        assert output.suppressOutput is False

    def test_create_filters_none_values(self):
        output = MockHookOutput.create(
            is_continue=True, stopReason=None, suppressOutput=False
        )
        assert output.is_continue is True
        assert output.stopReason is None
        assert output.suppressOutput is False

    def test_to_json_basic(self):
        output = MockHookOutput(
            is_continue=True, stopReason="test", suppressOutput=False
        )
        data = output.to_json()
        assert data["continue"] is True
        assert data["stopReason"] == "test"
        assert data["suppressOutput"] is False

    def test_to_json_excludes_none_values(self):
        output = MockHookOutput(is_continue=True)
        data = output.to_json()
        assert data["continue"] is True
        assert "stopReason" not in data
        assert "suppressOutput" not in data

    def test_execute_prints_json(self):
        output = MockHookOutput(is_continue=True)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            output.execute()

        printed = mock_stdout.getvalue().strip()
        assert "'continue': True" in printed

    def test_execute_with_exit_code(self):
        output = MockHookOutput(is_continue=True)
        output._exit_code = 1

        with patch("sys.stdout", new_callable=StringIO):
            with pytest.raises(SystemExit) as exc_info:
                output.execute()

        assert exc_info.value.code == 1

    def test_execute_without_exit_code(self):
        output = MockHookOutput(is_continue=True)

        with patch("sys.stdout", new_callable=StringIO):
            output.execute()  # Should not raise SystemExit

    def test_pre_execute_called(self):
        output = MockHookOutput()
        pre_execute_called = False

        def mock_pre_execute():
            nonlocal pre_execute_called
            pre_execute_called = True

        output._pre_execute = mock_pre_execute

        with patch("sys.stdout", new_callable=StringIO):
            output.execute()

        assert pre_execute_called

    def test_dict_name_mapping(self):
        assert "is_continue" in MockHookOutput.DICT_NAME_MAPPING
        assert MockHookOutput.DICT_NAME_MAPPING["is_continue"] == "continue"
