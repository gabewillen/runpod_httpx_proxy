import typing
from starlette.applications import Starlette
from starlette.routing import Route
from collections import OrderedDict
from starlette.requests import Request
import asyncio
from runpod_httpx_proxy.types import (
    JSON,
    ConcurrencyModifier,
    Handler,
    JobInput,
    StartConfigDict,
)
from runpod_httpx_proxy.worker.local.local_job import LocalJob


class LocalWorker(typing.Generic[JobInput], Starlette):
    job_queue: OrderedDict[str, asyncio.Task[JSON]]
    concurrency_modifier: ConcurrencyModifier
    config: StartConfigDict[JobInput]
    handler: Handler[JobInput]

    def __init__(self, start_config_dict: StartConfigDict[JobInput]):
        super().__init__(
            routes=[
                Route("/runsync", self.run_sync, methods=["POST"]),
                Route("/run", self.run, methods=["POST"]),
                Route("/stream/{job_id:str}", self.stream, methods=["GET", "POST"]),
                Route("/status/{job_id:str}", self.status, methods=["GET", "POST"]),
                Route("/cancel/{job_id:str}", self.cancel, methods=["POST"]),
                Route("/purge-queue", self.purge_queue, methods=["POST"]),
                Route("/health", self.health, methods=["GET"]),
            ]
        )
        self.config = start_config_dict
        self.handler = start_config_dict["handler"]
        self.concurrency_modifier = start_config_dict.get(
            "concurrency_modifier", lambda concurrency: concurrency
        )
        self.job_queue = OrderedDict()

    async def run_sync(self, request: Request):
        await self.wait_for_concurrency()
        job = LocalJob(self.handler)
        task = asyncio.create_task(
            job.run(input=await request.json()),
            name=job.id,
        )
        await task

    async def run(self):
        pass

    async def stream(self, job_id: str):
        pass

    async def status(self, job_id: str):
        pass

    async def cancel(self, job_id: str):
        pass

    async def purge_queue(self):
        pass

    async def health(self):
        pass

    async def wait_for_concurrency(self):
        async def check_concurrency():
            while not self.concurrency_modifier(len(self.job_queue)) > 0:
                await asyncio.sleep(0)

        await asyncio.wait_for(check_concurrency(), timeout=1)
