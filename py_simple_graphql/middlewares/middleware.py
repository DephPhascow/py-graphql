from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..query import Query
from ..returned_types import ReturnedTypes
from ..enums import QueryType
from ..graphql import GraphQL

@dataclass
class Middleware:
    name: str 
    gql: GraphQL = field(default_factory=GraphQL)
    headers: Dict[str, Any] = field(default_factory=dict)
    
    async def on_startup(self, ):
        pass
    async def on_shutdown(self, ):
        pass
    async def on_before_requests(self, type: QueryType):
        pass
    async def on_before_request(self, query: Query):
        pass
    async def on_after_requests(self, type: QueryType):
        pass
    async def on_after_request(self, response: ReturnedTypes):
        pass
    async def get_header(self, ):
        pass
    