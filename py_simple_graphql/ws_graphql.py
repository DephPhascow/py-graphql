import json
from .query import Query
from .query_str_builder import QueryStrBuilder
import ssl
import websockets
from strenum import StrEnum
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from .enums import QueryType

class WSReceiveMessageType(StrEnum):
    DATA = "data"
    COMPLETE = "complete"
    ERROR = "error"
    

@dataclass
class WSReceiveMessage:
    type: WSReceiveMessageType
    id: str
    payload: Optional[Any] = None
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = WSReceiveMessageType(self.type)

@dataclass
class WSGraphQL:
    ws_url: str
    enable_traceback: bool = False
    ws: websockets.WebSocketClientProtocol = None
    headers: dict = field(default_factory=dict)
    
    async def __aenter__(self):
        sslcontext = ssl.create_default_context()
        sslcontext.check_hostname = False
        sslcontext.verify_mode = ssl.CERT_NONE
        self.ws = await websockets.connect(self.ws_url, ssl=sslcontext, subprotocols=["graphql-ws"])
        return self
    
    async def execute(self, query: Query, vars: dict = None, headers: Optional[dict] = None,funct: Callable = None):
        if self.ws is None:
            raise Exception("WebSocket is not connected")
        if self.ws.closed:
            raise Exception("WebSocket is closed")
        if query.query_type != QueryType.SUBSCRIPTION:
            raise Exception("Only subscriptions queries are allowed")
        query_str = QueryStrBuilder([query]).builder(f'{query.id}')
        request = json.dumps({
            "id": query.id,
            "type": "start",
            "payload": {
                "query": query_str,
                "variables": vars
            }
        })
        await self.ws.send(request)
        while True:
            res = json.loads(await self.ws.recv())
            response = WSReceiveMessage(**res)
            if funct:
                funct(response)
            if response.type == WSReceiveMessageType.COMPLETE:
                break
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.ws:
            await self.ws.close()