from langgraph.graph import StateGraph

from graphs.state import AgentState
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from nodes.router import route_node
from nodes.intention import intention_node
from nodes.auth import auth_permission_node
from agents.fill_form_agent import fill_form_subgraph
from agents.knowledge_ingest_agent import knowledge_ingest_subgraph
from langgraph.checkpoint.memory import InMemorySaver
from tools.base import tools_container
from pydantics.intentions import Intention



def _init_node(state: AgentState):
    return {
        "fill_form_messages": [],
        "answer": "",
        "intentions": {},
    }


def _register_nodes(builder: StateGraph):
    builder.add_node("init_node", _init_node)
    builder.add_node("intention_node", intention_node)
    builder.add_node("route_node", route_node)
    builder.add_node("auth_permission", auth_permission_node)
    builder.add_node("fill_form", fill_form_subgraph)
    builder.add_node("knowledge_ingest", knowledge_ingest_subgraph)


def build_graph():
    builder = StateGraph(AgentState)
    _register_nodes(builder)

    builder.set_entry_point("init_node")
    builder.add_edge("init_node", "intention_node")
    builder.add_edge("intention_node", "auth_permission")

    builder.add_edge("auth_permission", "route_node")

    # ✅ 创建带允许列表的序列化器
    serde = JsonPlusSerializer(allowed_msgpack_modules=[Intention])

    # ✅ 使用自定义序列化器初始化 checkpointer
    checkpointer = InMemorySaver(serde=serde)

    return builder.compile(checkpointer=checkpointer)


main_graph = build_graph()
