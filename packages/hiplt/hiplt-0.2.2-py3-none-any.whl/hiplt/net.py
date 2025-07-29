# hiplt/net.py

import aiohttp
import asyncio
import logging
import async_timeout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def request(method, url, *, params=None, data=None, json=None, headers=None, timeout=10, retries=3, return_response=False):
    attempt = 0
    while attempt < retries:
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(timeout):
                    async with session.request(method, url, params=params, data=data, json=json, headers=headers) as response:
                        response.raise_for_status()
                        if return_response:
                            return response
                        return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"{method} запрос к {url} не удался: {e}. Попытка {attempt + 1} из {retries}")
            attempt += 1
            await asyncio.sleep(1)
    return None

# Удобные обёртки для GET и POST

async def get(url, **kwargs):
    return await request("GET", url, **kwargs)

async def post(url, **kwargs):
    return await request("POST", url, **kwargs)


# Пример использования

async def main():
    url = "https://httpbin.org/get"
    response = await get(url, return_response=True)
    if response:
        print("Status:", response.status)
        text = await response.text()
        print("Content:", text[:100])
    else:
        print("GET запрос не удался.")

if __name__ == "__main__":
    asyncio.run(main())