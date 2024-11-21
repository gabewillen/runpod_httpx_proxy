import os
import types
import typing
from httpx._transports.asgi import _ASGIApp
import httpx

from runpod_httpx_proxy.models import Job, ResponseDict, WorkerRequest, is_streaming


P = typing.ParamSpec("P")


def async_handler(app: _ASGIApp):
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app))

    async def handle(job: Job):
        serialized_request = job.get("input", None)
        if serialized_request is None:
            yield ResponseDict(
                status_code=500,
                headers={},
                content="missing request input",
                request=serialized_request,
            )
        request = WorkerRequest.from_dict(serialized_request)
        response = await client.send(request, stream=True)
        stream = is_streaming(response)
        # yield the response collecting the content if we aren't streaming
        yield ResponseDict.from_request(
            response, content=(await response.aread()) if not stream else None
        )
        # if we are streaming yield the data from the stream
        if stream:
            async for data in response.iter_text():
                yield data
        # close the response
        await response.aclose()

    return handle
