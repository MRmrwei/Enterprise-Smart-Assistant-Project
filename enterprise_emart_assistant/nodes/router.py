from langgraph.graph import END

from enums.intentions import Intentions
from graphs.state import AgentState
from langgraph.types import Command

from pydantics.intentions import Intention


def route_node(state: AgentState):
    intentions: Intention | None = state.get("intentions", None)

    if intentions is None:
        return Command(goto=END)
    elif intentions.type == Intentions.UNKNOWN.value:
        print("Unknown Intention")
        return Command(goto="chat_node")

    return Command(goto="executor_agent")
