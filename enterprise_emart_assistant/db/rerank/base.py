from langchain_core.documents import Document
from abc import ABC, abstractmethod



class BaseReranker(ABC):
    """所有重排器的抽象基类"""

    @abstractmethod
    async def arerank(
        self, query: str, documents: list[Document], top_k: int = 3
    ) -> list[Document]:
        """对文档列表重排序，返回前 top_k 个"""
        pass

