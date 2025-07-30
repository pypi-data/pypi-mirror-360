"""
Simple tests for PreToolUse inputs with automatic tool input parsing.
"""

from pathlib import Path
from typing import Any, Dict

import pytest

from claude_pyhooks.inputs import (
    BashInput,
    EditInput,
    ExitPlanModeInput,
    GlobInput,
    GrepInput,
    LSInput,
    MultiEditInput,
    NotebookEditInput,
    NotebookReadInput,
    PreToolUseInput,
    ReadInput,
    TaskInput,
    WebFetchInput,
    WebSearchInput,
    WriteInput,
)

from .test_data.load_samples import load_all_pre_tool_use_samples


def compare_fields(obj: Any, json_data: Dict[str, Any]) -> None:
    """Compare object fields with JSON data."""
    for key, json_value in json_data.items():
        if hasattr(obj, key):
            obj_value = getattr(obj, key)

            # Handle Path objects
            if isinstance(obj_value, Path):
                expected = json_value.replace("/home/user/", "/home/user/")
                assert str(obj_value) == expected
            # Skip complex tool_input comparison (tested separately)
            elif key == "tool_input":
                assert obj_value is not None
            else:
                assert obj_value == json_value


# Tool input class mapping
tool_input_classes = {
    "bash": BashInput,
    "edit": EditInput,
    "read": ReadInput,
    "write": WriteInput,
    "ls": LSInput,
    "glob": GlobInput,
    "grep": GrepInput,
    "multiedit": MultiEditInput,
    "webfetch": WebFetchInput,
    "websearch": WebSearchInput,
    "task": TaskInput,
    "exit_plan_mode": ExitPlanModeInput,
    "notebookread": NotebookReadInput,
    "notebookedit": NotebookEditInput,
}

# Generate test cases
pretool_test_cases = [
    (tool_name, pre_data)
    for tool_name, pre_data in load_all_pre_tool_use_samples().items()
    if tool_name in tool_input_classes
]


@pytest.mark.parametrize("tool_name,pre_data", pretool_test_cases)
def test_pretool_parsing(tool_name: str, pre_data: Dict[str, Any]):
    """Test PreToolUse parsing with automatic tool input parsing."""
    hook = PreToolUseInput.from_json(pre_data)

    # Test basic hook fields
    compare_fields(hook, pre_data)

    # Test that tool_input is automatically parsed to the correct class
    if tool_name in tool_input_classes:
        expected_class = tool_input_classes[tool_name]
        assert isinstance(hook.tool_input, expected_class)
    else:
        # Unknown tool should remain as dict
        assert isinstance(hook.tool_input, dict)

    # Test round-trip
    obj_dict = hook.to_json()
    assert obj_dict is not None
    assert "session_id" in obj_dict

    # Test round-trip conversion
    assert hook.to_json() == pre_data
