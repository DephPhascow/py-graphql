from strenum import StrEnum
    
    
class QueryType(StrEnum):
    QUERY = 'query'
    MUTATION = 'mutation'
    SEND_FILE = 'send_file'
    SUBSCRIPTION = 'subscription'
    FRAGMENT = 'fragment'