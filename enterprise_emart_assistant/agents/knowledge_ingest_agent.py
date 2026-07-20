from langgraph.graph import StateGraph
from regex import B

from graphs.state import AgentState
from nodes.knowledge_ingest import init_node


def _register_nodes(builder: StateGraph):

    builder.add_node("init_node", init_node)


def build_knowledge_ingest_agent():
    builder = StateGraph(AgentState)
    
    _register_nodes(builder)
    
    builder.set_entry_point("init_node")

    return builder.compile()


knowledge_ingest_subgraph = build_knowledge_ingest_agent()
