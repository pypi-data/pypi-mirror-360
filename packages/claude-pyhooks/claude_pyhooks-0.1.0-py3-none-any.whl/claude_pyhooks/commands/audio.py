"""
Audio command implementations for notifications and feedback.

This module provides commands for generating audio notifications across
different platforms (Windows, WSL, POSIX).
"""

import os
import platform
import sys
import time
from dataclasses import dataclass

from claude_pyhooks.commands.output_base import Command


def _make_beep(frequency: int, duration_ms: int) -> None:
    try:
        # WSL → Windows Console.Beep
        if os.getenv("WSL_DISTRO_NAME") or "microsoft" in platform.release().lower():
            os.system(f'powershell.exe -c "[console]::beep({frequency},{duration_ms})"')
        # Native Windows
        elif sys.platform.startswith("win"):
            import winsound

            winsound.Beep(frequency, duration_ms)  # type: ignore
        # POSIX systems
        else:
            sys.stdout.write("\a")
            sys.stdout.flush()
            time.sleep(duration_ms / 1000)
    except Exception:
        # Fallback using curses if available
        try:
            import curses

            curses.setupterm()
            curses.beep()
        except Exception:
            pass
        finally:
            time.sleep(duration_ms / 1000)


@dataclass(frozen=True, slots=True)
class BeepCommand(Command):
    """
    Command to generate a single beep sound.

    This command produces an audio beep with specified frequency and duration.
    It works across different platforms with appropriate fallbacks.

    Attributes:
        frequency: The frequency of the beep in Hz (default: 800).
        duration_ms: The duration of the beep in milliseconds (default: 300).
    """

    frequency: int = 800
    duration_ms: int = 300

    def execute(self) -> None:
        """Execute the beep command."""
        _make_beep(self.frequency, self.duration_ms)


@dataclass(frozen=True, slots=True)
class SleepCommand(Command):
    """
    Command to pause execution for a specified duration.

    This command introduces a delay, useful for timing between audio
    notifications or other operations.

    Attributes:
        duration_ms: The duration to sleep in milliseconds (default: 100).
    """

    duration_ms: int = 100

    def execute(self) -> None:
        """Execute the sleep command."""
        time.sleep(self.duration_ms / 1000)


@dataclass(frozen=True, slots=True)
class BeepSequence(Command):
    """
    Command to execute a sequence of beeps and pauses.

    This command allows creating complex audio patterns by combining
    BeepCommand and SleepCommand instances in a sequence.

    Attributes:
        commands: Tuple of BeepCommand and/or SleepCommand instances.

    Example:
        >>> melody = BeepSequence((
        ...     BeepCommand(800, 200),
        ...     SleepCommand(100),
        ...     BeepCommand(1000, 200),
        ... ))
        >>> melody.execute()
    """

    commands: tuple[BeepCommand | SleepCommand, ...]

    def __post_init__(self) -> None:
        """Validate that all commands are of the correct type."""
        if not all(
            isinstance(cmd, (BeepCommand, SleepCommand)) for cmd in self.commands
        ):
            raise TypeError(
                "BeepSequence only accepts BeepCommand and SleepCommand instances"
            )

    def execute(self) -> None:
        """Execute all commands in the sequence."""
        for command in self.commands:
            command.execute()


# Predefined common beep patterns
DEFAULT_BEEP = BeepCommand()
SUCCESS_BEEP = BeepSequence(
    (
        BeepCommand(800, 150),
        SleepCommand(20),
        BeepCommand(1000, 150),
    )
)
ERROR_BEEP = BeepSequence(
    (
        BeepCommand(1000, 150),
        BeepCommand(1000, 450),
    )
)
WARNING_BEEP = BeepSequence(
    (
        BeepCommand(900, 200),
        BeepCommand(900, 200),
        BeepCommand(900, 200),
    )
)
