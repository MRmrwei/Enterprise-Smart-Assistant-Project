from abc import ABC, abstractmethod


class BaseCache(ABC):
    @abstractmethod
    def get(self, key: str, default=None):
        pass

    @abstractmethod
    def set(self, key: str, value):
        pass

    @abstractmethod
    def setex(self, key, value, seconds: int):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass

    @abstractmethod
    def expire(self, key: str, seconds: int):
        pass

    @abstractmethod
    def ttl(self, key: str) -> int:
        pass

    @abstractmethod
    def flush(self):
        pass
