from dataclasses import dataclass, field
from typing import List
from .query import Query

@dataclass
class QueryStrBuilder:
    queries: List[Query] = field(default_factory=list)
    fragments: List[Query] = field(default_factory=list)

    def add(self, query: Query):
        self.queries.append(query)
        return self
    
    def builder(self, name: str):
        dataQuery = ""
        dataVariables = ""
        vars = []
        fragments_str = ""
        for query in self.queries:
            vars += [f"{key}: {value}" for key, value in query.variables.items() if f"{key}: {value}" not in vars]
            dataQuery += f"{query.query} "
            fragments_str = '\r\n'.join(
                [f"fragment {fragment.query}" for req_fragment in query.require_fragments 
                 for fragment in self.fragments if fragment.query_name == req_fragment]
            )        
        dataVariables = ", ".join(vars)
        dataVariables = f"({dataVariables})" if dataVariables != "" else ""
        return f"{fragments_str}\r\n{self.queries[0].query_type} {name} {dataVariables} {{ {dataQuery} }}"