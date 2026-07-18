from langgraph.graph import END
from langgraph.types import Command

from enums.intentions import Intentions
from enums.roles import Role
from graphs.state import AgentState


def auth_permission_node(state: AgentState):
    intention_type = state.get("intention_type")
    role = state.get("role")
    user_id = state.get("user_id")
    
    # if role not in [Role.BOSS.value, Role.MANAGER.value]:
        
    #     return Command(goto=END, update={"answer": "无权限访问"})        
        
    # if intention_type is Intentions.FILL_FORM.value:
    #     pass
    
    return state