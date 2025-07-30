#!/usr/bin/env python3
"""Log bash command results."""

from pathlib import Path

from claude_pyhooks import BashInput, BashResponse, PostToolUseInput

current_dir = Path(__file__).parent.resolve()


def main():
    hook_input = PostToolUseInput.from_stdin()

    if hook_input.tool_name == "Bash":
        assert isinstance(hook_input.tool_input, BashInput)
        assert isinstance(hook_input.tool_response, BashResponse)
        command = hook_input.tool_input.command
        success = not hook_input.tool_response.stderr

        status = "success" if success else "failure"
        with open(current_dir / "bash_command_log.txt", "a") as log_file:
            log_file.write(f"{status}: {command}\n")


if __name__ == "__main__":
    main()
