from datetime import datetime
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage, SystemMessage, SystemMessageChunk

from graphs.state import AgentState
from llms.factory import get_default_llm
from tools.forms import leave_request

llm_with_tools = get_default_llm().bind_tools([leave_request], strict=True)


def _get_create_system_prompt() -> str:
    return f"""
    你是一位智能填单专家。结合意图描述和用户原话，合理调用工具生成一个符合要求的填单。
    背景信息：
    - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
    注意：
    - 根据意图描述，尽可能推断出所有字段的值。
    - 只有当关键字段确实无法推断时，才询问用户补全。
    - 询问时只需问缺少的数据，不要输出其他内容。
    - 信息完整后需要用户确认时，只输出确认内容，不要额外废话。
    - 返回的信息必须包含已确认的信息
    - 必须要用户确认后才能调用工具。
    """


async def form_create_node(state: AgentState):

    # print(f"state = {state}")

    origin_input = state.get("intentions", {}).get("origin_input")
    description = state.get("intentions", {}).get("description")
    message = await llm_with_tools.ainvoke(
        [
            SystemMessage(
                content=f"{_get_create_system_prompt()}\n意图描述：{description}\用户原话：{origin_input}"
            ),
        ]
    )
    return {"fill_form_messages": [message]}


def _get_confirm_system_prompt() -> str:
    return f"""
    你是单据确认助手。根据上下文来引导用户填写数据。
    背景信息：
    - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
    注意：
    - 如果数据已经补全，对用户发送确认请求的话语。
    - 如果数据已经补全也和用户确认过。立即根据上下文判断使用工具。
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
    print("router: ", last_message)
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "confirm_node"


def _get_completed_system_message(state: AgentState):
    return f"""

  
  
  """

def completed_node(state: AgentState):
    messages = state.get("fill_form_messages", [])
    print("completed_node: ", messages[-1].content)
    return {"answer": state.get("answer", "")}