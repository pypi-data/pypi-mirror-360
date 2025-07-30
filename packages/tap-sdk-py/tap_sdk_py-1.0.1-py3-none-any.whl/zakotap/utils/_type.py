from typing import TypedDict, NotRequired, Literal


class ClientData(TypedDict):
    name: str
    token: str
    zakoEndpoint: NotRequired[str]


class HelloData(TypedDict):
    name: str
    token: str


class HelloResponse(TypedDict):
    ok: bool
    version: str
    message: str


class AudioRequest(TypedDict):
    id: str
    ping: bool
    data: str
    parameters: dict[str, str]


class ErrorMessage(TypedDict):
    message: str


class VersionType(TypedDict):
    Major: int
    Minor: int
    Patch: int


EmitterEvents = Literal["ready", "audio", "error", "warn", "close"]
