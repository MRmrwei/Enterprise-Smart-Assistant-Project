from agents.base import BaseAgent
from agents.chat.agent import ChatAgent
from agents.employee.agent import EmployeeDataAgent
from agents.form.agent import FormDataAgent
from agents.qa.agent import QaAgent

agents: list[BaseAgent] = [EmployeeDataAgent, ChatAgent, FormDataAgent,QaAgent]

