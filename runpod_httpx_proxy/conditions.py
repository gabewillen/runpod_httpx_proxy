import httpx
import types
import inspect
from runpod_httpx_proxy.models import ResponseDict
from runpod_httpx_proxy.types import Handler, JobInput


def is_content_type_event_stream(headers: dict[str, str]) -> bool:
    content_type = headers.get("content-type", "").lower()
    return "text/event-stream" in content_type


def is_connection_keep_alive(headers: dict[str, str]) -> bool:
    connection = headers.get("connection", "").lower()
    return "keep-alive" in connection


def is_chunked_transfer_encoding(headers: dict[str, str]) -> bool:
    transfer_encoding = headers.get("transfer-encoding", "").lower()
    return "chunked" in transfer_encoding


def is_content_type_multipart(headers: dict[str, str]) -> bool:
    content_type = headers.get("content-type", "").lower()
    return "multipart/" in content_type


def is_content_length_missing(headers: dict[str, str]) -> bool:
    return headers.get("content-length") is None


def is_streaming_response(response: httpx.Response | ResponseDict) -> bool:
    headers = (
        {**response.headers}
        if isinstance(response, httpx.Response)
        else response["headers"]
    )
    return (
        is_content_type_event_stream(headers)
        or is_chunked_transfer_encoding(headers)
        or is_content_type_multipart(headers)
        or (
            is_connection_keep_alive(headers) and not is_content_length_missing(headers)
        )
    )


def is_generator(handler: Handler[JobInput]) -> int:
    if inspect.isgeneratorfunction(handler):
        return 0b10
    elif inspect.isasyncgenfunction(handler):
        return 0b11
    return 0


def is_coroutine(handler: Handler[JobInput]) -> int:
    return int(inspect.iscoroutinefunction(handler))
