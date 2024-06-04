from dataclasses import dataclass, field
from .errors import ValidationError
from .query_str_builder import QueryStrBuilder
from .returned_types import ReturnedTypes
from .query import Query
from .enums import QueryType
from .utils import check_errors
from requests import post
import json
import os
from typing import TYPE_CHECKING, Callable, List, Optional
from .requester import Request
from .ws_graphql import WSGraphQL
if TYPE_CHECKING:
    from .graphql import GraphQL


@dataclass
class GraphQLExecutor:
    name: str
    queries: List[Query] = field(default_factory=list)
    gql: "GraphQL" = field(default_factory="GraphQL")
    subscriptions: List[Query] = field(default_factory=list)
    query_type: QueryType = None
    on_subscription_message: Optional[Callable] = None

    def __post_init__(self):
        self.query_type = self.queries[0].query_type if len(self.queries) > 0 else None
        
    def add_query(self, query: Query):
        if not self.query_type:
            self.query_type = query.query_type
        elif self.query_type != query.query_type:
            raise ValueError("All queries must be the same type")
        self.queries.append(query)
        return self
    
    def __getitem__(self, key: str):
        splited = key.split("__")
        if len(splited) == 2:
            if splited[0] == 'middleware':
                for middleware in self.gql.middlewares:
                    if middleware.name == splited[1]:
                        return middleware
                raise Exception("Not found middleware")
        raise Exception("Unknown command")
    
    async def execute(self, variables: dict = {}, headers: dict = {}, ignore_middlewares: List[str] = [], on_validation: Optional[Callable] = None):
        self.gql.logger.log(f"Begin request: ({[x.query_name for x in self.queries]}) {variables=}; {headers=}, {ignore_middlewares=}")
        result = ReturnedTypes()
        for middleware in self.gql.middlewares:
            if middleware.name not in ignore_middlewares:
                self.gql.logger.log(f"Do middleware: {middleware.name}")
                await middleware.on_before_requests(self.query_type)
                self.gql.logger.log(f"Done middleware: {middleware.name}")
        self.gql.logger.log(f"Begin request: middleware completed, ignore {ignore_middlewares}")
        queries = list(filter(lambda query: query.query_type == QueryType.QUERY, self.queries))
        if len(queries) > 0:
            self.gql.logger.log(f"EXECUTE QUERES {len(queries)}: ({[x.query_name for x in queries]}) {variables=}; {headers=}, {ignore_middlewares=}")
            result += await self.__execute_query(queries, variables, headers, ignore_middlewares=ignore_middlewares, on_validation=on_validation)
            self.gql.logger.log(f"EXECUTE QUERES: DONE")
        mutations = list(filter(lambda query: query.query_type == QueryType.MUTATION, self.queries))
        if len(mutations) > 0:
            self.gql.logger.log(f"EXECUTE MUTATIONS {len(mutations)}: ({[x.query_name for x in mutations]}) {variables=}; {headers=}, {ignore_middlewares=}")
            result +=  await self.__execute_mutations(mutations, variables, headers, ignore_middlewares, on_validation=on_validation)
            self.gql.logger.log(f"EXECUTE MUTATIONS: DONE")
        mutations = list(filter(lambda query: query.query_type == QueryType.SEND_FILE, self.queries))
        if len(mutations) > 0:
            return  await self.__execute_send_file(mutations, variables, headers, on_validation=on_validation)
        mutations = list(filter(lambda query: query.query_type == QueryType.SUBSCRIPTION, self.queries))
        if len(mutations) > 0:
            await self.__execute_subscriptions(mutations, variables, headers, on_validation=on_validation)
            
        for middleware in self.gql.middlewares:
            if middleware.name not in ignore_middlewares:
                await middleware.on_after_requests(self.query_type)        
                    
        return result
        
    async def __request_post(self, url: str, data: dict, headers: dict = {}, ignore_middlewares: List[str] = []):
        self.gql.logger.log(f"REQUEST: IGNORE MIDDLEWARES {[x for x in ignore_middlewares]}")
        for middleware in self.gql.middlewares:
            if middleware.name not in ignore_middlewares:
                headers = {**headers, **await middleware.get_header()}
        self.gql.logger.log(f"REQUEST: {data=}; {headers=}")
        result =  await Request.post(url, json=data, headers=headers)
        self.gql.logger.log(f"RESPONSE: {result=}")
        return result
    
    async def __request_files(self, url: str, data: dict, files: dict, headers: dict = {}, ignore_middlewares: List[str] = []):
        self.gql.logger.log(f"REQUEST: IGNORE MIDDLEWARES {[x for x in ignore_middlewares]}")
        for middleware in self.gql.middlewares:
            if middleware.name not in ignore_middlewares:
                headers = headers | await middleware.get_header()        
        return post(url, data=data, files=files, headers=headers)
    
    async def __execute(self, queries: list[Query], variables: dict, headers: dict = {}, ignore_middlewares: List[str] = [], on_validation: Optional[Callable] = None):
        query = QueryStrBuilder(queries=queries, fragments=self.gql.fragments).builder(self.name)
        data = {
            "query": query,
            "variables": variables,
        }
        data = await self.__request_post(self.gql.gql_config.http, data, headers=headers, ignore_middlewares=ignore_middlewares)
        check_errors(data)
        result = ReturnedTypes()
        if on_validation:
            if not await on_validation(data):
                raise ValidationError(f"Validation error at {data}")
        return result.load(queries, data)
    
    async def __execute_query(self, queries: list[Query], variables: dict, headers: dict = {}, ignore_middlewares: List[str] = [], on_validation: Optional[Callable] = None):
        return await self.__execute(queries, variables, headers, ignore_middlewares, on_validation=on_validation)
    
    async def __execute_mutations(self, mutations: list[Query], variables: dict, headers: dict = {}, ignore_middlewares: List[str] = [], on_validation: Optional[Callable] = None):
        result = ReturnedTypes()
        for mutate in mutations:
            result += await self.__execute([mutate], variables, headers, ignore_middlewares, on_validation=on_validation)
            self.gql.logger.log(f"EXECUTE MUTATIONS {mutate.query_name}: {result}")
        self.gql.logger.log(f"EXECUTE MUTATIONS DONE: {result}")
        return result
    
    async def __execute_subscriptions(self, subscriptions: list[Query], variables: dict, headers: dict = {}, on_validation: Optional[Callable] = None):
        if not self.gql.gql_config.ws:
            raise ValueError("Websocket url not set")
        async with WSGraphQL(self.gql.gql_config.ws) as ws:
            for subscription in subscriptions:
                await ws.execute(subscription, variables, headers, self.on_subscription_message)
        
    async def __execute_send_file(self, mutations: list[Query], variables: dict, headers: dict = {}, on_validation: Optional[Callable] = None):
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
                    res = (await self.__request_files(self.gql.gql_config.http, data=data, files=files, headers=headers))
                    res = res.json()
                    check_errors(res)
                    response.append(res)
            if not found:
                raise ValueError("File not set")
        return response