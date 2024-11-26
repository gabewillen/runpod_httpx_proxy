from typing import AsyncGenerator
import typing
from httpx._transports.asgi import _ASGIApp  # type: ignore i'm not sure why this is not exported by httpx
import httpx


from runpod_httpx_proxy.models import (
    RequestDict,
    ResponseDict,
    request_from_request_dict,
    response_dict_from_response,
)
from runpod import RunPodLogger
from runpod_httpx_proxy.utils import stream_type_from_headers
from runpod_httpx_proxy.types import JobDict


logger = RunPodLogger()


def async_handler(app: _ASGIApp):
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app))

    async def handle(
        job: JobDict[RequestDict],
    ) -> AsyncGenerator[typing.Union[ResponseDict, str], None]:
        request_dict = job.get("input", None)
        logger.info(f"request_dict: {request_dict}")  # type: ignore
        if request_dict is None:  # type: ignore
            yield ResponseDict(
                status_code=500,
                headers={},
                content="missing request input",
                request=request_dict,
            )
        request_stream_type = stream_type_from_headers(request_dict["headers"])
        logger.info(f"request_stream_type: {request_stream_type}")  # type: ignore

        request = request_from_request_dict(request_dict)

        # we attempt to stream the response
        response = await client.send(request, stream=True)
        response_stream_type = stream_type_from_headers(response.headers)
        # yield the response collecting the content if this is not a streaming response
        yield response_dict_from_response(
            response,
            content=(
                (await response.aread()).decode() if not response_stream_type else None
            ),
        )
        # if we are streaming yield the data from the stream
        if response_stream_type in ("text/event-stream", "application/x-ndjson"):
            async for data in response.aiter_lines():
                yield data
        elif response_stream_type is not None:
            async for data in response.aiter_raw(1024 * 1024):  # 1MB chunks
                yield data.decode("utf-8")
        # close the response
        await response.aclose()

    return handle
