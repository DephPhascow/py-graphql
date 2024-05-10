from dataclasses import dataclass, field
from typing import List
from .query import Query, QueryFragment
from abc import ABC

@dataclass
class QueryBuilder(ABC):
    def builder(self, name: str):
        pass
    
@dataclass
class QueryFragmentBuilder(QueryBuilder):
    fragments: List[QueryFragment] = field(default_factory=list)
    def builder(self, required_fragments: List[str]):
        fragments_str = ""
        for fragment in self.fragments:
            if fragment.query_name in required_fragments:
                fragments_str += f"fragment {fragment.query}\r\n"
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
        requre_fragments = [x.require_fragments for x in self.queries]
        names = []
        for req in requre_fragments:
            for fname in req:
                names.append(fname)
                
        fragments_str = QueryFragmentBuilder(fragments=self.fragments).builder(names)
        for query in self.queries:
            vars += [f"{key}: {value}" for key, value in query.variables.items() if f"{key}: {value}" not in vars]
            dataQuery += f"{query.query} "
            
        dataVariables = ", ".join(vars)
        dataVariables = f"({dataVariables})" if dataVariables != "" else ""
        res =  f"{fragments_str}\r\n{self.queries[0].query_type} {name} {dataVariables} {{ {dataQuery} }}"
        return res