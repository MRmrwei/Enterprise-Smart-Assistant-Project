from graphs.state import AgentState
from langgraph.types import Command
from langgraph.config import get_stream_writer

from pydantics.intentions import Intention


def route_node(state: AgentState):

    intentions: Intention | None = state.get("intentions", None)

    if intentions is None:
        return Command(goto="completed", update={"answer": "意图识别失败"})

    return Command(goto=intentions.type)
