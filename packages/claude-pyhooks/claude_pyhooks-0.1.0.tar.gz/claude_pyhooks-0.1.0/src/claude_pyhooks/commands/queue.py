"""
Command queue implementation for batch command execution.
"""

import sys
from dataclasses import dataclass, field

from claude_pyhooks.commands.output_base import Command


@dataclass
class CommandQueue(Command):
    commands: list[Command] = field(default_factory=list)

    def add(self, command: Command | list[Command]) -> None:
        if isinstance(command, list):
            for cmd in command:
                self.add(cmd)
        else:
            if not isinstance(command, Command):
                raise TypeError(
                    "Command must be an instance of Command or a list of Commands"
                )
            self.commands.append(command)

    def size(self) -> int:
        return len(self.commands)

    def is_empty(self) -> bool:
        return len(self.commands) == 0

    def execute(self) -> None:
        """Execute all commands in the queue in order."""
        for command in self.commands:
            command.execute()

    def execute_and_exit(self, exit_code: int = 0) -> None:
        self.execute()
        sys.exit(exit_code)
