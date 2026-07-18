from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from graphs.state import AgentState
from nodes.fill_form import form_create_node,form_init_node, confirm_node, router, completed_node
from tools.forms import leave_request, form_skills

def _register_nodes(builder: StateGraph):
    builder.add_node("form_init", form_init_node)
    builder.add_node("load_skill", ToolNode([form_skills], messages_key="fill_form_messages"))
    builder.add_node("form_create", form_create_node)
    builder.add_node("router", router)
    builder.add_node("confirm", confirm_node)
    builder.add_node("finish", completed_node)
    builder.add_node("tools", ToolNode([leave_request], messages_key="fill_form_messages"))


def build_fill_form_agent() -> StateGraph:
    builder = StateGraph(AgentState)
    _register_nodes(builder)

    builder.set_entry_point("form_init")
    builder.add_edge("form_init", "load_skill")
    builder.add_edge("load_skill", "form_create")
    builder.add_edge("form_create", "confirm")
    
    
    builder.add_conditional_edges("confirm", router)

    builder.add_edge("tools", "finish")

    return builder.compile()


fill_form_subgraph = build_fill_form_agent()
