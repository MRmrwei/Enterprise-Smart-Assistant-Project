from db.caches.client import cache
from db.caches.client import _getCache
def test_local():
    cache.setex("test", "test1", 10)
    print(cache.ttl("test"))