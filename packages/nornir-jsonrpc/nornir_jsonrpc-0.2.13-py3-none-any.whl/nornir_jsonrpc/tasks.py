from nornir.core.task import Result, Task
from nornir_jsonrpc.connection import CONNECTION_NAME
from nornir_jsonrpc.types import (
    RPCBaseModel,
    Response,
    CLIRPC,
    CLIParams,
    GetCommand,
    GetParams,
    GetRPC,
    SetCommand,
    SetParams,
    SetRPC,
    Action,
)
from typing import Iterable, Union, Any
from pydantic import BaseModel
import itertools

_req_id_counter = itertools.count()
Value = dict[str, Any]


def jsonify(v: BaseModel) -> Value:
    """Create Python struct that can be JSON serialized."""
    return v.model_dump(exclude_none=True, exclude_unset=True, by_alias=True)


def _send_rpc(request: RPCBaseModel, task: Task) -> Result:
    device = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
    response = device.post(
        content=request.model_dump_json(exclude_none=True),
    )
    response.raise_for_status()
    reply = Response(**response.json())
    if reply.error:
        return Result(host=task.host, result=reply.error)

    assert reply.result
    return Result(host=task.host, result=reply.result)


def jsonrpc_cli(task: Task, cmds: list[str]) -> Result:
    """
    Runs a list of commands on the device.

    Args:
        task: The Nornir task.
        cmds: A list of commands to run.

    Returns:
        A Nornir Result object.
    """
    return _send_rpc(
        request=CLIRPC(id=next(_req_id_counter), params=CLIParams(commands=cmds)), task=task
    )


def jsonrpc_get(task: Task, paths: Iterable[Union[str, GetCommand]]) -> Result:
    """
    Retrierieves data from the device.

    Args:
        task: The Nornir task.
        paths: An iterable of paths or GetCommand objects.

    Returns:
        A Nornir Result object.
    """
    cmds = [p if isinstance(p, GetCommand) else GetCommand(path=p) for p in paths]
    return _send_rpc(
        request=GetRPC(id=next(_req_id_counter), params=GetParams(commands=cmds)), task=task
    )


def jsonrpc_set(task: Task, cmds: Iterable[SetCommand]) -> Result:
    """
    Sets data on the device.

    Args:
        task: The Nornir task.
        cmds: An iterable of SetCommand objects.

    Returns:
        A Nornir Result object.
    """
    return _send_rpc(
        request=SetRPC(id=next(_req_id_counter), params=SetParams(commands=cmds)), task=task
    )


def jsonrpc_update_config(
    task: Task, path: str, value: BaseModel | None = None
) -> Result:
    """
    Updates the configuration at a specific path.

    Args:
        task: The Nornir task.
        path: The path to update.
        value: The value to update the path with.

    Returns:
        A Nornir Result object.
    """
    cmd = SetCommand(
        action=Action.UPDATE,
        path=path,
    )
    if value:
        cmd.value = jsonify(v=value)
    return _send_rpc(
        request=SetRPC(id=next(_req_id_counter), params=SetParams(commands=[cmd])), task=task
    )


def jsonrpc_replace_config(
    task: Task, path: str, value: BaseModel | None = None
) -> Result:
    """
    Replaces the configuration at a specific path.

    Args:
        task: The Nornir task.
        path: The path to replace.
        value: The value to replace the path with.

    Returns:
        A Nornir Result object.
    """
    cmd = SetCommand(
        action=Action.REPLACE,
        path=path,
    )
    if value:
        cmd.value = jsonify(v=value)
    return _send_rpc(
        request=SetRPC(id=next(_req_id_counter), params=SetParams(commands=[cmd])), task=task
    )


def jsonrpc_delete_config(
    task: Task, path: str, value: BaseModel | None = None
) -> Result:
    """
    Deletes the configuration at a specific path.

    Args:
        task: The Nornir task.
        path: The path to delete.
        value: The value to delete at the path.

    Returns:
        A Nornir Result object.
    """
    cmd = SetCommand(
        action=Action.DELETE,
        path=path,
    )
    if value:
        cmd.value = jsonify(v=value)
    return _send_rpc(
        request=SetRPC(id=next(_req_id_counter), params=SetParams(commands=[cmd])), task=task
    )
