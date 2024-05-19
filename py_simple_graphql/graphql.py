from copy import copy
from dataclasses import dataclass, field
from .graphql_config import GraphQLConfig
from .graphql_executor import GraphQLExecutor
from .logger import Logger
from .query import Query, QueryFragment
from typing import TYPE_CHECKING, Callable, List, Optional
if TYPE_CHECKING:
    from .middlewares.middleware import Middleware

@dataclass
class GraphQL:
    gql_config: GraphQLConfig = field(default_factory=GraphQLConfig)
    middlewares: List["Middleware"] = field(default_factory=list)
    fragments: List[QueryFragment] = field(default_factory=list)
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
                
    def add_middleware(self, middleware: "Middleware"):
        self.middlewares.append(middleware)
        
    async def init(self):
        for middleware in self.middlewares:
            await middleware.on_startup()
                
    def add_fragment(self, fragment: QueryFragment):
        self.fragments.append(fragment)
        self.logger.log(f"Добавлен фрагмент: {fragment}")

    def add_query(self, name: str, query: Query, on_subscription_message: Optional[Callable] = None):
        return GraphQLExecutor(name=name, queries=[query], gql=copy(self), on_subscription_message=on_subscription_message)
    
    # async def __del__(self):
    #     for middleware in self.middlewares:
    #         await middleware.on_shutdown()