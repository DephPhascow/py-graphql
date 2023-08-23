import sys

if sys.version_info >= (3, 10):
    from enum import StrEnum
else:
    from strenum import StrEnum
    
    
class QueryType(StrEnum):
    QUERY = 'query'
    MUTATION = 'mutation'
    SEND_FILE = 'send_file'
    SUBSCRIPTION = 'subscription'