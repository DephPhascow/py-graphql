import asyncio
from tests.settings import gql
from tests.queres import users_admins

async def main():
    executor = gql.add_query("ex", users_admins())
    res = await executor.execute()
    print(res.filter("directionalsDel", "name_r", "Тура"))
    
asyncio.run(main())