import redis

from db.caches.base import BaseCache
from configs.config import config


class Redis(BaseCache):

    client: redis.Redis | None = None

    def __init__(self):
        prot = config.get("CACHE_PORT", 6379)
        db = config.get("CACHE_DB", 0)
        host = config.get("CACHE_HOST", "127.0.0.1")
        max_conn = config.get("CACHE_MAX_CONN", 20)
        conn = redis.ConnectionPool(
            host=host, port=prot, db=db, max_connections=max_conn,socket_timeout=5,decode_responses=True
        )
        self.client = redis.Redis(connection_pool=conn)

    def get(self, key, default=None):
        return self.client.get(key) or default


    def set(self, key, value):
        return self.client.set(key, value)
        
    
    def setex(self, key, value, seconds: int):
        return self.client.setex(key, seconds, value)
    
    
    def delete(self, key):
        return self.client.delete(key)
    
    def expire(self, key, seconds: int):
        return self.client.expire(key, seconds)
    
    
    def ttl(self, key):
        return self.client.ttl(key)
    