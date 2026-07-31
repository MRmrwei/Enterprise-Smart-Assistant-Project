from langgraph.graph import END

from enums.intentions import Intentions
from graphs.state import AgentState
from langgraph.types import Command
from langgraph.config import get_stream_writer

from pydantics.intentions import Intention


def route_node(state: AgentState):
    
    
    writer = get_stream_writer()
    
    writer({"type": "reasoning", "content": "你好，世界！这是一段通过流式传输呈现的文字，模拟打字机的效果。"})
    intentions: Intention | None = state.get("intentions", None)

    if intentions is None:
        return Command(goto=END)
    elif intentions.type == Intentions.UNKNOWN.value:
        return Command(goto="chat_node")

    return Command(goto="executor_agent")
