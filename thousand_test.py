import random

import aiohttp
import asyncio


async def fetch(url, session):
    async with session.post(url, json={"userId": random.randint(1, 5), "city": random.choice(
            ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])}) as response:
        return response.status


async def main():
    url = "http://localhost:5000/update_balance"
    tasks = []

    # Set up an aiohttp session
    async with aiohttp.ClientSession() as session:
        for _ in range(1000):  # 1000 requests
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # Check and count successful responses (HTTP 200)
        success_count = sum(1 for response in responses if response == 200)

        print(f"Total requests: {len(tasks)}")
        print(f"Successful requests: {success_count}")
        print(f"Failed requests: {len(tasks) - success_count}")


# Run the main function in the asyncio event loop
asyncio.run(main())
