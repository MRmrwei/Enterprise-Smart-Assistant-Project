from db.caches.base import BaseCache
from configs.config import config
from cacheout import Cache
from typing import Optional


class LoacalCache(BaseCache):
    """
    本地缓存
    """

    client: Cache | None = None

    def __init__(self):
        """
        初始化缓存

        maxsize: 最大容量
        default_ttl: 默认过期时间（秒）
        """
        default_ttl = config.get("CACHE_DEFAULT_TTL", 86400)
        self.client = Cache(
            maxsize=config.get("CACHE_MAX_SIZE", 1000),
            ttl=default_ttl,  # 默认 TTL
            timer=lambda: int(__import__("time").time()),  # 使用整数时间戳
        )
        self._default_ttl = default_ttl

    def get(self, key: str, default=None):
        """获取缓存值"""
        return self.client.get(key, default)

    def set(self, key: str, value):
        """设置缓存，使用默认过期时间"""
        self.client.set(key, value)

    def setex(self, key: str, value, seconds: int):
        """设置缓存并指定过期时间（秒）"""
        self.client.set(key, value, ttl=seconds)

    def delete(self, key: str):
        """删除缓存"""
        self.client.delete(key)

    def expire(self, key: str, seconds: int):
        """设置 key 的过期时间"""
        if key not in self.client:
            return False

        # 获取当前值
        value = self.client.get(key)
        if value is not None:
            # 重新设置并指定新的 TTL
            self.client.set(key, value, ttl=seconds)
            return True
        return False

    def ttl(self, key: str) -> int:
        """获取 key 的剩余过期时间（秒）"""
        if key not in self.client:
            return -2

        # cacheout 没有直接获取 TTL 的方法，需要自己计算
        # 这里通过内部属性获取（不同版本可能不同）
        try:
            # 获取缓存项的过期时间戳
            item = self.client._Cache__cache.get(key)
            if item is None:
                return -2

            # 获取当前时间
            import time

            remaining = int(item.expiry - time.time())
            if remaining <= 0:
                self.delete(key)
                return -2

            return remaining
        except AttributeError:
            # 如果无法获取内部属性，返回 -1（表示存在但未知剩余时间）
            return -1

    def flush(self):
        """清空所有缓存"""
        self.client.clear()

    def __len__(self):
        return len(self.client)
