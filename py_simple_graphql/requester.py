from typing import Optional
import aiohttp

from core.errors import RequestError

class Request:
    
    @staticmethod
    async def post(url: str, json: Optional[dict] = None, headers: Optional[dict] = None):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json, headers=headers) as response:
                if response.status != 200:
                    raise RequestError(f"Request failed with status {response.status}")
                return await response.json()