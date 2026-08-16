import asyncio

from db.rerank.ollama import OllamaReranker
from db.vectors.vector import vector_store


def test_rerank():
    reranker = OllamaReranker()
    q = "有关销售经理的内容"
    docs = vector_store.similarity_search(q, k=50)
    res = asyncio.run(reranker.arerank(q, docs))
    # print(f"res len = {len(res)}")
    # [print(f"res = {doc}\n") for doc in res]
