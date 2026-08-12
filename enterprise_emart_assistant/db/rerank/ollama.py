import asyncio

import ollama
import re
from langchain_core.documents import Document


class OllamaReranker:
    def __init__(self, model: str = "dengcao/Qwen3-Reranker-0.6B:F16"):
        self.model = model
        self.client = ollama.AsyncClient()

    async def arerank(
        self, query: str, documents: list[Document], top_k: int = 3
    ) -> list[Document]:
        if not documents:
            return []

        # 并发发送所有请求
        tasks = [self._score_document(query, doc) for doc in documents]
        results = await asyncio.gather(*tasks)

        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        # [print(score) for doc, score in results]
        return [doc for doc, _ in results[:top_k]]

    async def _score_document(self, query: str, doc: Document):
        prompt = self._build_prompt(query, doc.page_content)
        try:
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                options={"num_predict": 10, "temperature": 0.0},
            )
            # 从返回的文本中提取 yes/no
            match = re.search(r"\b(yes|no)\b", response["response"], re.IGNORECASE)
            score = 1.0 if match and match.group(1).lower() == "yes" else 0.0
        except Exception as e:
            print(f"Scoring error: {e}")
            score = 0.0
        return (doc, score)

    def _build_prompt(self, query: str, content: str) -> str:
        return (
            "<|im_start|>system\n"
            "Judge whether the Document meets the requirements based on the Query and the Instruct provided. "
            'Note that the answer can only be "yes" or "no".<|im_end|>\n'
            "<|im_start|>user\n"
            f"<Instruct>: Given a web search query, retrieve relevant passages that answer the query\n"
            f"<Query>: {query}\n"
            f"<Document>: {content}\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
            "<think>\n\n</think>\n\n"
        )
