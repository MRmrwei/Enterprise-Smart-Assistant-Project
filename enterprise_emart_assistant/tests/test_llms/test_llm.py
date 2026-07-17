from langchain_core.messages import SystemMessage,HumanMessage

from llms.factory import get_default_llm, get_llm


def test_llm():
    llm = get_default_llm()
    print(llm.invoke([
        SystemMessage(content="你是知性的大姐姐，回答用户所提出的问题。根据事实回答。"),
        HumanMessage(content="你是男生女生")
    ]).content)