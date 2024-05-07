from dataclasses import dataclass, field
from py_simple_graphql.graphql_config import GraphQLConfig
from py_simple_graphql.graphql_executor import GraphQLExecutor
from py_simple_graphql.logger import Logger
from py_simple_graphql.query import Query
from typing import TYPE_CHECKING, Callable, List, Optional
if TYPE_CHECKING:
    from .auth import Auth

@dataclass
class GraphQL:
    gql_config: GraphQLConfig = field(default_factory=GraphQLConfig)
    auth: "Auth" = None
    fragments: List[Query] = field(default_factory=list)
    logger: Logger = field(default_factory=Logger)
    def __post_init__(self):
        self.fragments = []
        self.logger.log("Прошла инициализация")
                
    def set_logger(self, logger: Logger):
        self.logger = logger
        self._set_logger_debug()
        
    def _set_logger_debug(self):
        self.logger.DEBUG = self.gql_config.DEBUG
        self.logger.log(f"Установился логгер на {self.gql_config.DEBUG}")
        
    async def set_auth(self, auth: "Auth"):
        self.auth = auth
        self.logger.log(f"Установился авторизации")
        await self.auth.request_tokens()
        self.logger.log(f"Получен результат авторизации: {self.auth.token}")
                
    def add_fragment(self, fragment: Query):
        self.fragments.append(fragment)
        self.logger.log(f"Добавлен фрагмент: {fragment}")
                
    def add_query(self, name: str, query: Query, on_subscription_message: Optional[Callable] = None):
        return GraphQLExecutor(name=name, queries=[query], gql_config=self.gql_config, auth=self.auth, fragments=self.fragments, on_subscription_message=on_subscription_message, logger=self.logger)