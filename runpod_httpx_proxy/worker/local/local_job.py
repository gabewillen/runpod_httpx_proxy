from uuid_extensions import uuid7str  # type: ignore
from uuid import UUID
from runpod_httpx_proxy.types import JobInput, StartConfigDict
import typing


class LocalJob(typing.Generic[JobInput]):
    config: StartConfigDict[JobInput]
    id: str
    output: typing.Union[
        str, typing.Generator[str, None, None], typing.AsyncGenerator[str, None]
    ]

    def __init__(self, config: StartConfigDict[JobInput]):
        self.config = config
        self.id = uuid7str()
