from dataclasses import dataclass
from typing import List

@dataclass
class Location:
    line: int
    column: int
    
@dataclass
class Error:
    message: str
    locations: List[Location]
    
class Errors(Exception):
    errors: List[Error]
    def __init__(self, errors):
        self.errors = errors