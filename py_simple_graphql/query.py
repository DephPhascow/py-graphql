from dataclasses import dataclass, field
from .enums import QueryType

@dataclass
class Query:
    query_type: QueryType = field(default=QueryType.QUERY)
    query: str = ""
    variables: dict = field(default_factory=dict, )
    id: str = ""
    query_name: str = ""
    query_request: str = ""
    init_args_from_vars: bool = False
    
    def __post_init__(self):
        if self.init_args_from_vars:
            vars = ",".join([f"{key[1:]}: {key}" for key in self.variables.keys()])
            request = f"{{ { self.query_request } }}" if self.query_request else ""
            self.query = f"{self.query_name}({vars}) {request}"