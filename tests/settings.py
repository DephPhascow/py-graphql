from py_simple_graphql.graphql import GraphQL, GraphQLConfig
from py_simple_graphql.logger import ConsoleLogger, FileLogger
from py_simple_graphql.middlewares.auth_middleware import AuthMiddleware
from tests import fragments
import asyncio
from dotenv import load_dotenv
import os

load_dotenv(override=True)

GRAPHQL_URL = os.getenv("GRAPHQL_URL")
WS_URL = os.getenv("WS_URL")

gql = GraphQL(
    gql_config=GraphQLConfig(
        http=GRAPHQL_URL,
        ws=WS_URL,
        DEBUG=True,
        disable_ssl=True
    )
)

async def on_save(token, login):
    pass

gql.add_middleware(AuthMiddleware(gql=gql, name="auth", on_save=on_save))
gql.set_logger(FileLogger(file_name="gql-log.txt"))
    
asyncio.run(gql.init())