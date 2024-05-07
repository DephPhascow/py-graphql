from dataclasses import dataclass, field

from py_simple_graphql.query_str_builder import QueryStrBuilder
from py_simple_graphql.returned_types import ReturnedTypes
from py_simple_graphql.graphql_config import GraphQLConfig
from py_simple_graphql.query import Query
from py_simple_graphql.enums import QueryType
from py_simple_graphql.utils import check_errors, get_data
from requests import post
import json
from py_simple_graphql.logger import Logger
import os
from typing import TYPE_CHECKING, Callable, List, Optional
from py_simple_graphql.requester import Request
from py_simple_graphql.ws_graphql import WSGraphQL
if TYPE_CHECKING:
    from py_simple_graphql.auth import Auth


@dataclass
class GraphQLExecutor:
    name: str
    gql_config: GraphQLConfig = field(default_factory=GraphQLConfig)
    queries: List[Query] = field(default_factory=list)
    fragments: List[Query] = field(default_factory=list)
    subscriptions: List[Query] = field(default_factory=list)
    fragments: List[Query] = field(default_factory=list)
    auth: "Auth" = None
    logger: Logger = None
    query_type: QueryType = None
    on_subscription_message: Optional[Callable] = None

    def __post_init__(self):
        self.query_type = self.queries[0].query_type if len(self.queries) > 0 else None
        
    def set_logger(self, logger: Logger):
        self.Logger = Logger
        
    def add_query(self, query: Query):
        if not self.query_type:
            self.query_type = query.query_type
        elif self.query_type != query.query_type:
            raise ValueError("All queries must be the same type")
        self.queries.append(query)
        return self
    
    def add_fragment(self, fragment: Query):
        self.fragments.append(fragment)
    
    async def execute(self, variables: dict = {}, headers: dict = {}, ignore_token: bool = False, ignore_middlewares: List[str] = []):
        result = ReturnedTypes()
        if not ignore_token and self.auth and "auth" not in ignore_middlewares:
            await self.auth.middleware()
        queries = list(filter(lambda query: query.query_type == QueryType.QUERY, self.queries))
        if len(queries) > 0:
            result += await self.__execute_query(queries, variables, headers,)
        mutations = list(filter(lambda query: query.query_type == QueryType.MUTATION, self.queries))
        if len(mutations) > 0:
            result +=  await self.__execute_mutations(mutations, variables, headers, ignore_token)
        mutations = list(filter(lambda query: query.query_type == QueryType.SEND_FILE, self.queries))
        if len(mutations) > 0:
            result +=  self.__execute_send_file(mutations, variables, headers)
        mutations = list(filter(lambda query: query.query_type == QueryType.SUBSCRIPTION, self.queries))
        if len(mutations) > 0:
            await self.__execute_subscriptions(mutations, variables, headers)
        return result
        
    async def __request_post(self, url: str, data: dict, headers: dict = {}, ignore_token: bool = False):
        if self.auth and not ignore_token:
            headers['Authorization'] = f"JWT {self.auth.token.token}"
        if self.gql_config.user_agent:
            headers['User-Agent'] = self.gql_config.user_agent
        self.logger.log(f"Посылается запрос: {data} с шапкой: {headers}, значение аргументов: {self.auth} {not ignore_token}")
        return await Request.post(url, json=data, headers=headers, disable_ssl=self.gql_config.disable_ssl)
    
    def __request_files(self, url: str, data: dict, files: dict, headers: dict = {}):
        if "Content-Type" in headers:
            headers = headers | {
                "Content-Type": "multipart/form-data"
            }
        if self.gql_config.user_agent:
            headers['User-Agent'] = self.gql_config.user_agent
        return post(url, data=data, files=files, headers=headers)
    
    async def __execute(self, queries: list[Query], variables: dict, headers: dict = {}, ignore_token: bool = False):
        query = QueryStrBuilder(queries=queries, fragments=self.fragments).builder(self.name)
        data = {
            "query": query,
            "variables": variables,
        }
        if self.gql_config.DEBUG:
            self.logger.log(json.dumps(data))
        data = await self.__request_post(self.gql_config.http, data, headers=headers, ignore_token=ignore_token)
        check_errors(data)
        if self.gql_config.DEBUG:
            self.logger.log(json.dumps(data)) 
        result = ReturnedTypes()
        return result.load(queries, data)
    
    async def __execute_query(self, queries: list[Query], variables: dict, headers: dict = {}, ignore_token: bool = False):
        return await self.__execute(queries, variables, headers, ignore_token)
    
    async def __execute_mutations(self, mutations: list[Query], variables: dict, headers: dict = {}, ignore_token: bool = False):
        response = []
        for_result = { "data": {} }
        for mutate in mutations:
            res = await self.__execute([mutate], variables, headers, ignore_token)
            for_result['data'][mutate.query_name] = get_data(res, mutate.query_name)
            if self.gql_config.DEBUG:
                self.logger.log(f'{response}') 
        result = ReturnedTypes()
        return result.load(mutations, for_result)
    
    async def __execute_subscriptions(self, subscriptions: list[Query], variables: dict, headers: dict = {}):
        if not self.gql_config.ws:
            raise ValueError("Websocket url not set")
        async with WSGraphQL(self.gql_config.ws) as ws:
            for subscription in subscriptions:
                await ws.execute(subscription, variables, headers, self.on_subscription_message)
        
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
                        self.logger.log(json.dumps(data))            
                    res = self.__request_files(self.gql_config.http, data=data, files=files, headers=headers).json()
                    check_errors(res)
                    response.append(res)
                    if self.gql_config.DEBUG:
                        self.logger.log(json.dumps(response)) 
            if not found:
                raise ValueError("File not set")
        return response