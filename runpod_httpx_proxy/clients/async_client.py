import httpx
import typing
from urllib.parse import urljoin
from runpod_httpx_proxy.models import (
    StreamResponse,
    RunRequest,
)

P = typing.ParamSpec("P")


class AsyncClient(httpx.AsyncClient):
    def build_stream_request(self, job_id: str) -> httpx.Response:
        return httpx.Request(
            method="POST",
            url=self.base_url.join(f"/stream/{job_id}"),
        )

    async def send_stream_request(self, request: httpx.Request) -> httpx.Response:
        return await super().send(request)

    async def send_run_request(
        self,
        request: RunRequest,
        stream: bool = False,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> httpx.Request:
        print("WorkerRunRequest", request.url, request.content)
        run_response = await super().send(
            request,
            stream=stream,
            *args,
            **kwargs,
        )
        if run_response.status_code != 200:
            return run_response
        job = run_response.json()
        # send a request to the stream endpoint even if the client is not streaming

        stream_response = await self.send_stream_request(
            self.build_stream_request(job["id"])
        )
        print("STREAM RESPONSE", stream_response)
        # if the stream endpoint returns an error, return the error
        if stream_response.status_code != 200:
            return stream_response

        stream_response_content = stream_response.json()
        print("STREAM RESPONSE CONTENT", stream_response_content)
        stream_response_dict = stream_response_content.get("stream", [{}])[0]
        if stream_response_content.get("status") == "COMPLETED":
            return StreamResponse.from_dict(stream_response_dict)

        async def stream():
            next_response = await self.send_stream_request(job["id"])
            if next_response.status_code != 200:
                raise Exception(next_response.text)
            next_response_content = next_response.json()
            print("NEXT RESPONSE CONTENT", next_response_content)
            if next_response_content.get("status") != "COMPLETED":
                yield next_response_content

        return StreamResponse.from_dict(stream_response_dict, content=stream())

    async def send(
        self,
        request: httpx.Request,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> httpx.Response:
        if str(request.url).startswith(str(self.base_url)):
            request = RunRequest.from_request(request)
            return await self.send_run_request(request, *args, **kwargs)

        return await super().send(request, *args, **kwargs)
