from py_simple_graphql.graphql import GraphQL, GraphQLConfig
from py_simple_graphql.logger import ConsoleLogger, FileLogger
from py_simple_graphql.middlewares.auth_middleware import AuthMiddleware
from tests import fragments
import asyncio

GRAPHQL_URL = "https://telecure.ru/graphql/"
WS_URL = "wss://telecure.ru/graphql/"

gql = GraphQL(
    gql_config=GraphQLConfig(
        http=GRAPHQL_URL,
        ws=WS_URL,
        DEBUG=True,
        disable_ssl=True
    )
)

gql.add_middleware(AuthMiddleware(gql=gql, name="auth"))
gql.set_logger(FileLogger(file_name="gql-log.txt"))
    
asyncio.run(gql.init())