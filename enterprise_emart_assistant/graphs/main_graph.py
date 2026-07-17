from langgraph.graph import StateGraph

from graphs.state import AgentState

from nodes.router import route_node
from nodes.intention import intention_node
from nodes.auth import auth_permission


def _register_nodes(builder: StateGraph):
    builder.add_node("intention_node", intention_node)
    builder.add_node("route_node", route_node)


def build_graph():
    builder = StateGraph(AgentState)
    _register_nodes(builder)

    builder.set_entry_point("intention_node")

    builder.add_conditional_edges("intention_node", auth_permission)
    
    return builder.compile()


main_graph = build_graph()
