import asyncio

from tools.knowledges import upload_file_knowledge


def test_file_upload():
    url = "http://www.filedown.com/向量数据库11.doc"
    res  = asyncio.run(upload_file_knowledge(url))
    print(res)