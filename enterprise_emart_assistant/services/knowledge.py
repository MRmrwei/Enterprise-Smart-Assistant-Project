import json

from aspose import words_foss
from click import prompt
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
import time
from db.vectors.vector import vector_store
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llms.factory import get_default_llm
from langchain_community.document_loaders import TextLoader


def upload_knowledge(path: str, **kwargs):
    
    loader = TextLoader(path, encoding="utf-8")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=350,  # 每块 350 字（中文约 400 Token）
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        length_function=len,
    )

    documents = loader.load_and_split(splitter)
    timestamp = int(time.time())
    for doc_key, doc in enumerate(documents):
        doc.metadata["chunk_index"] = doc_key
        doc.metadata["create_time"] = timestamp
        doc.metadata = {**doc.metadata, **kwargs}
        
    res = vector_store.add_documents(documents)
    print(res)