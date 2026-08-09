from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph

from agents.base import BaseAgent
from graphs.state import AgentState
from llms.factory import get_default_llm

SYSTEM_PROMPT = """
你是一个友好、亲切的闲聊助手。你的任务是与用户进行自然、连贯的对话。

**重要准则**：
1. **基于历史回答**：请完整阅读整个对话历史（包括用户之前的问题和所有助手的回复）。如果用户的问题涉及之前已经讨论过的内容（例如查询到的个人信息、角色、数据等），请**直接引用**这些事实，不要虚构或猜测。
2. **保持风格一致**：回答应轻松、幽默，但必须确保信息准确。如果用户的问题无法从历史中找到答案，你可以坦诚告知，并引导用户提出更明确的问题。
3. **连贯性**：尽可能延续对话的上下文，避免重复或前后矛盾。
**你的能力**：
你可以帮助用户完成以下任务（但你不直接执行，而是会协调相应的专业助手）：
{capabilities}
记住，你是一个善于倾听、乐于助人的聊天伙伴。
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
        
        from agents.list import agents  # 假设agents是模块级列表
        capabilities = "\n".join([f"- {agent.get_description()}" for agent in agents])
        prompt = SYSTEM_PROMPT.format(capabilities=capabilities)
        messages = state.get("messages", "")
        aimessage = await get_default_llm().ainvoke(
            [SystemMessage(prompt)] + messages
        )
        return {
            "answer": aimessage.content,
        }
