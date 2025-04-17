import httpx
import asyncio


async def call_until_success(url: str, max_retries: int = 10, delay: int = 2):
    attempt = 0
    async with httpx.AsyncClient() as client:
        while attempt < max_retries:
            try:
                response = await client.get(url)  # <- GET agora
                if response.status_code == 200:
                    return {"url": url, "status": 200, "attempts": attempt + 1}
                elif response.status_code == 400:
                    attempt += 1
                    await asyncio.sleep(delay)
                else:
                    return {
                        "url": url,
                        "status": response.status_code,
                        "detail": response.text,
                        "attempts": attempt + 1
                    }
            except httpx.HTTPStatusError as http_err:
                return {
                    "url": url,
                    "status": http_err.response.status_code,
                    "error": str(http_err),
                    "attempts": attempt + 1
                }
            except httpx.RequestError as e:
                return {
                    "url": url,
                    "error": str(e),
                    "attempts": attempt + 1
                }

        return {
            "url": url,
            "status": "failed after retries",
            "attempts": max_retries
        }
