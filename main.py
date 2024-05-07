import asyncio
import json
from tests.settings import gql
from tests.queres import users_admins
import ssl
import websockets

# async def main():
#     executor = gql.add_query("ex", users_admins())
#     res = await executor.execute()
#     print(res.filter("directionalsDel", "name_r", "Тура"))

async def subscribe_to_graphql(host: str, port: int):
    try:
        headers = {
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
        uri = f"wss://{host}/graphql/"  # Замените на ваш адрес GraphQL сервера
        sslcontext = ssl.create_default_context()
        sslcontext.check_hostname = False
        sslcontext.verify_mode = ssl.CERT_NONE    
        async with websockets.connect(uri, ssl=sslcontext, extra_headers=headers) as websocket:
            await websocket.send(json.dumps({
                "id": "1",
                "type": "connection_init",
                "payload": {
                    "query": "subscription { count }"
                }
            }))
    except Exception as e:
        print(f"An error occurred: {e}")
        # subscription_query = '''
        # subscription {
        #     count
        # }
        # '''
        # await websocket.send(subscription_query)
        
        # while True:
        #     response = await websocket.recv()
        #     print(response)
        pass

async def main():
    await subscribe_to_graphql("telecure.ru", 443)

asyncio.run(main())