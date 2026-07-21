
from agents.base import BaseExecutorAgent
from tools.base import tools_container
from tools.forms import reimbursement_request

def test_get_tool():
    print("ddddddddddddddd\n")
    print(tools_container.get_tools("leave_request", reimbursement_request))
    
def test_agent_get_tool():
    print(f"fffff= {BaseExecutorAgent().get_skills()}")