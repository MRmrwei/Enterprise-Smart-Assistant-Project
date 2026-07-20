from turtle import st
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState, add_messages

from enums.roles import Role
from pydantics.intentions import Intention


class AgentState(MessagesState):
    role: str | None = ""
    user_id: str | None = None
    answer: str | None = ""
    intentions: Intention | None = None
    fill_form_messages: Annotated[list[AnyMessage], add_messages]
    knowledge_ingest_messages: Annotated[list[AnyMessage], add_messages]
    pass
