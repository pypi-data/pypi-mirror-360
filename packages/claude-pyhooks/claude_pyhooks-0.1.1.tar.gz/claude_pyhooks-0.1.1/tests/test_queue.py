"""Tests for queue module."""

from unittest.mock import patch

import pytest

from claude_pyhooks.commands.output_base import Command
from claude_pyhooks.commands.queue import CommandQueue


class MockCommand(Command):
    def __init__(self, name: str = "mock"):
        self.name = name
        self.executed = False

    def execute(self) -> None:
        self.executed = True


class TestCommandQueue:
    def test_default_empty_queue(self):
        queue = CommandQueue()
        assert queue.size() == 0
        assert queue.is_empty() is True
        assert queue.commands == []

    def test_add_single_command(self):
        queue = CommandQueue()
        command = MockCommand("test")

        queue.add(command)

        assert queue.size() == 1
        assert queue.is_empty() is False
        assert queue.commands[0] is command

    def test_add_multiple_commands_individually(self):
        queue = CommandQueue()
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")

        queue.add(cmd1)
        queue.add(cmd2)

        assert queue.size() == 2
        assert queue.commands[0] is cmd1
        assert queue.commands[1] is cmd2

    def test_add_list_of_commands(self):
        queue = CommandQueue()
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        cmd3 = MockCommand("cmd3")

        queue.add([cmd1, cmd2, cmd3])

        assert queue.size() == 3
        assert queue.commands[0] is cmd1
        assert queue.commands[1] is cmd2
        assert queue.commands[2] is cmd3

    def test_add_mixed_commands_and_lists(self):
        queue = CommandQueue()
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        cmd3 = MockCommand("cmd3")
        cmd4 = MockCommand("cmd4")

        queue.add(cmd1)
        queue.add([cmd2, cmd3])
        queue.add(cmd4)

        assert queue.size() == 4
        assert queue.commands[0] is cmd1
        assert queue.commands[1] is cmd2
        assert queue.commands[2] is cmd3
        assert queue.commands[3] is cmd4

    def test_add_invalid_command_raises_error(self):
        queue = CommandQueue()

        with pytest.raises(TypeError, match="Command must be an instance of Command"):
            queue.add("not a command")

    def test_add_list_with_invalid_command_raises_error(self):
        queue = CommandQueue()
        cmd = MockCommand("valid")

        with pytest.raises(TypeError, match="Command must be an instance of Command"):
            queue.add([cmd, "invalid"])

    def test_execute_empty_queue(self):
        queue = CommandQueue()
        queue.execute()  # Should not raise any errors

    def test_execute_single_command(self):
        queue = CommandQueue()
        command = MockCommand("test")
        queue.add(command)

        queue.execute()

        assert command.executed is True

    def test_execute_multiple_commands_in_order(self):
        queue = CommandQueue()
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")
        cmd3 = MockCommand("cmd3")

        queue.add([cmd1, cmd2, cmd3])

        queue.execute()

        assert cmd1.executed is True
        assert cmd2.executed is True
        assert cmd3.executed is True

    def test_execute_calls_commands_in_correct_order(self):
        queue = CommandQueue()
        execution_order = []

        class OrderedCommand(Command):
            def __init__(self, name: str):
                self.name = name

            def execute(self) -> None:
                execution_order.append(self.name)

        cmd1 = OrderedCommand("first")
        cmd2 = OrderedCommand("second")
        cmd3 = OrderedCommand("third")

        queue.add([cmd1, cmd2, cmd3])
        queue.execute()

        assert execution_order == ["first", "second", "third"]

    def test_execute_and_exit_calls_execute_then_exits(self):
        queue = CommandQueue()
        command = MockCommand("test")
        queue.add(command)

        with patch("claude_pyhooks.commands.queue.sys.exit") as mock_exit:
            queue.execute_and_exit(42)

        assert command.executed is True
        mock_exit.assert_called_once_with(42)

    def test_execute_and_exit_default_exit_code(self):
        queue = CommandQueue()

        with patch("claude_pyhooks.commands.queue.sys.exit") as mock_exit:
            queue.execute_and_exit()

        mock_exit.assert_called_once_with(0)

    def test_execute_and_exit_with_empty_queue(self):
        queue = CommandQueue()

        with patch("claude_pyhooks.commands.queue.sys.exit") as mock_exit:
            queue.execute_and_exit(1)

        mock_exit.assert_called_once_with(1)

    def test_size_updates_correctly(self):
        queue = CommandQueue()
        assert queue.size() == 0

        queue.add(MockCommand("cmd1"))
        assert queue.size() == 1

        queue.add([MockCommand("cmd2"), MockCommand("cmd3")])
        assert queue.size() == 3

    def test_is_empty_updates_correctly(self):
        queue = CommandQueue()
        assert queue.is_empty() is True

        queue.add(MockCommand("cmd1"))
        assert queue.is_empty() is False

    def test_commands_list_is_preserved(self):
        queue = CommandQueue()
        cmd1 = MockCommand("cmd1")
        cmd2 = MockCommand("cmd2")

        queue.add(cmd1)
        queue.add(cmd2)

        # Direct access to commands list
        assert len(queue.commands) == 2
        assert queue.commands[0] is cmd1
        assert queue.commands[1] is cmd2

    def test_command_execution_with_exception_propagates(self):
        queue = CommandQueue()

        class FailingCommand(Command):
            def execute(self) -> None:
                raise RuntimeError("Command failed")

        queue.add(FailingCommand())

        with pytest.raises(RuntimeError, match="Command failed"):
            queue.execute()

    def test_partial_execution_on_exception(self):
        queue = CommandQueue()
        cmd1 = MockCommand("cmd1")

        class FailingCommand(Command):
            def execute(self) -> None:
                raise RuntimeError("Command failed")

        cmd3 = MockCommand("cmd3")

        queue.add([cmd1, FailingCommand(), cmd3])

        with pytest.raises(RuntimeError):
            queue.execute()

        # First command should have executed
        assert cmd1.executed is True
        # Third command should not have executed
        assert cmd3.executed is False
