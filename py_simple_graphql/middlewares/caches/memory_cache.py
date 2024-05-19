

from datetime import datetime, time
from typing import Optional
from ..caches.abstract import CacheMiddleware
from ...query import Query


class MemCache(CacheMiddleware):
    cache: dict = {}
    exp: Optional[time] = None
    
    async def add(self, key, value, **kwargs):
        if 'filter' in kwargs:
            key = f"{key}_{kwargs['filter']}"
        self.cache[key] = {
            "value": value,
            "exp": self.exp
        }

    async def get(self, key, **kwargs):
        if 'filter' in kwargs:
            key = f"{key}_{kwargs['filter']}"        
        return self.cache.get(key)

    async def on_before_request(self, query: Query):
        keys = self.cache.keys()
        for key in keys:
            if self.cache[key]["exp"] is not None and self.cache[key]["exp"] < datetime.now().time():
                self.cache.pop(key)
        return super().on_before_request(query)