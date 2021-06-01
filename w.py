from armada_agent.utils.request import LOOP, async_req

import asyncio

urls = [
    "https://google.com",
    "https://youtube.com"
]

headers = {
    'Content-Type': 'application/json'
}

methods = ["GET", "GET"]

params = [None] * 2

data = [{}] * 2

future = asyncio.ensure_future(async_req(urls, methods, headers, params, data), loop=LOOP)
LOOP.run_until_complete(future)

result = future.result()

print(list(map(lambda response: response.status, result)))