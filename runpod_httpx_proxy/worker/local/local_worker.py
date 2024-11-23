import typing
from starlette.applications import Starlette
from starlette.routing import Route
from collections import OrderedDict
from starlette.requests import Request

from runpod_httpx_proxy.types import JobDict, JobInput, StartConfigDict, Handler
from runpod_httpx_proxy.worker.local.local_job import LocalJob


class LocalWorker(typing.Generic[JobInput], Starlette):
    job_queue: OrderedDict[str, LocalJob[JobInput]]
    config: StartConfigDict[JobInput]

    def __init__(self, start_config_dict: StartConfigDict[JobInput]):
        super().__init__(
            routes=[
                Route("/runsync", self.runsync, methods=["POST"]),
                Route("/run", self.run, methods=["POST"]),
                Route("/stream/{job_id:str}", self.stream, methods=["GET", "POST"]),
                Route("/status/{job_id:str}", self.status, methods=["GET", "POST"]),
                Route("/cancel/{job_id:str}", self.cancel, methods=["POST"]),
                Route("/purge-queue", self.purge_queue, methods=["POST"]),
                Route("/health", self.health, methods=["GET"]),
            ]
        )
        self.config = start_config_dict
        self.job_queue = OrderedDict()

    def runsync(self, request: Request):
        job = LocalJob(self.config)
        self.job_queue.update({job.id: job})
        return job.id

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
