import tempfile
import os
from contextlib import contextmanager
import requests
import tempfile
import os
from urllib.parse import urlparse, unquote


@contextmanager
def remote_document(url: str, supports: list[str]):
    """
    下载远程文档到临时文件，自动清理

    Args:
        url: 文件下载链接

    Yields:
        str: 临时文件路径

    Example:
        for file_path in remote_document("http://example.com/file.docx"):
            # 处理文件
            print(f"文件已下载到: {file_path}")
            # 退出循环后自动删除
    """
    # 1. 下载文件
    response = requests.get(url)
    response.raise_for_status()  # 检查下载是否成功
    content = response.content

    # 2. 从URL中提取文件后缀
    suffix = ""  # 默认后缀
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)  # 解码URL编码（处理中文）

    if "." in path:
        # 提取最后一个点后面的部分作为后缀
        ext = path.split(".")[-1]
        # 过滤掉明显不是后缀的情况
        if ext and len(ext) < 8 and ext.isalnum():
            suffix = f".{ext}"

    if suffix.lstrip(".") not in supports:
        raise Exception("不支持的文件格式")

    # 3. 创建临时文件
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="wb") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 4. 返回文件路径
        yield tmp_path
    finally:
        # 5. 自动清理临时文件
        try:
            os.unlink(tmp_path)
        except Exception:
            pass  # 忽略删除失败的错误
