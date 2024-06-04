import asyncio
from tests.subscriptions import my_name
from tests.queres import directionals, users
from tests.mutations import file_upload
from tests.settings import gql

def rev(response):
    print(response)

async def main():
    # executor = gql.add_query("send_file", file_upload())
    # executor = gql.add_query("get_count", my_name(), rev)
    executor = gql.add_query("get_count", file_upload())
    auth = executor['middleware__auth']
    await auth.set_data("302942780", "ca6f048d-572e-49d1-b6dc-8833e1dbe607", None, None, None, None)     
    res = await executor.execute(variables={"appoitmentId": "2", "message": "Hello", "file": "1.jpeg"})
    # executor = gql.add_query("users", users())
    # auth = executor['middleware__auth']
    # await auth.set_data("302942780", "6ab832b9-b20d-4ec5-9b3b-ad9c1376a8e1", None, None, None, None) 
    # res = await executor.execute()
    print(res)

asyncio.run(main())