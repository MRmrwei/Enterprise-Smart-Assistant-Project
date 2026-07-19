from datetime import datetime
import json

from langchain_core.messages import HumanMessage, SystemMessage

from enums.intentions import Intentions
from graphs.state import AgentState
from llms.factory import get_default_llm
from prompts.intention import get_intention_system_prompt
from pydantics.intentions import Intention




def intention_llm():
    llm = get_default_llm().with_structured_output(Intention, method="json_mode")
    return llm


async def intention_node(state: AgentState):
    """
    意图识别节点
    """
    messages = state.get("messages")
    message = messages[-1]

    intentions:Intention = await intention_llm().ainvoke(
        [SystemMessage(get_intention_system_prompt()), message]
    )
    intentions.origin_input = message.content
    print(intentions)
    state.update(
        {
            "intentions": intentions
        }
    )
    return state
