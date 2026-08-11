from datetime import datetime
import json

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.config import get_stream_writer
from enums.intentions import Intentions
from graphs.state import AgentState
from llms.factory import get_default_llm
from prompts.intention import get_intention_system_prompt
from pydantics.intentions import Intention


def intention_llm():
    llm = get_default_llm().with_structured_output(
        Intention, method="json_mode", include_raw=True
    )

    return llm


async def intention_node(state: AgentState):
    """
    意图识别根据意图选择skill节点
    """
    question = state.get("messages", [])[-1]
    response = await intention_llm().ainvoke(
        [SystemMessage(get_intention_system_prompt()), question]
    )

    intentions: Intention = response["parsed"]

    print(f"意图: {intentions}")
    # state.update(
    #     {
    #         "intentions": intentions
    #     }
    # )

    state["intentions"] = intentions
    writer = get_stream_writer()
    writer({"type": "reasoning", "content": intentions.description})
    return state
