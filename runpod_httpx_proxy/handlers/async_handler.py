from httpx._transports.asgi import _ASGIApp  # type: ignore i'm not sure why this is not exported by httpx
import httpx

from runpod_httpx_proxy.models import (
    RequestDict,
    ResponseDict,
    WorkerRequest,
)
from runpod_httpx_proxy.rest_utils import is_streaming_response
from runpod_httpx_proxy.types import JobDict, Handler


def async_handler(app: _ASGIApp) -> Handler:
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app))

    async def handle(job: JobDict[RequestDict]):
        serialized_request = job.get("input", None)
        if serialized_request is None:  # type: ignore
            yield ResponseDict(
                status_code=500,
                headers={},
                content="missing request input",
                request=serialized_request,
            )
        request = WorkerRequest.from_dict(serialized_request)
        response = await client.send(request, stream=True)
        stream = is_streaming_response(response)
        # yield the response collecting the content if we aren't streaming
        yield response_dict_from_response(
            response, content=(await response.aread()) if not stream else None
        )
        # if we are streaming yield the data from the stream
        if stream:
            async for data in response.iter_text():
                yield data
        # close the response
        await response.aclose()

    return handle
