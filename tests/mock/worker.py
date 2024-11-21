import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import runpod
import runpod_httpx_proxy
from sse_starlette.sse import EventSourceResponse
from runpod.serverless.modules.rp_fastapi import WorkerAPI


app = FastAPI()

MESSAGE = json.dumps({"message": "Hello, World!"})


@app.get("/stream")
async def stream():
    async def streamer():
        yield MESSAGE
        await asyncio.sleep(5)
        yield MESSAGE
        await asyncio.sleep(5)
        yield MESSAGE

    return StreamingResponse(
        streamer(),
        headers={"Transfer-Encoding": "chunked"},
    )


@app.get("/stream_sse")
async def stream_sse():
    async def event_publisher():
        for i in range(10):
            yield dict(data=i)
            await asyncio.sleep(0.2)

    return EventSourceResponse(event_publisher())


@app.get("/json")
async def json():
    return {"message": "Hello, World!"}


runpod.serverless.start(
    {
        "handler": runpod_httpx_proxy.handlers.AsyncHandler(app),
    }
)

# worker = WorkerAPI(
#     {
#         "handler": runpod_httpx_proxy.handlers.AsyncHandler(app),
#     }
# ).rp_app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(worker, host="localhost", port=8000)
