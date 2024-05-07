from dataclasses import dataclass, field
from typing import Dict, Any, List

from py_simple_graphql.query import Query
from py_simple_graphql.utils import get_data

@dataclass
class ReturnedTypes:
    values: Dict[str, Any] = field(default_factory=dict)
    
    def __getitem__(self, key: str):
        if key in self.values:
            return self.values[key]
        
    def __add__(self, other: "ReturnedTypes"):
        if not isinstance(other, ReturnedTypes):
            raise TypeError("ReturnedTypes can only be added to ReturnedTypes")
        self.values.update(other.values)
        return self
        
    def add(self, key: str, value: Any):
        self.values[key] = value
        
    def load(self, queries: List[Query], data: dict):
        for query in queries:
            a = get_data(data, query.query_name, query.q_words)
            if query.to_type:
                b = [query.to_type(**item) for item in a] if isinstance(a, list) else query.to_type(**a)
            else:
                b = a
            self.add(query.query_name, b)
        return self
    
    def first(self):
        return list(self.values.values())[0]
    
    def last(self):
        return list(self.values.values())[-1]
    
    def filter(self, method_name: str, key: str, value: Any):
        instance = self.values[method_name]
        if isinstance(instance, list):
            return list(filter(lambda x: getattr(x, key) == value, instance))
        return []