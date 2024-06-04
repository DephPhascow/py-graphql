from typing import Dict, List
from ..caches.enums import CacheType
from ...middlewares.middleware import Middleware
from dataclasses import dataclass

from ...query import Query
from ...returned_types import ReturnedTypes

@dataclass
class CacheMiddleware(Middleware):
    """Не использовать. Нужно потом доделать"""
    cached_methods: List[Dict[str, List[str]]]
    cache_type: CacheType = CacheType.SAVE_BY_USER
    
    async def add(self, key, value, **kwargs):
        pass
    async def get(self, key, **kwargs):
        pass
    
    def _has_method(self, name: str):
        for cached_method in self.cached_methods:
            if name in cached_method['methods']:
                return True
        return False

    async def on_before_request(self, query: Query):
        if self._has_method(query.query_name):
            self.gql.logger(f"CacheMiddleware: check {query.query_name} in cache")
            return await self.get(query.query_name)
        
    async def on_after_request(self, responces: ReturnedTypes):
        for responce in responces.keys():
            if self._has_method(responce):
                self.gql.logger.log(f"CacheMiddleware: add {responce} to cache")
                return await self.add(responce, responces[responce])