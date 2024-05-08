from py_simple_graphql.graphql import GraphQL, GraphQLConfig
from py_simple_graphql.logger import ConsoleLogger, FileLogger
from tests import fragments


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
# gql.set_logger(FileLogger(file_name="log.txt"))
gql.set_logger(ConsoleLogger())
gql.add_fragment(fragments.fragment_user())