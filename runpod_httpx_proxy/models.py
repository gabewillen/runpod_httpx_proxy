import typing
from urllib.parse import urljoin
import httpx
from dataclasses import dataclass, asdict
import re


class RequestDict(typing.TypedDict):
    method: str
    url: str
    headers: dict[str, str]
    content: typing.Optional[typing.Any]

    @classmethod
    def from_request(
        cls, request: httpx.Request, **overrides: typing.Unpack["RequestDict"]
    ) -> "RequestDict":
        input = cls(
            method=overrides.pop("method", request.method),
            url=overrides.pop("url", str(request.url)),
            headers=overrides.pop("headers", {**request.headers}),
        )
        content = overrides.pop("content", request.content)
        if content is not None:
            input["content"] = content
        return input


class ResponseDict(typing.TypedDict):
    status_code: int
    headers: dict[str, str]
    content: typing.Optional[typing.Any]
    request: RequestDict

    @classmethod
    def from_request(
        cls, response: httpx.Response, **overrides: typing.Unpack["ResponseDict"]
    ) -> "ResponseDict":
        return cls(
            status_code=overrides.pop("status_code", response.status_code),
            headers={**overrides.pop("headers", response.headers)},
            content=overrides.pop("content", response.content),
        )


class Job(typing.TypedDict):
    input: RequestDict

    @classmethod
    def from_request(
        cls, request: httpx.Request, **overrides: typing.Unpack[RequestDict]
    ) -> "Job":
        return cls(input=RequestDict.from_request(request, **overrides))


class WorkerRequest(httpx.Request):

    @classmethod
    def from_dict(cls, dict: RequestDict) -> "WorkerRequest":
        return cls(
            method=dict["method"],
            url=dict["url"],
            headers=dict.get("headers", {}),
            content=dict.get("content", None),
        )

    @classmethod
    def from_request(
        cls, request: httpx.Request, **overrides: typing.Unpack["RequestDict"]
    ) -> "WorkerRequest":
        return cls(
            method=overrides.pop("method", request.method),
            url=overrides.pop("url", str(request.url)),
            headers=overrides.pop("headers", request.headers),
            content=overrides.pop("content", request.content),
        )

    def to_dict(self) -> RequestDict:
        return RequestDict.from_request(self)


STREAMABLE_CONTENT_TYPES = ["text/event-stream", "multipart/"]
STREAMING_CONNECTIONS = ["keep-alive"]
STREAMING_TRANSFER_ENCODINGS = ["chunked"]
STREAMING_CONTENT_LENGTHS = [None, "0"]


def is_streaming(self) -> bool:
    content_type = self.headers.get("content-type", "").lower()
    return (
        # Check for streamable content types
        any(
            streamable_content_type in content_type
            for streamable_content_type in STREAMABLE_CONTENT_TYPES
        )
        # Check for connection header indicating a persistent connection
        or self.headers.get("connection", "").lower() in STREAMING_CONNECTIONS
        # If content length is not specified or is zero, assume it could be streaming
        or self.headers.get("content-length") in STREAMING_CONTENT_LENGTHS
        # Check for chunked transfer encoding
        or self.headers.get("transfer-encoding", "").lower()
        in STREAMING_TRANSFER_ENCODINGS
        # Check for file download indicator, common in streamed downloads
        or "attachment" in self.headers.get("content-disposition", "").lower()
        # Check for range requests, which may indicate partial, streamable content
        or self.headers.get("accept-ranges", "").lower() == "bytes"
    )


StreamStatus = typing.Literal["IN_PROGRESS", "COMPLETED"]


class StreamResponseDict(typing.TypedDict):
    status: StreamStatus
    stream: tuple[ResponseDict]


class StreamResponse(httpx.Response):

    # @classmethod
    # def from_response(
    #     cls, response: httpx.Response, **override: typing.Unpack["ResponseDict"]
    # ) -> "WorkerResponse":
    #     return cls(
    #         status_code=override.pop("status_code", response.status_code),
    #         headers=override.pop("headers", response.headers),
    #         content=override.pop("content", response.content),
    #         request=override.pop("request", response.request),
    #     )

    @classmethod
    def from_dict(
        cls, dict: ResponseDict, **overrides: typing.Unpack["ResponseDict"]
    ) -> "StreamResponse":
        return cls(
            status_code=overrides.pop("status_code", dict["status_code"]),
            headers=overrides.pop("headers", dict["headers"]),
            content=overrides.pop("content", dict["content"]),
            request=overrides.pop("request", dict["request"]),
        )


RUNPOD_ENDPOINT_PATTERN = re.compile(
    r"/?(?P<version>v\d+)/(?P<endpoint_id>\d+)(?P<path>/.*?)/?$"
)


class RunRequest(httpx.Request):

    @classmethod
    def from_request(
        cls, request: httpx.Request, **override: typing.Unpack["RequestDict"]
    ) -> "RunRequest":
        url = httpx.URL(override.pop("url", str(request.url)))
        base_url = f"{url.scheme}://{url.host}"
        match = RUNPOD_ENDPOINT_PATTERN.match(request.url.path)
        if match is not None:
            _, _, path = match.groups()
        else:
            path = request.url.path
        content = request.content.decode() if request.content else None
        return cls(
            method="POST",
            url=urljoin(base_url, "/run"),
            headers=override.get("headers", {}),
            json={
                "input": RequestDict.from_request(
                    request, url=urljoin(base_url, path), content=content
                ),
            },
        )
