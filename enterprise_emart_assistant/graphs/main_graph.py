from langgraph.graph import StateGraph

from graphs.state import AgentState

from nodes.router import route_node
from nodes.intention import intention_node
from nodes.auth import auth_permission_node
from agents.fill_form_agent import fill_form_subgraph
from langgraph.checkpoint.memory import InMemorySaver


def _register_nodes(builder: StateGraph):
    builder.add_node("intention_node", intention_node)
    builder.add_node("route_node", route_node)
    builder.add_node("auth_permission", auth_permission_node)
    builder.add_node("fill_form", fill_form_subgraph)


def build_graph():
    builder = StateGraph(AgentState)
    _register_nodes(builder)

    builder.set_entry_point("intention_node")
    builder.add_edge("intention_node", "auth_permission")

    builder.add_edge("auth_permission", "route_node")

    return builder.compile(checkpointer=InMemorySaver())


main_graph = build_graph()
