import json

from aspose import words_foss
from click import prompt
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_skills_adapters import SkillsTool

from llms.factory import get_default_llm
from services.file import remote_document

# @tool
# def upload_str_knowledge(file_path: str):
#     pass


# @tool
async def upload_file_knowledge(file_url: str) -> str:

    try:
        with remote_document(file_url, ["doc", "docx"]) as path:
            word = words_foss.Document(path).get_text()
            # print(f"文件已下载到: {word.get_text()}")
    except Exception as e:
        return f"下载失败：{e}"

    prompt = """
        【系统指令】
        你是一个文档切割工具，不是作家、编辑或摘要员。唯一职责是裁剪文本。

        【最高优先级约束 - 必须首先执行】
        1. 零修改原则：输出的每段内容必须与下方【原文档】中的原文逐字逐句完全一致。不得修改任何标点、术语、数字、空格、引用标记（如[citation:X]）、加粗符号（**）。严禁改写、总结、润色、压缩或翻译。
        2. 严禁添加：禁止添加任何"上下文锚点"、"核心主题"、"本文档关于XXX部分"等额外文字。只输出原文片段本身。

        【分块约束】
        3. 块大小：每块内容长度控制在300-500个字符（含标点符号、英文、数字、空格）。注意：是"字符"不是"汉字"。
        4. 切割边界：必须在句号（。）问号（？）感叹号（！）或段落换行（\n\n）处切割。严禁在逗号、分号、冒号处切断句子。
        5. 语义保护：如某个自然段落在300-500字之间，则保留该段落为独立一块，不拆分。
        6. 完整性：如遇到列表（1. 2. 3. 或 - 项目），必须将整个列表视为一个整体，禁止将列表项拆散到不同块中。
        ## 请返回json格式：
            ["块1", "块2"]
    """
    res = await get_default_llm(response_format={"type": "json_object"}).ainvoke(
        [SystemMessage(content=prompt), HumanMessage(content=f"文档内容：\n{word}")]
    )
    
    chunk = json.loads(res.content)

    print(f"res = {res.content}")


skills = SkillsTool(skills_path="./skills/knowledge/")
# skills.verbose=True
skills.name = "knowledge_skills"
