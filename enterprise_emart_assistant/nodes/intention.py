import json

from langchain_core.messages import HumanMessage, SystemMessage

from enums.intentions import Intentions
from graphs.state import AgentState
from llms.factory import get_default_llm

INTENTION_SYSTEM_PROMPT = f"""你是一位意图分析专家。请根据用户输入判断其意图，并输出JSON格式的分析结果。

可选的意图类型：
- {Intentions.QA.value}: 制度/知识问答
- {Intentions.FILL_FORM.value}: 智能填单（请假/报销）
- {Intentions.KNOWLEDGE_INGEST.value}: 文档上传与知识入库
- {Intentions.DATA_QUERY.value}: 个人数据查询（工资/考勤/报销）
- {Intentions.UNKNOWN.value}: 一般问答、知识查询、闲聊等

输出格式（严格JSON）：
{{
    "type": "意图类型的key",
    "description": "意图描述"
}}

注意：
1. 不要输出任何JSON以外的内容
"""


def intention_llm():
    llm = get_default_llm(response_format={"type": "json_object"})
    return llm


async def intention_node(state: AgentState):
    """
    意图识别节点
    """
    messages = state.get("messages")
    message = messages[-1]

    res = await intention_llm().ainvoke(
        [SystemMessage(INTENTION_SYSTEM_PROMPT), message]
    )
    intentions = json.loads(res.content)

    state.update(
        {
            "intentions": {
                "origin_input": message.content,
                **intentions,
            }
        }
    )
    return state
