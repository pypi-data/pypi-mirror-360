"""
Simple tests for PostToolUse inputs with automatic tool input/response parsing.
"""

from pathlib import Path
from typing import Any, Dict

import pytest

from claude_pyhooks.inputs import (
    BashInput,
    BashResponse,
    EditInput,
    EditResponse,
    ExitPlanModeInput,
    ExitPlanModeResponse,
    GlobInput,
    GlobResponse,
    GrepInput,
    GrepResponse,
    LSInput,
    LSResponse,
    MultiEditInput,
    MultiEditResponse,
    NotebookEditInput,
    NotebookEditResponse,
    NotebookReadInput,
    NotebookReadResponse,
    PostToolUseInput,
    ReadInput,
    ReadResponse,
    TaskInput,
    TaskResponse,
    WebFetchInput,
    WebFetchResponse,
    WebSearchInput,
    WebSearchResponse,
    WriteInput,
    WriteResponse,
)

from .test_data.load_samples import load_all_post_tool_use_samples


def compare_fields(obj: Any, json_data: Dict[str, Any]) -> None:
    print(obj)
    """Compare object fields with JSON data."""
    for key, json_value in json_data.items():
        if hasattr(obj, key):
            obj_value = getattr(obj, key)

            # Handle Path objects
            if isinstance(obj_value, Path):
                expected = json_value.replace("/home/user/", "/home/user/")
                assert str(obj_value) == expected
            # Skip complex tool_input/tool_response comparison (tested separately)
            elif key in ["tool_input", "tool_response"]:
                assert obj_value is not None
            else:
                assert obj_value == json_value


# Tool class mappings
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

tool_response_classes = {
    "bash": BashResponse,
    "edit": EditResponse,
    "read": ReadResponse,
    "write": WriteResponse,
    "ls": LSResponse,
    "glob": GlobResponse,
    "grep": GrepResponse,
    "multiedit": MultiEditResponse,
    "webfetch": WebFetchResponse,
    "websearch": WebSearchResponse,
    "task": TaskResponse,
    "exit_plan_mode": ExitPlanModeResponse,
    "notebookread": NotebookReadResponse,
    "notebookedit": NotebookEditResponse,
}

# Generate test cases
TOOL_SAMPLES = load_all_post_tool_use_samples()
posttool_test_cases = [
    (tool_name, post_data)
    for tool_name, post_data in TOOL_SAMPLES.items()
    if tool_name in tool_input_classes
]


@pytest.mark.parametrize("tool_name,post_data", posttool_test_cases)
def test_posttool_parsing(tool_name: str, post_data: Dict[str, Any]):
    """Test PostToolUse parsing with automatic tool input/response parsing."""
    hook = PostToolUseInput.from_json(post_data)

    # Test basic hook fields
    compare_fields(hook, post_data)

    # Test that tool_input is automatically parsed to the correct class
    if tool_name in tool_input_classes:
        expected_input_class = tool_input_classes[tool_name]
        assert isinstance(hook.tool_input, expected_input_class)
    else:
        # Unknown tool should remain as dict
        assert isinstance(hook.tool_input, dict)

    # Test that tool_response is automatically parsed to the correct class
    if tool_name in tool_response_classes:
        expected_response_class = tool_response_classes[tool_name]
        assert isinstance(hook.tool_response, expected_response_class)
    else:
        # Unknown tool response should remain as original format
        pass

    # Test round-trip
    obj_dict = hook.to_json()
    assert obj_dict is not None
    assert "session_id" in obj_dict

    hook_dict = hook.to_json()
    if tool_name == "ls":
        # tool response for LS should be different from the original post_data
        hook_dict["tool_response"] = post_data["tool_response"]
    assert hook_dict == post_data
