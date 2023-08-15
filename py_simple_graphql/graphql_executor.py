from dataclasses import dataclass, field

from .graphql_config import GraphQLConfig
from .query import Query
from .enums import QueryType
from requests import post
import json
from .logger import Logger

@dataclass
class GraphQLExecutor:
    name: str
    gql_config: GraphQLConfig = field(default_factory=GraphQLConfig)
    queries: list[Query] = field(default_factory=list[Query])
    subscriptions: list = field(default_factory=list)
    logger: Logger = Logger()
    def add_query(self, query: Query):
        self.queries.append(query)
        return self
    
    def execute(self, variables: dict):
        queries = list(filter(lambda query: query.query_type == QueryType.QUERY, self.queries))
        if len(queries) > 0:
            return self.__execute_query(queries, variables)
        mutations = list(filter(lambda query: query.query_type == QueryType.MUTATION, self.queries))
        if len(mutations) > 0:
            return self.__execute_mutations(mutations, variables)        
        
    def __request_post(self, url: str, data: dict, headers: dict = {}):
        return post(url, json=data, headers=headers)
    
    def __execute_query(self, queries: list[Query], variables: dict, headers: dict = {}):
        dataQuery = ""
        dataVariables = ""
        vars = []
        for query in queries:
            vars += [f"{key}: {value}" for key, value in query.variables.items() if f"{key}: {value}" not in vars]
            tmp = query.query
            dataQuery += f"{tmp} "
        dataVariables = ", ".join(vars)
        dataVariables = f"({dataVariables})" if dataVariables != "" else ""
        data = {
            "query": f"query {self.name} {dataVariables} {{ {dataQuery} }}",
            "variables": variables,
        }
        print(data)
        if self.gql_config.DEBUG:
            self.logger.print("queries.txt", json.dumps(data))
        response = self.__request_post(self.gql_config.http, data, headers=headers)
        data = response.json()
        if self.gql_config.DEBUG:
            self.logger.print("response.txt", json.dumps(data)) 
        
        return data
    def __execute_mutations(self, mutations: list[Query], variables: dict, headers: dict = {}):
        response = []
        for mutate in mutations:
            dataVariables = ",".join([f"{key}: {value}" for key, value in mutate.variables.items()])
            dataVariables = f"({dataVariables})" if dataVariables != "" else ""
            tmp = mutate.query
            if mutate.init_args_from_vars:
                tmp = [tmp.replace(f"{key}", f"{key[1:]}: {key}") for key in mutate.variables.keys()]
            data = {
                "query": f"mutation {self.name} {dataVariables} {{ {tmp} }}",
                "variables": variables,
            }
            if self.gql_config.DEBUG:
                self.logger.print("query.txt", json.dumps(data))            
            response.append(self.__request_post(self.gql_config.http, data, headers=headers).json())
            if self.gql_config.DEBUG:
                self.logger.print("response.txt", json.dumps(response)) 
        return response