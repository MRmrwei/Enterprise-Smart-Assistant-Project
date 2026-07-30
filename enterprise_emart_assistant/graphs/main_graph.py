from langgraph.graph import END, StateGraph
from langgraph.config import get_stream_writer
from agents.base import BaseExecutorAgent
from graphs.state import AgentState
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from llms.factory import get_default_llm
from nodes.router import route_node
from nodes.intention import intention_node
from nodes.auth import auth_permission_node
from langgraph.checkpoint.memory import InMemorySaver
from tools.base import tools_container
from pydantics.intentions import Intention
from tools.forms import form_all_tools
from tools.qa import qa_query
from langchain_core.messages import HumanMessage, SystemMessage


def _init_node(state: AgentState):
    return {
        "sub_messages": [],
        "answer": "",
        "intentions": {},
    }


def _register_nodes(builder: StateGraph):

    executor_agent = BaseExecutorAgent().set_tools(
        tools_container.get_tools(form_all_tools + [qa_query])
    )

    builder.add_node("init_node", _init_node)
    builder.add_node("intention_node", intention_node)
    builder.add_node("chat_node", _chat_node)
    builder.add_node("route_node", route_node)
    builder.add_node("auth_permission", auth_permission_node)
    builder.add_node("executor_agent", executor_agent.graph)
    builder.add_node("completed", _completed_node)
    builder.add_node("verification", _verification_node)


async def _chat_node(state: AgentState):
    messages = state.get("messages", [])
    res = await get_default_llm().ainvoke(
        [SystemMessage("你是一个闲聊助手，负责和用户闲聊")] + messages
    )
    return {"messages": [res], "answer": res.content}


async def _verification_node(state: AgentState):
    """
    审核节点
    """

    return state


async def _completed_node(state: AgentState):

    writer = get_stream_writer()

    writer({"type": "answer", "content": state.get("answer", "")})

    """完成节点，最终输出答案"""
    return state


def build_graph():
    builder = StateGraph(AgentState)
    _register_nodes(builder)

    builder.set_entry_point("init_node")
    builder.add_edge("init_node", "intention_node")
    builder.add_edge("intention_node", "auth_permission")

    builder.add_edge("auth_permission", "route_node")

    for node in ["chat_node", "executor_agent"]:
        builder.add_edge(node, "verification")

    builder.add_edge("verification", "completed")
    builder.add_edge("completed", END)

    # ✅ 创建带允许列表的序列化器
    serde = JsonPlusSerializer(allowed_msgpack_modules=[Intention])

    # ✅ 使用自定义序列化器初始化 checkpointer
    checkpointer = InMemorySaver(serde=serde)

    return builder.compile(checkpointer=checkpointer)


main_graph = build_graph()
