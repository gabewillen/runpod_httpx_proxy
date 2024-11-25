import asyncio
import httpx
from httpx_sse import aconnect_sse
import pytest
import runpod_httpx_proxy


class TestAsyncClient:
    client: runpod_httpx_proxy.clients.AsyncClient = (
        runpod_httpx_proxy.clients.AsyncClient(
            base_url="https://api.runpod.ai/v2/svh9xg0m4r37k4",
            headers={
                "Authorization": "Bearer EVC5KDSRUMT86BTKMXVSWJZGBZ3ENH5S4XAPNI3M"
            },
            timeout=60,
        )
    )

    # client = httpx.AsyncClient(
    #     base_url="http://localhost:8000", transport=httpx.ASGITransport(app)
    # )

    # @pytest.mark.asyncio
    # async def test_get_json(self):
    #     response = await self.client.get("/json")
    #     print("RESPONSE", response)
    #     assert response.status_code == 200
    #     assert response.json() == {"message": "Hello, World!"}

    # @pytest.mark.asyncio
    # async def test_stream_sse(self):
    #     async with aconnect_sse(self.client, "GET", "/stream_sse") as response:
    #         async for event in response.aiter_sse():
    #             assert event.data == "Hello, World!"

    @pytest.mark.asyncio
    async def test_stream_json(self):
        async with self.client.stream("GET", "/stream") as response:
            async for json in response.aiter_text():
                print("JSON", json)


# async def main():
#     client = runpod_httpx_proxy.clients.AsyncClient(
#         base_url="https://api.runpod.ai/v2/your-pod-id",
#         headers={"Authorization": "Bearer YOUR_API_KEY"},
#     )
#     # note you can fetch here and optionally pass any additional headers if necessary
#     response = await client.get("/json")
#     # or stream server sent events
#     async with aconnect_sse(client, "GET", "/stream_sse") as event_source:
#         for sse in event_source.iter_sse():
#             print(sse.event, sse.data, sse.id, sse.retry)

#     # or stream a response
#     async with client.stream("/stream") as response:
#         async for chunk in response.iter_bytes():
#             print(chunk)


# if __name__ == "__main__":
#     asyncio.run(main())
