from http import HTTPStatus
from unittest.mock import MagicMock

import httpx
import pytest
from nornir.core.task import Result, Task

from nornir_jsonrpc.tasks import (
    jsonrpc_cli,
    jsonrpc_delete_config,
    jsonrpc_get,
    jsonrpc_replace_config,
    jsonrpc_set,
    jsonrpc_update_config,
)
from nornir_jsonrpc.types import Action, SetCommand, GetCommand


@pytest.fixture
def nornir_task() -> Task:
    """Create a mock Nornir task."""
    task = MagicMock(spec=Task)
    task.host = MagicMock()
    task.nornir = MagicMock()

    mock_response = httpx.Response(
        HTTPStatus.OK,
        json={
            "id": 0,
            "jsonrpc": "2.0",
            "result": [{"basic system info": {"version": "v23.10.1"}}],
        },
        request=httpx.Request("POST", "https://testhost:443/jsonrpc"),
    )

    mock_connection = MagicMock()
    mock_connection.post.return_value = mock_response
    task.host.get_connection.return_value = mock_connection

    return task


def test_jsonrpc_cli(nornir_task: Task) -> None:
    """Test the jsonrpc_cli task."""
    result = jsonrpc_cli(nornir_task, cmds=["show version"])
    assert isinstance(result, Result)
    assert result.result == [{"basic system info": {"version": "v23.10.1"}}]


def test_jsonrpc_get(nornir_task: Task) -> None:
    """Test the jsonrpc_get task."""
    result = jsonrpc_get(nornir_task, paths=["/system/information/version"])
    assert isinstance(result, Result)
    assert result.result == [{"basic system info": {"version": "v23.10.1"}}]


def test_jsonrpc_get_mixed(nornir_task: Task) -> None:
    """Test the jsonrpc_get task with mixed paths."""
    import json

    result = jsonrpc_get(
        nornir_task,
        paths=[
            "/system/information/version",
            GetCommand(path="/system/information/model-name"),
        ],
    )
    assert isinstance(result, Result)
    assert result.result == [{"basic system info": {"version": "v23.10.1"}}]

    mock_connection = nornir_task.host.get_connection.return_value
    mock_connection.post.assert_called_once()

    # Get the content passed to post
    _, kwargs = mock_connection.post.call_args
    request_payload = json.loads(kwargs["content"])

    # Assert payload structure and content, ignoring the dynamic 'id'
    assert request_payload["jsonrpc"] == "2.0"
    assert request_payload["method"] == "get"
    expected_commands = [
        {"path": "/system/information/version", "datastore": "running"},
        {"path": "/system/information/model-name", "datastore": "running"},
    ]
    assert request_payload["params"]["commands"] == expected_commands


def test_jsonrpc_set(nornir_task: Task) -> None:
    """Test the jsonrpc_set task."""
    result = jsonrpc_set(
        nornir_task,
        cmds=[
            SetCommand(
                action=Action.UPDATE,
                path="/interface[name=mgmt0]",
                value={"description": "set-via-json-rpc"},
            )
        ],
    )
    assert isinstance(result, Result)
    assert result.result == [{"basic system info": {"version": "v23.10.1"}}]


def test_jsonrpc_update_config(nornir_task: Task) -> None:
    """Test the jsonrpc_update_config task."""
    result = jsonrpc_update_config(
        nornir_task, path="/interface[name=mgmt0]/description:set-via-json-rpc"
    )
    assert isinstance(result, Result)
    assert result.result == [{"basic system info": {"version": "v23.10.1"}}]


def test_jsonrpc_replace_config(nornir_task: Task) -> None:
    """Test the jsonrpc_replace_config task."""
    result = jsonrpc_replace_config(
        nornir_task, path="/interface[name=mgmt0]/description:replaced-via-json-rpc"
    )
    assert isinstance(result, Result)
    assert result.result == [{"basic system info": {"version": "v23.10.1"}}]


def test_jsonrpc_delete_config(nornir_task: Task) -> None:
    """Test the jsonrpc_delete_config task."""
    result = jsonrpc_delete_config(
        nornir_task, path="/interface[name=mgmt0]/description"
    )
    assert isinstance(result, Result)
    assert result.result == [{"basic system info": {"version": "v23.10.1"}}]
