from langgraph.graph import MessagesState


class AgentState(MessagesState):
    intention_type: str | None = "unknown"
    intention_description:str | None = None
    role: str | None = "employee"
    user_id: str | None = None
    pass
