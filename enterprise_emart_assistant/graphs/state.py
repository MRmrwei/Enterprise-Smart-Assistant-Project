from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState, add_messages
from enums.roles import Role
from pydantics.intentions import Intention


class AgentState(MessagesState):
    uid: int | None = None
    answer: str | None = ""
    intentions: Intention | None = None
    # 智能体消息寄存
    agent_messages: dict[str, list[AnyMessage]] | None = {}
    agent_answer: dict[str, str] | None = {}
    question: str | None = ""

    @staticmethod
    def get_message_key() -> str:
        """
        获取agent消息key
        """
        return "messages"
