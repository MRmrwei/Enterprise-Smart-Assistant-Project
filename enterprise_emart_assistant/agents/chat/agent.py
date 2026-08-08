from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph

from agents.base import BaseAgent
from graphs.state import AgentState
from llms.factory import get_default_llm

SYSTEM_PROMPT = """
    "你是一个智能助手，你的任务是负责与用户闲聊。"
"""


class ChatAgent(BaseAgent):

    @classmethod
    def get_description(cls) -> str:
        return "用户无特定意图时负责与用户闲聊"

    @classmethod
    def get_key(cls) -> str:
        return "chat_agent"

    def register_nodes(self, builder: StateGraph):
        builder.add_node("chat_node", self.chat_node)
        pass

    def edge_nodes(self, builder: StateGraph):
        builder.set_entry_point("chat_node")
        pass

    def get_state(self) -> AgentState:
        return AgentState

    async def chat_node(self, state: AgentState):
        messages = state.get("messages", "")
        aimessage = await get_default_llm().ainvoke(
            [SystemMessage(SYSTEM_PROMPT)] + messages
        )
        return {
            "answer": aimessage.content,
        }
