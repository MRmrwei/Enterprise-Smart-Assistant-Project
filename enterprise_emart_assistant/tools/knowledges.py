from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_skills_adapters import SkillsTool


@tool
def analysis_word(file_path: str):
    """
    通过文件地址获取文件并解析内容返回，上传知识库文档中带有文档地址请调用此工具获取文档内容
    Args:
        file_path: 文件地址 必填
    """

    return """
腾讯公司介绍

腾讯成立于1998年，总部位于中国深圳，是一家世界领先的互联网科技公司。2004年于香港联合交易所主板上市，股票代码为00700[citation:4][citation:11]。公司以“用户为本，科技向善”为使命愿景，致力于用创新的产品和服务提升全球各地人们的生活品质[citation:4]。

【发展历程与业务演变】
腾讯的发展史是一部不断“变形”的商业进化史。公司从即时通讯软件起步，在探索盈利模式的过程中，通过模仿日本电信运营商推出增值服务，并在与中国移动合作“移动梦网”业务后，于2001年首次实现单月盈亏平衡，成为中国最早盈利的互联网公司之一[citation:2]。
2004年上市前后，腾讯完成了第一次重大转型。通过推出QQ秀、QQ空间、QQ游戏等产品，互联网增值服务收入快速增长，成功摆脱了对“移动梦网”业务的依赖，构建起在社交领域的优势[citation:2]。此后，腾讯主动进军游戏业务，在经历初期挫折后，凭借《穿越火线》《地下城与勇士》等爆款产品及对Riot Games的投资，确立了游戏领域的统治地位。到2011年，网络游戏收入已占全年总收入的一半以上[citation:2]。
2011年，微信的推出成为腾讯发展史上的又一关键转折点。这款产品不仅帮助腾讯在移动互联网时代锁定了胜局，更推动其从一家互联网产品公司，成长为横跨社交、游戏、内容、金融与产业互联网的超级平台型企业[citation:2][citation:7]。近年来，随着2018年确立“科技向善”使命及2021年将“可持续社会价值创新”纳入核心战略，腾讯已无法用单一业务来定义，其业务版图和价值主张持续扩展[citation:5][citation:8]。

【核心业务板块】
目前，腾讯的业务主要由四大板块构成[citation:1][citation:6]：
1.  **增值服务**：主要包括网络游戏（如《王者荣耀》《和平精英》等长青游戏）和视频号直播、视频付费会员等社交网络服务。
2.  **营销服务**：涵盖媒体广告、社交及其他广告业务，智能投放产品矩阵和视频号广告是重要增长引擎。
3.  **金融科技及企业服务**：提供商业支付、金融科技及腾讯云等服务，助力企业实现数字化转型。
4.  **其他业务**：包括为第三方制作与发行电影电视节目、内容授权及商品销售等。
"""

    # from aspose import words_foss
    # word = words_foss.Document(file_path)

    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=350,  # 每块 350 字（中文约 400 Token）
    #     chunk_overlap=50,
    #     separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    #     length_function=len,
    # )
    # texts = splitter.split_text(word.get_text())
    # docs = [Document(text, metadata={"xxs":333}) for text in texts]
    # print("文档内容：")
    # [print(f"{doc}\n----------------------------------------------\n") for doc in docs]


@tool
def upload_knowledge(docs: str):
    """
    将接收到的字符串内容上传到向量数据库，如用户需要把内容上传到向量数据库中，请调用此工具
    Args:
        docs: 接收到的字符串内容
    """

    return "上传成功， id1559"


skills = SkillsTool(skills_path="./skills/knowledge/")
skills.name = "knowledge_skills"
