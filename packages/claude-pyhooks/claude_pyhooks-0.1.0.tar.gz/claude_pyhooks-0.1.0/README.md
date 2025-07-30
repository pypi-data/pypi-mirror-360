# Claude PyHooks

A lightweight framework for implementing **Claude Code hooks** in Python.

---

## Overview

Claude PyHooks makes it easy to build and register custom hooks for Claude Code.  
The following hook types are supported:

| Hook type | Typical use cases |
|-----------|------------------|
| **PreToolUse** | Validate or block tool calls (e.g. dangerous shell commands) |
| **PostToolUse** | Post-processing after tool execution (logging, backups, notifications, …) |
| **Notification** | Handle general notifications emitted by Claude Code |
| **Stop** | Run cleanup logic when a session ends |
| **SubagentStop** | Run cleanup logic when a sub-agent terminates |

---

## Installation

```bash
pip install claude-pyhooks
# or, if you use uv
uv add claude-pyhooks
```

### Development version (recommended with uv)

```bash
git clone <this-repository>
cd claude-pyhooks
uv sync
uv pip install -e .
```

## Quick start
### PreToolUse — block a dangerous command
```python
#!/usr/bin/env python3
from claude_pyhooks import (
    PreToolUseInput,
    PreToolUseOutput,
    BashInput,
)

def main() -> None:
    hook_input = PreToolUseInput.from_stdin()

    if hook_input.tool_name == "Bash":
        assert isinstance(hook_input.tool_input, BashInput)
        command = (hook_input.tool_input.command or "").strip()

        if "rm -rf /" in command:
            PreToolUseOutput.block(
                f"Dangerous command blocked: {command}"
            ).execute()

if __name__ == "__main__":
    main()
```

### PostToolUse — log every Bash run
```python
#!/usr/bin/env python3
from claude_pyhooks import (
    PreToolUseInput,
    PreToolUseOutput,
    BashInput,
)

def main() -> None:
    hook_input = PreToolUseInput.from_stdin()

    if hook_input.tool_name == "Bash":
        assert isinstance(hook_input.tool_input, BashInput)
        command = (hook_input.tool_input.command or "").strip()

        if "rm -rf /" in command:
            PreToolUseOutput.block(
                f"Dangerous command blocked: {command}"
            ).execute()

if __name__ == "__main__":
    main()
```

### Notification — play a beep
```python
#!/usr/bin/env python3
from pathlib import Path
from claude_pyhooks import (
    PostToolUseInput,
    BashInput,
    BashResponse,
)

log_file = Path(__file__).with_name("bash_command_log.txt")

def main() -> None:
    hook_input = PostToolUseInput.from_stdin()

    if hook_input.tool_name == "Bash":
        assert isinstance(hook_input.tool_input, BashInput)
        assert isinstance(hook_input.tool_response, BashResponse)

        command = hook_input.tool_input.command
        success = not hook_input.tool_response.stderr
        status = "success" if success else "failure"

        with log_file.open("a") as f:
            f.write(f"{status}: {command}\n")

if __name__ == "__main__":
    main()
```

## Registering hooks with Claude Code
Add the hooks to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "uv run /path/to/pre_hook.py"
          }
        ]
      }
    ]
  }
}
```

## API highlights

### Input classes

| Class | Description |
|-------|-------------|
| `PreToolUseInput` | Data passed before a tool runs |
| `PostToolUseInput` | Data passed after a tool runs |
| `NotificationInput` | Generic notification payload |
| `StopInput` | Session-end payload |
| `SubagentStopInput` | Sub-agent end payload |

`tool_input` and `tool_response` are automatically parsed into strongly-typed objects such as `BashInput` or `BashResponse`.

### Output classes

| Class | Description |
|-------|-------------|
| `PreToolUseOutput` | Approve or block execution (`approve()`, `block()`) |
| `PostToolUseOutput` | Return post-processing commands |
| `StopOutput` | Commands on session end |
| `SubagentStopOutput` | Commands on sub-agent end |

Calling `.execute()` dispatches the command queue.  
If the output blocks execution, the process exits with code 2 automatically.

### Beep utilities

Pre-defined constants:

- `DEFAULT_BEEP`
- `SUCCESS_BEEP`
- `ERROR_BEEP`
- `WARNING_BEEP`

Each constant is an instance of `BeepCommand` and can be part of a `BeepSequence`.

---

## Examples

See the `examples/` directory for practical scripts:

| File | What it does |
|------|--------------|
| `pre_bash.py` | Blocks dangerous Bash commands |
| `post_bash.py` | Logs Bash command results |
| `notification_beep.py` | Plays beeps based on notification |

## License

MIT License