from dataclasses import dataclass, field


from .graphql_config import GraphQLConfig
from .query import Query
from .enums import QueryType
from .utils import check_errors
from requests import post
import json
from .logger import Logger
import os


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
    
    def execute(self, variables: dict, headers: dict = {}):
        queries = list(filter(lambda query: query.query_type == QueryType.QUERY, self.queries))
        if len(queries) > 0:
            return self.__execute_query(queries, variables, headers)
        mutations = list(filter(lambda query: query.query_type == QueryType.MUTATION, self.queries))
        if len(mutations) > 0:
            return self.__execute_mutations(mutations, variables, headers)
        mutations = list(filter(lambda query: query.query_type == QueryType.SEND_FILE, self.queries))
        if len(mutations) > 0:
            return self.__execute_send_file(mutations, variables, headers)        
        
    def __request_post(self, url: str, data: dict, headers: dict = {}):
        return post(url, json=data, headers=headers)
    def __request_files(self, url: str, data: dict, files: dict, headers: dict = {}):
        if "Content-Type" in headers:
            headers = headers | {
                "Content-Type": "multipart/form-data"
            }
        return post(url, data=data, files=files, headers=headers)
    
    def __execute_query(self, queries: list[Query], variables: dict, headers: dict = {}):
        dataQuery = ""
        dataVariables = ""
        vars = []
        for query in queries:
            vars += [f"{key}: {value}" for key, value in query.variables.items() if f"{key}: {value}" not in vars]
            dataQuery += f"{query.query} "
        dataVariables = ", ".join(vars)
        dataVariables = f"({dataVariables})" if dataVariables != "" else ""
        data = {
            "query": f"query {self.name} {dataVariables} {{ {dataQuery} }}",
            "variables": variables,
        }
        if self.gql_config.DEBUG:
            self.logger.print("queries.txt", json.dumps(data))
        response = self.__request_post(self.gql_config.http, data, headers=headers)
        data = response.json()
        check_errors(data)
        if self.gql_config.DEBUG:
            self.logger.print("response.txt", json.dumps(data)) 
        return data
    def __execute_mutations(self, mutations: list[Query], variables: dict, headers: dict = {}):
        response = []
        for mutate in mutations:
            dataVariables = ",".join([f"{key}: {value}" for key, value in mutate.variables.items()])
            dataVariables = f"({dataVariables})" if dataVariables != "" else ""
            data = {
                "query": f"mutation {self.name} {dataVariables} {{ {mutate.query} }}",
                "variables": variables,
            }
            if self.gql_config.DEBUG:
                self.logger.print("query.txt", json.dumps(data))
            res = self.__request_post(self.gql_config.http, data, headers=headers).json()
            check_errors(res)
            response.append(res)
            if self.gql_config.DEBUG:
                self.logger.print("response.txt", json.dumps(response)) 
        return response
    def __execute_send_file(self, mutations: list[Query], variables: dict, headers: dict = {}):
        response = []
        for mutate in mutations:
            dataVariables = ",".join([f"{key}: {value}" for key, value in mutate.variables.items()])
            dataVariables = f"({dataVariables})" if dataVariables != "" else ""
            found = False
            for x, y in mutate.variables.items():
                if y == "Upload!":
                    x = x.replace("$", "")
                    found = True
                    image_name = variables[x]
                    if not os.path.exists(image_name):
                        raise ValueError(f"File {image_name} not found")
                    map = { x: [f"variables.{x}"] }        
                    operations = {
                        "query": f"mutation {self.name} {dataVariables} {{ {mutate.query} }}",
                        "variables": {
                            x: ""
                        } | variables,                 
                    }
                    data = {
                        "operations": json.dumps(operations),
                        "map": json.dumps(map),                
                    }
                    files = {
                        x: open(image_name, "rb")
                    }
                    if self.gql_config.DEBUG:
                        self.logger.print("query.txt", json.dumps(data))            
                    res = self.__request_files(self.gql_config.http, data=data, files=files, headers=headers).json()
                    check_errors(res)
                    response.append(res)
                    if self.gql_config.DEBUG:
                        self.logger.print("response.txt", json.dumps(response)) 
            if not found:
                raise ValueError("File not set")
        return response