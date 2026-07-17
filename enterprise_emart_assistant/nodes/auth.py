from langgraph.types import Command

from graphs.state import AgentState


def auth_permission(state: AgentState):
    intention_type = state.get("intention_type")
    role = state.get("role", "employee")
    user_id = state.get("user_id")
    
    return "route_node"