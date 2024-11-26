from httpx import Request
from sse_starlette import EventSourceResponse
from runpod_httpx_proxy.handlers.async_handler import async_handler
import runpod
import asyncio
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route
import json


async def get_json(request: Request):
    return JSONResponse({"message": "Hello, World!"})


async def get_stream_ndjson(request: Request):
    async def stream():
        for i in range(10):
            yield f"{json.dumps({'data': i})}\n"
            await asyncio.sleep(1)

    return StreamingResponse(stream(), media_type="application/x-ndjson")


async def get_stream_sse(request: Request):
    async def sse():
        for i in range(10):
            yield {"data": i}
            await asyncio.sleep(1)

    return EventSourceResponse(sse())


app = Starlette(
    routes=[
        Route("/json", get_json, methods=["GET"]),
        Route("/stream_ndjson", get_stream_ndjson, methods=["GET"]),
        Route("/stream_sse", get_stream_sse, methods=["GET"]),
    ]
)

if __name__ == "__main__":
    runpod.serverless.start(
        {"handler": async_handler(app), "return_aggregate_stream": True}
    )
