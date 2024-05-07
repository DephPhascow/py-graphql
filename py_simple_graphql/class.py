from dataclasses import dataclass, field
from py_simple_graphql.query import Query

@dataclass
class SubscriptionListener:
    id: str
    query: Query = field(default_factory=Query)
    socket: str # websockets