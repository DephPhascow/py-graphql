from dataclasses import dataclass, field
from .query import Query

@dataclass
class SubscriptionListener:
    id: str
    query: Query = field(default_factory=Query)
    socket: str # websockets