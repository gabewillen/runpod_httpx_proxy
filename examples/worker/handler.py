from fastapi.responses import JSONResponse
from httpx import Request
from runpod_httpx_proxy.handlers.async_handler import async_handler
import runpod
from starlette.applications import Starlette
from starlette.routing import Route


async def get_json(request: Request):
    return JSONResponse({"message": "Hello, World!"})


async def get_stream(request: Request):
    for i in range(10):
        yield {"data": i}


app = Starlette(
    routes=[
        Route("/json", get_json, methods=["GET"]),
        Route("/stream", get_stream, methods=["GET"]),
    ]
)

if __name__ == "__main__":
    runpod.serverless.start({"handler": async_handler(app)})
