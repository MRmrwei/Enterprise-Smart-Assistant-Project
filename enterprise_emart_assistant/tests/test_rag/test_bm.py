import bm25s

from services.rags.search import bm25_search
from db.vector import vector_store
import jieba
import re


def test_bm():

    def tokenize_mixed(text):
        """
        适用于中英文混合文本的分词器
        """
        # 1. 去除特殊符号（保留字母、数字、中文），防止干扰
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", " ", text)

        # 2. 使用 jieba 精确模式分词
        #    jieba 非常智能，能自动识别英文单词（如 Python 不会被拆成 P y t h o n）
        tokens = jieba.lcut(text)

        # 3. 过滤掉空白字符，并将英文统一转为小写（保证大小写不敏感）
        tokens = [t.lower().strip() for t in tokens if t.strip()]
        return tokens

    corpus = [
        "机器学习是人工智能的一个分支，主要研究算法。",
        "Python is a popular programming language for data science.",
        "Transformer 模型在自然语言处理（NLP）任务中表现优异。",
        "深度学习和神经网络是实现人工智能的重要手段。",
        "BM25 is widely used in information retrieval systems.",
    ]

    tokenized_corpus = [tokenize_mixed(doc) for doc in corpus]
    print(f"tokenized_corpus = {tokenized_corpus}")
    retriever = bm25s.BM25()
    retriever.index(tokenized_corpus)

    # # 1. 定义查询语句（中英文混合）
    query = "人工智能和Python的关系"

    # # 2. 对查询进行分词
    tokenized_query = tokenize_mixed(query)
    print(f"tokenized_query = {tokenized_query}")

    # # 3. 执行检索，返回 Top-3 结果
    # #    注意：retrieve 方法要求传入二维列表（支持批量查询），所以用 [tokenized_query]
    results, scores = retriever.retrieve(
        [tokenized_query],  # 查询列表
        corpus=corpus,  # 传入原始语料，方便直接返回文本内容
        k=3,  # 返回前 3 个结果
    )

    # 测试一下
    # 4. 打印结果
    print(f"查询词: {query}")
    print("=" * 40)
    for doc, score in zip(results[0], scores[0]):
        print(f"得分: {score:.4f} | 文档: {doc}")
