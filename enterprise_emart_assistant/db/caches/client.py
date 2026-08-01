from configs.config import config
from db.caches.base import BaseCache
from db.caches.drives.redis import Redis
from db.caches.drives.local import LoacalCache


def _getCache() -> BaseCache:
    tpye = config.get("CACHE", "local")
    if tpye == "redis":
        return Redis()
    elif tpye == "local":
        return LoacalCache()
    raise Exception("暂不支持的缓存驱动")


cache = _getCache()
