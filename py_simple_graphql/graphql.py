from dataclasses import dataclass, field
from .graphql_config import GraphQLConfig
from .graphql_executor import GraphQLExecutor
from .query import Query
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from .auth import Auth

@dataclass
class GraphQL:
    gql_config: GraphQLConfig = field(default_factory=GraphQLConfig)
    auth: "Auth" = None
    fragments: List[Query] = field(default_factory=list)
        
    async def set_auth(self, auth: "Auth"):
        self.auth = auth
        await self.auth.request_tokens()
                
    async def add_fragment(self, fragment: Query):
        self.fragments.append(fragment)
                
    def add_query(self, name: str, query: Query):
        return GraphQLExecutor(name=name, queries=[query], gql_config=self.gql_config, auth=self.auth, fragments=self.fragments)