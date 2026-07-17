import json

from langchain_core.messages import HumanMessage, SystemMessage

from graphs.state import AgentState
from llms.factory import get_default_llm

INTENTION_SYSTEM_PROMPT = """你是一位意图分析专家。请根据用户输入判断其意图，并输出JSON格式的分析结果。

可选的任务类型：
- qa: 制度/知识问答
- fill_form: 智能填单（请假/报销）
- knowledge_ingest: 文档上传与知识入库
- data_query: 个人数据查询（工资/考勤/报销）
- unknown: 一般问答、知识查询、闲聊等

输出格式（严格JSON）：
{
    "intention_type": "data_query|qa|fill_form|knowledge_ingest|unknown",
    "description": "任务描述",
}

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

    state["intention_type"] = intentions.get("intention_type", "unknown")
    state["intention_description"] = intentions.get("description", "")

    return state
