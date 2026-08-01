from langchain_community.document_loaders import TextLoader, Docx2txtLoader
from aspose import words_foss
from langchain_core.documents import Document
import requests
from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.file import remote_document


def test_open_file():
    doc1 = "C:/Users/宝🐖/Desktop/向量数据库11.doc"
    doc2 = "C:/Users/宝🐖/Desktop/向量数据库22.docx"

    word = words_foss.Document(doc1)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=350,  # 每块 350 字（中文约 400 Token）
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        length_function=len,
    )
    texts = splitter.split_text(word.get_text())
    docs = [Document(text, metadata={"xxs": 333}) for text in texts]
    print("文档内容：")
    [print(f"{doc}\n----------------------------------------------\n") for doc in docs]


def test_down_file():
    url = "http://www.filedown.com/向量数据库22.docx"

    try:
        with remote_document(url, ["doc", "docx"]) as path:
            word = words_foss.Document(path)
            print(f"文件已下载到: {word.get_text()}")
    except Exception as e:
        print(f"下载失败：{e}")

    # response = requests.get(url)
    # print(f"结果：{response}")
    