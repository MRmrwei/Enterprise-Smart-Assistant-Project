from datetime import datetime
from langchain_skills_adapters import SkillsTool
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage, SystemMessage, SystemMessageChunk
from graphs.state import AgentState
from llms.factory import get_default_llm
from prompts.fill_form import (
    get_confirm_system_prompt,
    get_decisio_system_prompt,
    get_init_system_prompt,
)
from pydantics.decision import AIDecision
from pydantics.intentions import Intention
from tools.forms import form_all_tools, form_skills

"""
采用工具加skills进行填单使其更具可维护性和扩展性。后续扩展只需要增加工具和skill即可。
"""

tools = form_all_tools + form_skills
llm_with_tools = get_default_llm().bind_tools(tools, strict=True)
llm_with_decision = get_default_llm().with_structured_output(
    AIDecision, method="json_mode"
)


def extract_info(intentions: Intention | None = None) -> str:
    """
    从意图中提取信息
    """
    if intentions is None:
        return ""
    origin_input = intentions.origin_input
    description = intentions.description
    vital_content = intentions.vital_content

    return f"\n意图描述：{description}\n用户原话：{origin_input}\n重要信息：{vital_content}"


async def form_init_node(state: AgentState):
    """填单节点初始化"""
    # print(f"state = {state}")

    intentions: Intention = state.get("intentions", None)

    message = await llm_with_tools.ainvoke(
        [SystemMessage(content=f"{get_init_system_prompt()}{extract_info(intentions)}")]
    )

    return {"fill_form_messages": [message]}


async def form_create_node(state: AgentState):
    """
    填单草稿创建节点
    """
    intentions: Intention = state.get("intentions", None)
    mes = state.get("fill_form_messages", [])

    messages = [
        SystemMessage(
            content=f"{get_confirm_system_prompt()}{extract_info(intentions)}"
        )
    ] + state.get("fill_form_messages", [])
    message = await llm_with_tools.ainvoke(messages)

    return {"fill_form_messages": [message]}


async def confirm_node(state: AgentState):

    messages = state.get("fill_form_messages", [])

    # print(f"\n".join([m.content for m in messages]))

    confirm_msg = interrupt(messages[-1].content)

    send_message = (
        [SystemMessage(content=get_confirm_system_prompt())]
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


async def ai_decision(state: AgentState):
    """
    AI决策节点
    """

    fill_form_messages = state.get("fill_form_messages", [])

    if len(fill_form_messages) < 1:
        return "confirm"

    content = "\n".join([m.content for m in fill_form_messages])
    try:
        result: AIDecision = await llm_with_decision.ainvoke(
            [
                SystemMessage(content=get_decisio_system_prompt()),
                HumanMessage(
                    content=f"请根据上下文和工具结果，给出一个AI决策结果：\n{content}"
                ),
            ]
        )
        print(f"判断结果 = {result}")
        return result.node
    except Exception as e:
        return "confirm"
