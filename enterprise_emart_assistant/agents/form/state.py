from typing import Annotated, Optional

from langchain.messages import AnyMessage
from langgraph.graph import add_messages

from graphs.state import AgentState
from pydantics.decision import AIDecision


class FormState(AgentState):
    form_messages: Annotated[list[AnyMessage], add_messages]
    decision: Optional[AIDecision] = None

    @staticmethod
    def get_message_key() -> str:
        return "form_messages"
