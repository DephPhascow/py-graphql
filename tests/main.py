from py_simple_graphql.enums import QueryType
from py_simple_graphql.graphql_executor import GraphQLExecutor
from py_simple_graphql.query import Query
from py_simple_graphql.graphql_config import GraphQLConfig
from py_simple_graphql.graphql import GraphQL
from py_simple_graphql.models import Errors, Error
from dataclasses import dataclass
from dotenv import load_dotenv
from os import getenv

load_dotenv()

HTTP = getenv("HTTPS")

query = Query(
  query_type=QueryType.SEND_FILE,
  query_name = "findObject",
  query_request=" x, y, w, h ",
  variables = {
    "$image": "Upload!",
    "$objectType": "FindObjectEnum!",
  }, 
  init_args_from_vars=True
)


gql = GraphQL(gql_config=GraphQLConfig(http=HTTP, DEBUG=True))

@dataclass
class Tmp:
    name: str

executor: GraphQLExecutor = gql.add_query("existingClient", query)
try:
  res = executor.execute({
    "image": "tests/00020-1044244937.jpeg",
    "objectType": "SMILE"
  })
  print(res)
except Errors as e:
  for a in e.errors:
    print(a.message)



# if __name__ == "__main__":
#   gql = GraphQL(gql_config=GraphQLConfig(http=HTTPS))
#   query = get_system_query()
#   executor: GraphQLExecutor = gql.add_query("getSystemInformation", query)
#   print(query)
#   executor.execute(success=on_get_system_information, error=lambda error: print(error))