import httpx
import types

from runpod_httpx_proxy.types import Handler, JobInput


def is_content_type_event_stream(response: httpx.Response) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    return "text/event-stream" in content_type


def is_connection_keep_alive(response: httpx.Response) -> bool:
    connection = response.headers.get("connection", "").lower()
    return "keep-alive" in connection


def is_chunked_transfer_encoding(response: httpx.Response) -> bool:
    transfer_encoding = response.headers.get("transfer-encoding", "").lower()
    return "chunked" in transfer_encoding


def is_content_type_multipart(response: httpx.Response) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    return "multipart/" in content_type


def is_content_length_missing(response: httpx.Response) -> bool:
    return response.headers.get("content-length") is None


def is_streaming_response(response: httpx.Response) -> bool:
    return (
        is_content_type_event_stream(response)
        or is_chunked_transfer_encoding(response)
        or is_content_type_multipart(response)
        or (
            is_connection_keep_alive(response)
            and not is_content_length_missing(response)
        )
    )


def is_generator(handler: Handler[JobInput]) -> bool:
    return isinstance(handler, (types.GeneratorType, types.AsyncGeneratorType))
