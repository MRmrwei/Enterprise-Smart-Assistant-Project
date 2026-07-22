from langchain_core.tools import tool
@tool
def qa_query() -> str:
    """
    查询关于公司的制度、假期、员工福利等关于本公司的内容请调用该工具
    """
    return "公司5天工作制，周六周日双休"
