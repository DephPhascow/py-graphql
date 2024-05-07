import websocket, ssl
try:
    import thread
except ImportError:
    import _thread as thread
import time, msgpack
import json

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

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(a, b, c):
    print("close")

def on_open(ws):
    ws.send(json.dumps({
            "id": "1",
            "type": "start",
            "payload": {
                "query": "subscription { count }"
            }
        }))


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://telecure.ru/graphql/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              header=headers,
                              subprotocols=["graphql-ws"])
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})