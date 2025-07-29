from enum import StrEnum, auto
from typing import Any, Iterable, Literal
from pydantic import BaseModel, Field, model_validator


class Action(StrEnum):
    REPLACE = auto()
    UPDATE = auto()
    DELETE = auto()


class Datastore(StrEnum):
    CANDIDATE = auto()
    RUNNING = auto()
    STATE = auto()
    TOOLS = auto()


class Method(StrEnum):
    GET = auto()
    SET = auto()
    VALIDATE = auto()
    CLI = auto()
    DIFF = auto()


class GetCommand(BaseModel):
    path: str
    datastore: Datastore = Datastore.RUNNING


class SetCommand(BaseModel):
    action: Action
    path: str
    value: Any | None = None


class GetParams(BaseModel):
    commands: list[GetCommand]


class SetParams(BaseModel):
    commands: Iterable[SetCommand]
    confirm_timeout: int | None = Field(gt=0, default=None)
    output_format: Literal["text"] | None = None


class CLIFormats(StrEnum):
    JSON = auto()
    TEXT = auto()
    TABLE = auto()


class CLIParams(BaseModel):
    commands: Iterable[str]
    output_format: CLIFormats = CLIFormats.JSON


class RPCBaseModel(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int


class GetRPC(RPCBaseModel):
    """JSON RPC for the "get" method"""

    method: Method = Method.GET
    params: GetParams


class SetRPC(RPCBaseModel):
    """JSON RPC for the "set" method"""

    method: Method = Method.SET
    params: SetParams


class CLIRPC(RPCBaseModel):
    """JSON RPC for the "cli" method"""

    method: Method = Method.CLI
    params: CLIParams


Result = list[dict[str, Any]]


class Error(BaseModel):
    code: int
    message: str


class Response(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int
    result: Result | None = None
    error: Error | None = None

    @model_validator(mode="after")
    def result_or_error(self) -> "Response":
        assert self.result or self.error
        return self
