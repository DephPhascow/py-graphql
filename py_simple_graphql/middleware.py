from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict
from py_simple_graphql.enums import QueryType
from py_simple_graphql.graphql import GraphQL

@dataclass
class Middleware:
    name: str 
    gql: GraphQL = field(default_factory=GraphQL)
    headers: Dict[str, Any] = field(default_factory=dict)
    
    async def on_startup(self, ):
        pass
    async def on_shutdown(self, ):
        pass
    async def on_before_request(self, type: QueryType):
        pass
    async def on_after_request(self, type: QueryType):
        pass
    async def get_header(self, ):
        pass
    