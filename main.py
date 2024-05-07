import asyncio
from tests.subscriptions import get_count
from tests.queres import directionals
from tests.settings import gql

def rev(response):
    print(response)

async def main():
    executor = gql.add_query("get_count", get_count(), rev)
    await executor.execute(variables={"target": 3})
    executor = gql.add_query("directionals", directionals())
    res = await executor.execute()
    print(res)

asyncio.run(main())