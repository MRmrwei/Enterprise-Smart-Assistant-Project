from agents.base import BaseAgent
from agents.chat.agent import ChatAgent
from agents.employee.agent import EmployeeDataAgent

agents: list[BaseAgent] = [EmployeeDataAgent, ChatAgent]
