import asyncio
import httpx
from httpx_sse import aconnect_sse
import runpod_httpx_proxy
import unittest


class TestAsyncClient(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = runpod_httpx_proxy.clients.AsyncClient(
            base_url="https://api.runpod.ai/v2/svh9xg0m4r37k4",
            headers={
                "Authorization": "Bearer EVC5KDSRUMT86BTKMXVSWJZGBZ3ENH5S4XAPNI3M"
            },
            timeout=60,
        )

    async def post_json(self):
        response = await self.client.post("/json", json={"message": "Hello, World!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, World!"})

    async def test_post_ndjson(self):
        async def ndjson_generator():
            for i in range(3):
                yield f'{{"data": {i}}}\n'.encode("utf-8")
                await asyncio.sleep(0.1)

        response = await self.client.post("/ndjson", content=ndjson_generator())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"data": i} for i in range(3)])

    async def test_get_json(self):
        response = await self.client.get("/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, World!"})

    async def test_get_stream_ndjson(self):
        async with self.client.stream("GET", "/stream_ndjson") as response:
            i = 0
            async for json in response.aiter_text():
                self.assertEqual(json, f'{{"data": {i}}}')
                i += 1

    async def test_get_stream_sse(self):
        async with aconnect_sse(self.client, "GET", "/stream_sse") as response:
            i = 0
            async for event in response.aiter_sse():
                self.assertEqual(event.data, f"{i}")
                i += 1


if __name__ == "__main__":
    unittest.main()
