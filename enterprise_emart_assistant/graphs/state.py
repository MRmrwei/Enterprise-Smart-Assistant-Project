from turtle import st
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState, add_messages

from enums.roles import Role
from pydantics.intentions import Intention


class AgentState(MessagesState):
    role: str | None = ""
    uid: int | None = None
    answer: str | None = ""
    intentions: Intention | None = None
    sub_messages: Annotated[list[AnyMessage], add_messages]
    agent_attributes: dict | None = {}
    question: str | None = ""
    pass
