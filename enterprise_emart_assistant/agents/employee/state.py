from cmath import e
from typing import Annotated

from langchain.messages import AnyMessage
from langgraph.graph import add_messages

from graphs.state import AgentState


class EmployeeState(AgentState):

    employee_messages: Annotated[list[AnyMessage], add_messages]

    @staticmethod
    def get_message_key() -> str:
        return "employee_messages"
