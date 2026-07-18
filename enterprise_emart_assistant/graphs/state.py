from turtle import st
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState, add_messages

from enums.roles import Role


class AgentState(MessagesState):
    """
    intentions: {
         "origin_input": 用户输入
         "type": 意图类型
         "description": 意图描述
    }
    """
    role: str | None = ""
    user_id: str | None = None
    answer: str | None = ""
    intentions: dict[str, str] | None = []
    fill_form_messages: Annotated[list[AnyMessage], add_messages]
    pass
