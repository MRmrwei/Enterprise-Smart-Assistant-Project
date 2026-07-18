

from graphs.state import AgentState
from langgraph.types import Command


def route_node(state: AgentState):
    
    return Command(goto="fill_form")