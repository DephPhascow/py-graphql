from typing import Optional
import aiohttp
import ssl
from .errors import RequestError

class Request:
    
    @staticmethod
    async def post(url: str, json: Optional[dict] = None, headers: Optional[dict] = None, disable_ssl: bool = False):
        client_session_kwargs = {}
        if disable_ssl:
            sslcontext = ssl.create_default_context()
            sslcontext.check_hostname = False
            sslcontext.verify_mode = ssl.CERT_NONE
            client_session_kwargs['connector'] = aiohttp.TCPConnector(ssl=sslcontext)
        async with aiohttp.ClientSession(**client_session_kwargs) as session:
            async with session.post(url, json=json, headers=headers) as response:
                if response.status != 200:
                    raise RequestError(f"Request failed with status {response.status}")
                return await response.json()