from langchain_core.documents import Document
from db.vectors.vector import get_vector_store
from db.rerank.factory import reranker


async def mixed_parent_search(question: str, k=5):
    """
    ***混合搜索+父子块搜索***
    1.使用向量搜索。
    1.使用重排筛选
    2.子块去重吗，父块召回
    """
    docs = await rerank_search(question, await asimilarity_search(question, k))

    # [
    #     print(
    #         f"所有：{doc.metadata.get('only_id')} ---- {doc.metadata.get('chunk_type')}"
    #     )
    #     for doc in docs
    # ]
    # 收集所有 parent 块的 only_id
    parent_ids = {
        doc.metadata.get("only_id")
        for doc in docs
        if doc.metadata.get("chunk_type") == "parent"
        and doc.metadata.get("only_id") is not None
    }

    # 去重：child 按 only_id 去重，且排除与 parent 同 only_id 的 child
    seen_ids = set()
    deduped: list[Document] = []
    for doc in docs:
        only_id = doc.metadata.get("only_id")
        if doc.metadata.get("chunk_type") == "child":
            # parent 已召回同名 only_id，跳过该 child
            if only_id in parent_ids:
                continue
            # child 自身按 only_id 去重
            if only_id is not None:
                if only_id in seen_ids:
                    continue
                seen_ids.add(only_id)
        deduped.append(doc)

    # [
    #     print(
    #         f"deduped ==={doc.metadata.get('only_id')} ---- {doc.metadata.get('chunk_type')}"
    #     )
    #     for doc in deduped
    # ]

    # 对 child 召回父块，替换 child 为 parent
    result: list[Document] = []
    for doc in deduped:
        if doc.metadata.get("chunk_type") == "child":
            parent_docs = parent_search(doc)
            if parent_docs:
                result.extend(parent_docs)
                continue
        result.append(doc)

    # [
    #         print(
    #             f"result ==={doc.metadata.get('only_id')} ---- {doc.metadata.get('chunk_type')}"
    #         )
    #         for doc in result
    #     ]
    return result


def mixed_search(question: str) -> list[Document]:
    """
    混合搜索，使用向量搜索与bm25搜索
    """
    return get_vector_store().similarity_search(question, k=30)


async def asimilarity_search(question: str, k: int = 3) -> list[Document]:
    """语义搜索"""
    docs = await get_vector_store().asimilarity_search(question, k)
    return docs


def bm25_search(question: str, k: int = 3) -> list[Document]:
    """
    bm25搜索
    需要同时维护BM25索引，暂不实现
    或者换成milvue2.4以上，支持bm25
    """
    pass


def parent_search(doc: Document) -> list[Document]:
    """
    父块召回：根据子块的 parent_id 从向量数据库查找对应的父块并返回
    """

    only_id = doc.metadata.get("only_id")

    if not only_id:
        raise ValueError("缺少唯一id")

    parent_id = doc.metadata.get("parent_id")
    if not parent_id:
        raise ValueError("缺少父块ID")

    result = get_vector_store().get(
        where={
            "$and": [
                {"chunk_type": "parent"},
                {"doc_id": parent_id},
                {"only_id": only_id},
            ]
        }
    )

    docs = []
    for i, doc_id in enumerate(result.get("ids", [])):
        docs.append(
            Document(
                id=doc_id,
                page_content=result["documents"][i],
                metadata=result["metadatas"][i] if result.get("metadatas") else {},
            )
        )

    return docs


async def rerank_search(question: str, docs: list[Document]) -> list[Document]:
    """
    重排筛选
    """
    if len(docs) == 0:
        return []

    docs = await reranker.arerank(question, docs)
    return docs
