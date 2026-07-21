from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

@tool
def analysis_word(file_path: str):
    """
    输入：文件路径
    输出：文件内容"""
    from aspose import words_foss
    word = words_foss.Document(file_path)
   
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=350,  # 每块 350 字（中文约 400 Token）
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        length_function=len,
    )
    texts = splitter.split_text(word.get_text())
    docs = [Document(text, metadata={"xxs":333}) for text in texts]
    print("文档内容：")
    [print(f"{doc}\n----------------------------------------------\n") for doc in docs]