from dataclasses import dataclass, field
from .graphql_config import GraphQLConfig
from .graphql_executor import GraphQLExecutor
from .query import Query

@dataclass
class GraphQL:
    gql_config: GraphQLConfig = field(default_factory=GraphQLConfig)
    
    def add_query(self, name: str, query: Query):
        return GraphQLExecutor(name=name, queries=[query], gql_config=self.gql_config)