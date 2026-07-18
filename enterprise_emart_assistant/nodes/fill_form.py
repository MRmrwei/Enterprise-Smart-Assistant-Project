from datetime import datetime
from langchain_skills_adapters import SkillsTool
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage, SystemMessage, SystemMessageChunk
from graphs.state import AgentState
from llms.factory import get_default_llm
from tools.forms import leave_request, form_skills

"""
采用工具加skills进行填单使其更具可维护性和扩展性。后续扩展只需要增加工具和skill即可。
"""

tools = [leave_request, form_skills]
llm_with_tools = get_default_llm().bind_tools(tools, strict=True)


def _get_init_system_prompt() -> str:
    return f"""
    你是智能填单专家。结合意图描述和用户原话，选择skill。
    背景信息：
    - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
    
    """


async def form_init_node(state: AgentState):
    """填单节点初始化"""
    # print(f"state = {state}")

    origin_input = state.get("intentions", {}).get("origin_input")
    description = state.get("intentions", {}).get("description")
    message = await llm_with_tools.ainvoke(
        [
            SystemMessage(
                content=f"{_get_init_system_prompt()}\n意图描述：{description}\n用户原话：{origin_input}"
            ),
        ]
    )
    return {"fill_form_messages": [message]}


async def form_create_node(state: AgentState):
    """
    填单草稿创建节点
    """

    messages = [
        SystemMessage(content="你是智能填单专家,根据skill的规则引导用户填单")
    ] + state.get("fill_form_messages", [])
    message = await get_default_llm().ainvoke(messages)
    return {"fill_form_messages": [message]}


def _get_confirm_system_prompt() -> str:
    return f"""
    你是单据引导助手。结合上下文和skill的规则来引导用户填单。
    背景信息：
    - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
    """


async def confirm_node(state: AgentState):

    messages = state.get("fill_form_messages", [])

    # print(f"\n".join([m.content for m in messages]))
    print(len(messages))
    confirm_msg = interrupt(messages[-1].content)

    send_message = (
        [SystemMessage(content=_get_confirm_system_prompt())]
        + messages
        + [HumanMessage(content=confirm_msg)]
    )

    res_message = await llm_with_tools.ainvoke(send_message)

    return {"fill_form_messages": [res_message]}


def router(state: AgentState):
    messages = state.get("fill_form_messages", [])
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "confirm"


def completed_node(state: AgentState):
    messages = state.get("fill_form_messages", [])
    return {"answer": messages[-1].content}
