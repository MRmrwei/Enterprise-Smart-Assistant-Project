from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from graphs.state import AgentState
from nodes.fill_form import form_create_node, confirm_node,router,completed_node
from tools.forms import leave_request


def _register_nodes(builder: StateGraph):
    tools = [leave_request]
    builder.add_node("form_create", form_create_node)
    builder.add_node("confirm_node", confirm_node)
    builder.add_node("finish_node", completed_node)
    builder.add_node("tools", ToolNode(tools, messages_key="fill_form_messages"))


def build_fill_form_agent() -> StateGraph:
    builder = StateGraph(AgentState)
    _register_nodes(builder)

    builder.set_entry_point("form_create")
    builder.add_edge("form_create", "confirm_node")
    builder.add_conditional_edges("confirm_node", router)
    builder.add_edge("tools", "finish_node")

    return builder.compile()


fill_form_subgraph = build_fill_form_agent()
