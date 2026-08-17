from langgraph.graph import StateGraph
from graphs.state import AgentState
from nodes.combine import combine_node
from nodes.router import route_node
from nodes.intention import intention_node
from langchain_core.messages import HumanMessage, AIMessage
from agents.list import agents
from langgraph.config import get_stream_writer
from db.savers.saver import get_saver


def init_node(state: AgentState):
    return {
        "agent_messages": {},
        "agent_answer": {},
        "answer": "",
        "intentions": None,
        "messages": [HumanMessage(content=state.get("question", ""))],
    }


async def register_nodes(builder: StateGraph):

    builder.add_node("init_node", init_node)
    builder.add_node("intention_node", intention_node)
    builder.add_node("combine", combine_node)
    builder.add_node("route_node", route_node)
    builder.add_node("completed", completed_node)
    # builder.add_node("verification", _verification_node)

    for agent in agents:
        agent_cls = agent()
        builder.add_node(agent.get_key(), await agent_cls.get_graph())
        builder.add_edge(agent.get_key(), "combine")


def completed_node(state: AgentState):
    """完成节点，最终输出答案"""
    answer = state.get("answer", "")

    writer = get_stream_writer()
    writer({"type": "answer", "content": answer})

    return {"messages": [AIMessage(content=answer)], "answer": answer}


async def build_graph():
    builder = StateGraph(AgentState)
    await register_nodes(builder)

    builder.set_entry_point("init_node")
    builder.add_edge("init_node", "intention_node")
    builder.add_edge("intention_node", "route_node")

    # builder.add_edge("verification", "completed")
    builder.add_edge("combine", "completed")
    builder.set_finish_point("completed")

    # ✅ 使用自定义序列化器初始化 checkpointer
    checkpointer = await get_saver()
    return builder.compile(checkpointer=checkpointer)


MAIN_GRAPH = None


async def get_main_graph():
    """异步获取编译后的主图（单例）"""
    global MAIN_GRAPH
    if MAIN_GRAPH is None:
        MAIN_GRAPH = await build_graph()
    return MAIN_GRAPH
