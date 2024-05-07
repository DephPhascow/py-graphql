from py_simple_graphql.graphql import GraphQL, GraphQLConfig
from tests import fragments


GRAPHQL_URL = "https://telecure.ru/graphql/"

gql = GraphQL(
    gql_config=GraphQLConfig(
        http=GRAPHQL_URL,
        DEBUG=True,
        disable_ssl=True
    )
)

gql.add_fragment(fragments.fragment_user())