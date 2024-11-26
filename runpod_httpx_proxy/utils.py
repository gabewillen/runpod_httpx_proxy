import typing
import httpx
import inspect
from runpod_httpx_proxy.types import Handler, JobInput


def is_content_type_event_stream(headers: dict[str, str]) -> typing.Optional[str]:
    content_type = headers.get("content-type", "").lower()
    return "text/event-stream" if "text/event-stream" in content_type else None


def is_content_type_ndjson(headers: dict[str, str]) -> typing.Optional[str]:
    content_type = headers.get("content-type", "").lower()
    return "application/x-ndjson" if "application/x-ndjson" in content_type else None


def is_connection_keep_alive(headers: dict[str, str]) -> typing.Optional[str]:
    connection = headers.get("connection", "").lower()
    return "keep-alive" if "keep-alive" in connection else None


def is_chunked_transfer_encoding(headers: dict[str, str]) -> typing.Optional[str]:
    transfer_encoding = headers.get("transfer-encoding", "").lower()
    return "chunked" if "chunked" in transfer_encoding else None


def is_content_type_multipart(headers: dict[str, str]) -> typing.Optional[str]:
    content_type = headers.get("content-type", "").lower()
    return content_type if "multipart/" in content_type else None


def is_content_length_missing(headers: dict[str, str]) -> bool:
    return headers.get("content-length") is None


def stream_type_from_headers(
    headers: httpx.Headers | dict[str, str]
) -> typing.Optional[str]:
    headers = {**headers} if isinstance(headers, httpx.Headers) else headers
    return (
        is_content_type_event_stream(headers)
        or is_chunked_transfer_encoding(headers)
        or is_content_type_multipart(headers)
        or is_content_type_ndjson(headers)
        or (
            is_connection_keep_alive(headers)
            if not is_content_length_missing(headers)
            else None
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
