from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import time
from db.vector import vector_store
import random


class RagUploadService:
    async def upload(
        self,
        file_path: str,
        filename,
        chunk_strategy: str,
        department: str,
        version: int,
        doc_type: str,
    ):
        print("上传文件")

        docs: list[Document] = []
        if chunk_strategy == "general":
            docs = self.recursive_char_documen(file_path)
        elif chunk_strategy == "parent_child":
            docs = self.parent_recursive_document(file_path)
        else:
            raise ValueError("chunk_strategy 参数错误")

        for doc in docs:
            doc.metadata["filename"] = filename
            doc.metadata["department"] = department
            doc.metadata["version"] = version
            doc.metadata["doc_type"] = doc_type
            doc.metadata["create_time"] = int(time.time())

        # [print(doc.metadata) for doc in docs]

        # 存入向量数据库
        try:
            res = vector_store.add_documents(docs)
        except Exception as e:
            print(e)
            raise e
        print(f"添加向量数据库成功---> {res}")

    def parent_recursive_document(self, file_path: str) -> list[Document]:
        """
        父子块文档切分：
        - 父块 1000 字，叠块 150 字，最后一段不足 600 字则并入前一个父块
        - 子块 200 字，叠字 30 字
        返回父子块混合的 list[Document]，通过 metadata.chunk_type 区分 parent/child
        """
        # 1. 加载文本
        loader = TextLoader(file_path, encoding="utf-8")
        full_text = loader.load()[0].page_content

        # 2. 父块切分
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "!", "?", " ", ""],
            length_function=len,
        )
        parent_texts = parent_splitter.split_text(full_text)

        # 3. 末段不足 600 字则合并到前一个父块
        if len(parent_texts) > 1 and len(parent_texts[-1]) < 600:
            parent_texts[-2] = parent_texts[-2] + parent_texts[-1]
            parent_texts.pop()

        # 4. 子块切分 & 组装结果
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=30,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "!", "?", " ", ""],
            length_function=len,
        )

        result: list[Document] = []
        only_id = self.generate_random_number(15)
        for parent_idx, parent_text in enumerate(parent_texts):
            parent_id = f"parent_{parent_idx + 1}"

            # 父块
            result.append(
                Document(
                    page_content=parent_text,
                    metadata={
                        "doc_id": parent_id,
                        "chunk_type": "parent",
                        "chunk_index": parent_idx,
                        "source": file_path,
                        "only_id": only_id,
                    },
                )
            )

            # 子块
            child_texts = child_splitter.split_text(parent_text)
            for child_idx, child_text in enumerate(child_texts):
                result.append(
                    Document(
                        page_content=child_text,
                        metadata={
                            "doc_id": f"{parent_id}_child_{child_idx}",
                            "parent_id": parent_id,
                            "chunk_type": "child",
                            "chunk_index": child_idx,
                            "source": file_path,
                            "only_id": only_id,
                        },
                    )
                )

        return result

    def recursive_char_documen(self, file_path: str) -> list[Document]:
        """
        递归块文档
        """
        loader = TextLoader(file_path, encoding="utf-8")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "!", "?", " ", ""],
            length_function=len,
        )

        docs = loader.load_and_split(splitter)
        only_id = self.generate_random_number(15)
        for index, doc in enumerate(docs):
            doc.metadata["source"] = file_path
            doc.metadata["chunk_type"] = "recursive_char"
            doc.metadata["chunk_index"] = index
            doc.metadata["doc_id"] = index + 1
            doc.metadata["only_id"] = only_id
        return docs

    def generate_random_number(self, length):
        """
        生成指定长度的随机数字，首位不能为0

        参数:
            length: 数字的长度
        返回:
            随机数字字符串
        """
        first = str(random.randint(1, 9))  # 第一位1-9
        rest = "".join(
            str(random.randint(0, 9)) for _ in range(length - 1)
        )  # 剩余位0-9
        return first + rest
