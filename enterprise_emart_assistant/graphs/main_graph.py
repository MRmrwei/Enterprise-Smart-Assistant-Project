from langchain.agents import create_agent
from langgraph.graph import END, StateGraph
from graphs.state import AgentState
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from llms.factory import get_default_llm
from nodes.combine import combine_node
from nodes.router import route_node
from nodes.intention import intention_node
from langgraph.checkpoint.memory import InMemorySaver
from pydantics.intentions import Intention
from langchain_core.messages import HumanMessage, AIMessage
from agents.list import agents


def init_node(state: AgentState):
    
    return {
        "agent_messages": {},
        "agent_answer": {},
        "answer": "",
        "intentions": None,
        "messages": [HumanMessage(content=state.get("question", ""))],
    }


def register_nodes(builder: StateGraph):

    builder.add_node("init_node", init_node)

    builder.add_node("intention_node", intention_node)
    builder.add_node("combine", combine_node)
    builder.add_node("route_node", route_node)
    builder.add_node("completed", completed_node)
    # builder.add_node("verification", _verification_node)

    for agent in agents:
        builder.add_node(agent.get_key(), agent().graph)
        builder.add_edge(agent.get_key(), "combine")


def completed_node(state: AgentState):
    """完成节点，最终输出答案"""
    answer = state.get("answer", "")
    return {"messages": [AIMessage(content=answer)]}


def build_graph():
    builder = StateGraph(AgentState)
    register_nodes(builder)

    builder.set_entry_point("init_node")
    builder.add_edge("init_node", "intention_node")
    builder.add_edge("intention_node", "route_node")

    # builder.add_edge("verification", "completed")
    builder.add_edge("combine", "completed")
    builder.add_edge("completed", END)

    # ✅ 创建带允许列表的序列化器
    serde = JsonPlusSerializer(allowed_msgpack_modules=[Intention])

    # ✅ 使用自定义序列化器初始化 checkpointer
    checkpointer = InMemorySaver(serde=serde)

    return builder.compile(checkpointer=checkpointer)


# main_graph = build_graph()
