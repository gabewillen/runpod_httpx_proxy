from runpod_httpx_proxy.conditions import is_generator, is_coroutine
from uuid_extensions import uuid7str  # type: ignore
from runpod_httpx_proxy.types import (
    JSON,
    AsyncGeneratorOutput,
    CoroutineJobOutput,
    GeneratorOutput,
    Handler,
    JobDict,
    JobInput,
    JobOutputDict,
    JobType,
    SyncFunctionOutput,
)
import typing


def job_type_from_handler(handler: Handler[JobInput]) -> JobType:
    return JobType(is_generator(handler) | is_coroutine(handler))


class LocalJob(typing.Generic[JobInput]):
    handler: Handler[JobInput]
    id: str
    type: JobType
    output: JSON
    stream: typing.List[JobOutputDict]

    def __init__(self, handler: Handler[JobInput]):
        self.handler = handler
        self.id = uuid7str()
        self.type = job_type_from_handler(self.handler)
        self.output = []

    async def run(self, input: JobDict[JobInput]) -> JSON:
        if self.type == JobType.SYNC_FUNCTION:
            self.output = typing.cast(SyncFunctionOutput, self.handler(input))
        elif self.type == JobType.ASYNC_FUNCTION:
            self.output = await typing.cast(CoroutineJobOutput, self.handler(input))
        elif self.type == JobType.SYNC_GENERATOR:
            self.output = []
            for output in typing.cast(GeneratorOutput, self.handler(input)):
                self.output.append(output)
        elif self.type == JobType.ASYNC_GENERATOR:
            self.output = []
            async for output in typing.cast(AsyncGeneratorOutput, self.handler(input)):
                self.output.append(output)
        return self.output
