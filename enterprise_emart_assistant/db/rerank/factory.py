from db.rerank.ollama import OllamaReranker
from db.rerank.base import BaseReranker


def reranker_factory() -> BaseReranker:
    # 暂时实现ollama的重排
    return OllamaReranker()

reranker = reranker_factory()
