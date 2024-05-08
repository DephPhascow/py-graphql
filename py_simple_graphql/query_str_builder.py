from dataclasses import dataclass, field
from typing import List
from .query import Query, QueryFragment
from abc import ABC

@dataclass
class QueryBuilder:
    def builder(self, name: str):
        pass
    
@dataclass
class QueryFragmentBuilder(QueryBuilder):
    fragments: List[QueryFragment] = field(default_factory=list)
    def builder(self, required_fragments: List[str]):
        fragments_str = ""
        for a in required_fragments:
            fragments_str = '\r\n'.join(
                [f"fragment {fragment.query}" for req_fragment in a 
                for fragment in self.fragments if fragment.query_name == req_fragment]
            )    
            # добавить встроеные fragments required
        return fragments_str

@dataclass
class QueryStrBuilder:
    queries: List[Query] = field(default_factory=list)
    fragments: List[QueryFragment] = field(default_factory=list)

    def add(self, query: Query):
        self.queries.append(query)
        return self
    
    def builder(self, name: str):
        dataQuery = ""
        dataVariables = ""
        vars = []
        fragments_str = QueryFragmentBuilder(fragments=self.fragments).builder([x.require_fragments for x in self.queries])
        
        for query in self.queries:
            vars += [f"{key}: {value}" for key, value in query.variables.items() if f"{key}: {value}" not in vars]
            dataQuery += f"{query.query} "
            
        dataVariables = ", ".join(vars)
        dataVariables = f"({dataVariables})" if dataVariables != "" else ""
        return f"{fragments_str}\r\n{self.queries[0].query_type} {name} {dataVariables} {{ {dataQuery} }}"