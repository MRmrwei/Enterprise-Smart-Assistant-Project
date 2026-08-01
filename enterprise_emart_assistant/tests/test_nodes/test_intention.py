import json

from langchain_core.messages import SystemMessage, HumanMessage

from nodes.intention import INTENTION_SYSTEM_PROMPT,intention_llm


def test_get_intention():
    llm = intention_llm()
    res = llm.invoke(
        [
            SystemMessage(content=INTENTION_SYSTEM_PROMPT),
            HumanMessage(content="公司的年假怎么放"),
        ]
    )
    intentions = json.loads(res.content)
    print(intentions)
