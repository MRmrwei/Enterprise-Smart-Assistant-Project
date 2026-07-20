from langgraph.graph import END

from enums.intentions import Intentions
from graphs.state import AgentState
from langgraph.types import Command

from pydantics.intentions import Intention


def route_node(state: AgentState):
    intentions: Intention | None = state.get("intentions", None)

    if intentions is None:
        return Command(goto=END)
    print(f"意图: {intentions}")
    return Command(goto=intentions.type)
  
    if intentions.type == Intentions.FILL_FORM.value:
        return Command(goto="fill_form_node")
  
    elif intentions.type == Intentions.KNOWLEDGE_INGEST.value:
        return Command(goto="knowledge_ingest")
    else:
        return Command(goto=END)
