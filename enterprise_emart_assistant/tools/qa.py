from langchain_core.tools import tool
from db.vectors.vector import get_vector_store
from llms.factory import get_default_llm


@tool
async def qa_query(question: str) -> str:
    """
    查询关于公司的制度、假期、员工福利等关于本公司的内容请调用该工具
    Args:
        question: 问题
    """


    docs = await get_vector_store().asimilarity_search(question, k=3)
    
    context = [f"{doc.page_content}\n" for doc in docs]
    
    return context
