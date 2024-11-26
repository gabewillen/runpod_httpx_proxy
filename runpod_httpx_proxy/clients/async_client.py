import httpx
import typing
from urllib.parse import urljoin
from runpod_httpx_proxy.utils import stream_type_from_headers
from runpod_httpx_proxy.models import (
    StreamResponse,
    RunRequest,
)

from runpod_httpx_proxy.types import JSON

P = typing.ParamSpec("P")


class AsyncClient(httpx.AsyncClient):
    async def send_run_request(
        self,
        request: RunRequest,
        stream: bool = False,
        *args: typing.Any,
        **kwargs: typing.Any,
    ):
        run_response = await super().send(
            request,
            *args,
            **kwargs,
        )
        if run_response.status_code != 200:
            return run_response
        job = run_response.json()
        stream_request = self.build_request(method="POST", url=f"stream/{job['id']}")

        async def wait_for_output() -> (
            typing.Tuple[httpx.Response, dict[str, typing.Any]]
        ):
            stream_response = await super(AsyncClient, self).send(stream_request)
            while stream_response.status_code == 200:
                stream_response_content = stream_response.json()
                if stream_response_content.get("status") == "IN_QUEUE":
                    stream_response = await super(AsyncClient, self).send(
                        stream_request
                    )
                    continue
                output = [
                    item["output"] for item in stream_response_content.pop("stream")
                ]
                return stream_response, {**stream_response_content, "output": output}
            return stream_response, {"output": [None]}

        stream_response, stream_response_content = await wait_for_output()

        if stream_response.status_code != 200:
            return stream_response
        stream_response_dict = stream_response_content["output"].pop(0)
        if stream_response_dict is None:
            raise Exception("No output in stream response")
        stream_response_is_streaming = stream_type_from_headers(stream_response_dict)
        if not stream_response_is_streaming:
            return StreamResponse.from_response_dict(stream_response_dict)

        async def stream_output(stream_response_content: dict[str, typing.Any]):
            while stream_response_content["status"] == "IN_PROGRESS":
                for output in stream_response_content["output"]:
                    yield output.encode("utf-8")
                stream_response, stream_response_content = await wait_for_output()
                if stream_response.status_code != 200:
                    raise Exception(stream_response.text)
            if stream_response_content["status"] == "FAILED":
                raise Exception(stream_response_content["error"])

        del stream_response_dict["content"]
        return httpx.Response(
            **stream_response_dict,
            content=stream_output(stream_response_content),
        )

    async def send(
        self,
        request: httpx.Request,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> httpx.Response:
        if str(request.url).startswith(str(self.base_url)):
            request_stream_type = stream_type_from_headers(request.headers)
            # TODO: handle streaming requests
            if request_stream_type in ("text/event-stream", "application/x-ndjson"):
                pass
            request = RunRequest.from_request(request)
            return await self.send_run_request(request, *args, **kwargs)

        return await super().send(request, *args, **kwargs)
