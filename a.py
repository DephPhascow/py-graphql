import websocket, ssl

from py_simple_graphql.query import Query
# try:
#     import thread
# except ImportError:
import _thread as thread
import time
import json
from strenum import StrEnum
from dataclasses import dataclass, field
from typing import Any

class WSReceiveMessageType(StrEnum):
    DATA = "data"
    COMPLETE = "complete"

@dataclass
class WSReceiveMessage:
    type: WSReceiveMessageType
    id: str
    payload: Any
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = WSReceiveMessageType(self.type)

@dataclass
class WSGraphQL:
    ws_url: str
    enable_traceback: bool = False
    ws: websocket.WebSocketApp = None
    headers: dict = field(default_factory=dict)

    def __post_init__(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.ws_url,
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close,
                                header=self.headers,
                                subprotocols=["graphql-ws"])
        
        args = {
            'sslopt': {
                "cert_reqs": ssl.CERT_NONE
            }, 
        }
        thr = thread.start_new_thread(self.ws.run_forever, args=(*{
            'sslopt': {
                "cert_reqs": ssl.CERT_NONE
            }, 
        },) )


    def on_open(self):
        pass
    def on_close(self, a, b, c):
        pass
    def on_message(self, message: WSReceiveMessage):
        print(message.payload)

    def on_error(self, error: Exception, a):
        pass
    
    def execute(self, quey: Query, vars: dict = {}):
        self.ws.send(json.dumps({
            "id": "1",
            "type": "start",
            "payload": {
                "query": quey.query,
                "variables": vars
            }
        }))

headers= {
        "Authorization": "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoie1xuIFwiZXhwXCI6IFwiMjAyNC0wNS0wN1QxMTozNzo0NC44MDg2ODBcIixcbiBcIm9yaWdJYXRcIjogXCIyMDI0LTA1LTA3VDExOjMyOjQ0LjgwODY4MFwiLFxuIFwidGdfaWRcIjogXCIxMjNcIlxufSJ9.iCoCQgjiQOwzK0LU9WpZ3pUy_1gJ1YyTxP0h60gcwJE",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'Upgrade': 'websocket',
        'Connection': 'Upgrade',
        'Sec-WebSocket-Key': 'suyuGTgHP89YSDTAad2evQ==',
        'Sec-WebSocket-Version': '13',
        'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
        'Sec-WebSocket-Protocol': 'graphql-transport-ws',
        'Cookie': 'csrftoken=ZgI4NJJ0sYewCXMo6VuXi8tnGaSjYwoU'
    }

ws = WSGraphQL("wss://telecure.ru/graphql/", headers=headers, enable_traceback=True)
ws.execute(Query("subscription ex ($target: Int){ count (target: $target) }"), vars={"target": 2})
# ws.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

# def on_message(ws, message):
#     print(message)

# def on_error(ws, error):
#     print(error)

# def on_close(a, b, c):
#     print("close")

# def on_open(ws):
#     ws.send(json.dumps({
#             "id": "1",
#             "type": "start",
#             "payload": {
#                 "query": "subscription ex ($target: Int){ count (target: $target) }",
#                 "variables": {
#                     "target": 2,
#                 }
#             }
#         }))


# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     ws = websocket.WebSocketApp("wss://telecure.ru/graphql/",
#                               on_message = on_message,
#                               on_error = on_error,
#                               on_close = on_close,
#                               header=headers,
#                               subprotocols=["graphql-ws"])
#     ws.on_open = on_open
#     ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})