"""
Simple tests for hook inputs (Notification, Stop, SubagentStop).
"""

from pathlib import Path
from typing import Any, Dict, Type

import pytest

from claude_pyhooks.inputs import NotificationInput, StopInput, SubagentStopInput

from .test_data.load_samples import (
    load_notification_sample,
    load_stop_sample,
    load_subagent_stop_sample,
)


def compare_fields(obj: Any, json_data: Dict[str, Any]) -> None:
    """Compare object fields with JSON data."""
    for key, json_value in json_data.items():
        if hasattr(obj, key):
            obj_value = getattr(obj, key)

            # Handle Path objects
            if isinstance(obj_value, Path):
                expected = json_value.replace("/home/user/", "/home/user/")
                assert str(obj_value) == expected
            else:
                assert obj_value == json_value


# Generate test cases
hook_test_cases = [
    ("Notification", NotificationInput, load_notification_sample()),
    ("Stop", StopInput, load_stop_sample()),
    ("SubagentStop", SubagentStopInput, load_subagent_stop_sample()),
]


@pytest.mark.parametrize("hook_name,hook_class,json_data", hook_test_cases)
def test_hook_parsing(hook_name: str, hook_class: Type, json_data: Dict[str, Any]):
    """Test hook input parsing and field comparison."""
    parsed = hook_class.from_json(json_data)
    compare_fields(parsed, json_data)

    # Test round-trip
    obj_dict = parsed.to_json()
    assert obj_dict is not None
    assert "session_id" in obj_dict
