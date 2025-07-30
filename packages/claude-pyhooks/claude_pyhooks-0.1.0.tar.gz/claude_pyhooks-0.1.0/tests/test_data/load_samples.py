"""
Utility functions to load sample data from JSON files.
"""

import json
from pathlib import Path
from typing import Any, Dict

_sample_inputs_dir = Path(__file__).parent / "sample_hook_inputs"

_tool_names = [
    "bash",
    "edit",
    "read",
    "write",
    "ls",
    "glob",
    "grep",
    "multiedit",
    "webfetch",
    "websearch",
    "task",
    "exit_plan_mode",
    "notebookread",
    "notebookedit",
]


def load_json_sample(filename: str) -> Dict[str, Any]:
    filepath = _sample_inputs_dir / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Sample file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_pre_tool_use_sample(tool_name: str) -> Dict[str, Any]:
    return load_json_sample(f"PreToolUse-{tool_name.lower()}.json")


def load_post_tool_use_sample(tool_name: str) -> Dict[str, Any]:
    return load_json_sample(f"PostToolUse-{tool_name.lower()}.json")


def load_notification_sample() -> Dict[str, Any]:
    return load_json_sample("Notification.json")


def load_stop_sample() -> Dict[str, Any]:
    return load_json_sample("Stop.json")


def load_subagent_stop_sample() -> Dict[str, Any]:
    return load_json_sample("SubagentStop.json")


def load_all_pre_tool_use_samples() -> Dict[str, Dict[str, Any]]:
    """Load all PreToolUse samples for all tools."""
    samples = {}
    for tool in _tool_names:
        try:
            samples[tool] = load_pre_tool_use_sample(tool)
        except FileNotFoundError:
            print(f"Warning: Sample file for {tool} not found.")
    return samples


def load_all_post_tool_use_samples() -> Dict[str, Dict[str, Any]]:
    """Load all PostToolUse samples for all tools."""
    samples = {}
    for tool in _tool_names:
        try:
            samples[tool] = load_post_tool_use_sample(tool)
        except FileNotFoundError:
            print(f"Warning: Sample file for {tool} not found.")
    return samples
