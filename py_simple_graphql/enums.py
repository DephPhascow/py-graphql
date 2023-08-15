from enum import StrEnum

class QueryType(StrEnum):
    QUERY = 'query'
    MUTATION = 'mutation'
    SUBSCRIPTION = 'subscription'