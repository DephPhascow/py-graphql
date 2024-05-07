import asyncio
import websockets
import json
import ssl

async def subscribe():
    uri = "wss://telecure.ru/graphql/"  # Замените на ваш адрес GraphQL WebSocket
    headers = {
        "Authorization": "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoie1xuIFwiZXhwXCI6IFwiMjAyNC0wNS0wN1QxMDowODoyNi41MDUzNDhcIixcbiBcIm9yaWdJYXRcIjogXCIyMDI0LTA1LTA3VDEwOjAzOjI2LjUwNTM0OFwiLFxuIFwidGdfaWRcIjogXCIxMjNcIlxufSJ9.vsywwnPPBPACPpUwIwGuYVJfXImUBczU49gGEkC9jLQ"
    }
    sslcontext = ssl.create_default_context()
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    async with websockets.connect(uri, ssl=sslcontext, extra_headers=headers) as websocket:
        # Определение вашего запроса подписки
        subscription_query = {
            "query": """
            subscription {
              newMessage {
                id
                content
              }
            }
            """
        }

        # Отправка запроса подписки
        await websocket.send(json.dumps(subscription_query))

        # Получение и печать результатов
        while True:
            response = await websocket.recv()
            print(json.loads(response))

asyncio.get_event_loop().run_until_complete(subscribe())
