from dataclasses import dataclass

@dataclass
class GraphQLConfig:
    http: str
    ws: str = ""
    DEBUG: bool = False