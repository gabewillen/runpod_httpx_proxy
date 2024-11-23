from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse


async def runsync():
    return JSONResponse({"message": "Hello, World!"})


async def run():
    return JSONResponse({"message": "Hello, World!"})


async def stream(job_id: str):
    return JSONResponse({"message": f"Hello, World! {job_id}"})


core = Starlette(
    routes=[
        Route("/runsync", runsync),
        Route("/run", run),
        Route("/stream/{job_id:str}", stream),
    ]
)


class Worker(Starlette):
    def __init__(self):
        super().__init__(
            routes=[
                Route("/runsync", runsync),
                Route("/run", run),
                Route("/stream/{job_id:str}", stream),
            ]
        )

    def runsync(self):
        
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
