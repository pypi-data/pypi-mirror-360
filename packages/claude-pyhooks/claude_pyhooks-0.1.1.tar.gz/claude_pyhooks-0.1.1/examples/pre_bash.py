#!/usr/bin/env python3
"""Block dangerous bash commands before execution."""

from claude_pyhooks import BashInput, PreToolUseInput, PreToolUseOutput

DANGEROUS_COMMANDS = [
    "rm -rf /",
    "sudo rm",
    "mkfs",
    "format",
    "dd if=/dev/zero",
]


def main():
    hook_input = PreToolUseInput.from_stdin()

    if hook_input.tool_name == "Bash":
        assert isinstance(hook_input.tool_input, BashInput)
        command = hook_input.tool_input.command
        if command is None:
            return
        command = command.strip()

        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in command:
                PreToolUseOutput.block(
                    f"Dangerous command blocked: {dangerous}"
                ).execute()
                return


if __name__ == "__main__":
    main()
