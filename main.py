from core.graphql_executor import GraphQLExecutor
from core.query import Query
from core.graphql_config import GraphQLConfig
from core.graphql import GraphQL
from dataclasses import dataclass
from dotenv import load_dotenv
from os import getenv

load_dotenv()

HTTP = getenv("HTTPS")

query = Query(
  query_name = "existingTgClient",
  variables = {
    "$security": "SecurityInput!",
    "$botUsername": "String!",
    "$tgId": "String!"
  }, 
  init_args_from_vars=True
)

count_user = Query(
  query_name = "getCountUsers",
  variables = {
    "$security": "SecurityInput!"
  }, 
  init_args_from_vars=True
)

gql = GraphQL(gql_config=GraphQLConfig(http=HTTP, DEBUG=True))

@dataclass
class Tmp:
    name: str

executor: GraphQLExecutor = gql.add_query("existingClient", query)
executor.add_query(count_user)
res = executor.execute({
    "security": {
      "appToken": "123",
      "token": "302942780",
    },
    "botUsername": "example",
    "tgId": "302942780"
  })
print(res)



# if __name__ == "__main__":
#   gql = GraphQL(gql_config=GraphQLConfig(http=HTTPS))
#   query = get_system_query()
#   executor: GraphQLExecutor = gql.add_query("getSystemInformation", query)
#   print(query)
#   executor.execute(success=on_get_system_information, error=lambda error: print(error))