import typing
from urllib.parse import urljoin
import httpx
import re


try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class RequestDict(TypedDict):
    method: str
    url: str
    headers: dict[str, str]
    content: typing.NotRequired[typing.Any]


class PartialRequestDict(typing.TypedDict, total=False):
    method: str
    url: str
    headers: dict[str, str]
    content: typing.NotRequired[typing.Any]


def request_dict_from_request(
    request: httpx.Request,
    /,
    **request_dict_overrides: typing.Unpack[PartialRequestDict],
) -> RequestDict:
    request_dict_overrides.setdefault("method", request.method)
    request_dict_overrides.setdefault("url", str(request.url))
    request_dict_overrides.setdefault("headers", dict(request.headers))
    if "content" not in request_dict_overrides:
        request_dict_overrides["content"] = (
            request.content.decode() if request.content else None
        )
    return RequestDict(**request_dict_overrides)


class ResponseDict(typing.TypedDict):
    status_code: int
    headers: dict[str, str]
    content: typing.NotRequired[typing.Any]
    request: RequestDict


class PartialResponseDict(typing.TypedDict, total=False):
    status_code: int
    headers: dict[str, str]
    content: typing.NotRequired[typing.Any]
    request: RequestDict


def response_dict_from_response(
    response: httpx.Response,
    /,
    **response_dict_overrides: typing.Unpack[PartialResponseDict],
) -> ResponseDict:
    response_dict_overrides.setdefault(
        "request", request_dict_from_request(response.request)
    )
    response_dict_overrides.setdefault("status_code", response.status_code)
    response_dict_overrides.setdefault("headers", dict(response.headers))
    if "content" not in response_dict_overrides:
        response_dict_overrides["content"] = response.content
    return ResponseDict(**response_dict_overrides)


class JobDict(typing.TypedDict):
    id: typing.NotRequired[str]
    input: RequestDict


def job_dict_from_request(
    request: httpx.Request, **overrides: typing.Unpack[RequestDict]
) -> JobDict:
    return JobDict(input=request_dict_from_request(request, **overrides))


def request_from_request_dict(request_dict: RequestDict) -> httpx.Request:
    return httpx.Request(
        method=request_dict["method"],
        url=request_dict["url"],
        headers=request_dict.get("headers", {}),
        content=request_dict.get("content", None),
    )


def response_from_response_dict(response_dict: ResponseDict) -> httpx.Response:
    return httpx.Response(
        status_code=response_dict["status_code"],
        headers=response_dict.get("headers", {}),
        content=response_dict.get("content", None),
    )


STREAMABLE_CONTENT_TYPES = ["text/event-stream", "multipart/"]
STREAMING_CONNECTIONS = ["keep-alive"]
STREAMING_TRANSFER_ENCODINGS = ["chunked"]
STREAMING_CONTENT_LENGTHS = [None, "0"]


StreamStatus = typing.Literal["IN_PROGRESS", "COMPLETED"]


class StreamResponseDict(typing.TypedDict):
    status: StreamStatus
    stream: tuple[ResponseDict]


class StreamResponse(httpx.Response):
    @classmethod
    def from_response_dict(
        cls,
        response_dict: ResponseDict,
        **kwargs: dict[str, typing.Any],
    ) -> "StreamResponse":
        return cls(
            status_code=response_dict["status_code"],
            headers=response_dict.get("headers", {}),
            content=kwargs.get("content", response_dict.get("content", None)),
            request=request_from_request_dict(response_dict.get("request")),
        )


RUNPOD_ENDPOINT_PATTERN = re.compile(
    r"/?(?P<version>v\d+)/(?P<endpoint_id>[a-zA-Z0-9]+)(?P<path>/.*?)/?$"
)


class RunRequest(httpx.Request):
    @classmethod
    def from_request(
        cls, request: httpx.Request, **override: typing.Unpack[PartialRequestDict]
    ) -> "RunRequest":
        print("RUN REQUEST", request.url, request.headers)
        url = httpx.URL(override.pop("url", str(request.url)))
        match = RUNPOD_ENDPOINT_PATTERN.match(request.url.path)
        if match is not None:
            version, endpoint_id, path = match.groups()
            base_url = f"{url.scheme}://{url.host}/{version}/{endpoint_id}"
        else:
            base_url = ""
            path = request.url.path
        content = request.content.decode() if request.content else None
        return cls(
            method="POST",
            url=f"{base_url}/run",
            headers=override.get("headers", request.headers),
            json={
                "input": request_dict_from_request(
                    request, url=urljoin(base_url, path), content=content
                ),
            },
        )
