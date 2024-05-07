from py_simple_graphql.gql_type import GQLType
from dataclasses import dataclass

@dataclass
class Directional(GQLType):
    name_r: str