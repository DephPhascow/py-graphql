from core.graphql import GraphQL, GraphQLConfig
import fragments
import asyncio

from core.gql_type import GQLType
from core.utils import gen_query, gen_mutate
from dataclasses import dataclass


@dataclass
class Directional(GQLType):
    name_r: str

def auth():
    return gen_mutate(
        name="tokenAuth",
        request=" token { token }",
        var={
            "tgId": "String!",
            "password": "String!",
        },
        q_words="data.tokenAuth.token.token"
    )
    

def users_admins():
  return gen_query(
    name="directionalsDel",
    request="...name",
    require_fragments = ['name'],
    to_type=Directional,
    q_words="data.directionalsDel[:].{name_r: name}"
  )

GRAPHQL_URL = "https://telecure.ru/graphql/"

gql = GraphQL(
    gql_config=GraphQLConfig(
        http=GRAPHQL_URL,
        DEBUG=True,
    )
)

async def main():
    # await gql.add_fragment(fragments.fragment_user())
    # executor = gql.add_query("ex", users_admins())
    executor = gql.add_query("ex", auth())
    # executor.add_query(auth())
    res = await executor.execute(variables={"tgId": "1", "password": "1"})
    print(res.first())
    
asyncio.run(main())