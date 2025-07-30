#!/usr/bin/env python3
"""Play notification beeps based on message content."""

from claude_pyhooks import (
    DEFAULT_BEEP,
    ERROR_BEEP,
    SUCCESS_BEEP,
    WARNING_BEEP,
    NotificationInput,
)


def main():
    hook_input = NotificationInput.from_stdin()

    # Default beep
    beep = DEFAULT_BEEP

    # Choose beep based on message content
    if hook_input.message:
        message_lower = hook_input.message.lower()

        if "error" in message_lower or "fail" in message_lower:
            beep = ERROR_BEEP
        elif "success" in message_lower or "complete" in message_lower:
            beep = SUCCESS_BEEP
        elif "warning" in message_lower or "permission" in message_lower:
            beep = WARNING_BEEP

    beep.execute()


if __name__ == "__main__":
    main()
