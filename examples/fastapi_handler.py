import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import runpod
import runpod_httpx_proxy
import json

app = FastAPI()

MESSAGE = json.dumps({"message": "Hello, World!"})


@app.get("/stream")
async def stream():
    async def streamer():
        yield MESSAGE
        await asyncio.sleep(1)
        yield MESSAGE
        await asyncio.sleep(1)
        yield MESSAGE

    return StreamingResponse(
        streamer(),
    )


@app.get("/json")
async def json():
    return {"message": "Hello, World!"}


runpod.serverless.start(
    {
        "handler": runpod_httpx_proxy.handlers.AsyncHandler(app),
    }
)

if __name__ == "__main__":
    import os

    async def main():
        client = runpod_httpx_proxy.clients.AsyncClient(
            base_url=f"https://api.runpod.ai/v2/{os.getenv("RUNPOD_ENDPOINT_ID")}",
        )
        response = await client.get("/stream")
        print(response)

    asyncio.run(main())
