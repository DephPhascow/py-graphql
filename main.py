import asyncio
from tests.subscriptions import get_count
from tests.queres import directionals, users
from tests.mutations import file_upload
from tests.settings import gql

def rev(response):
    print(response)

async def main():
    # executor = gql.add_query("send_file", file_upload())
    executor = gql.add_query("get_count", get_count(), rev)
    await executor.execute(variables={"target": 3}, ignore_middlewares=['auth'])
    executor = gql.add_query("users", users())
    auth = executor['middleware__auth']
    await auth.set_data("302942780", "123") 
    res = await executor.execute()
    print(res)
    token = auth.token
    auth.load(token)
    res = await executor.execute()
    # res = await executor.execute(variables={
    #     "img": "tests\\1.jpeg",
    #     "name": "esa"
    # })
    print(res)

asyncio.run(main())