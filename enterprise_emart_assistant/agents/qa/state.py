from graphs.state import AgentState


class QaState(AgentState):
    review_pass: bool = True
    review_reason: str = ""
    review_retry_count: int = 0
    review_context: str = ""