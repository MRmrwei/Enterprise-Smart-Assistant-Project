from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from regex import E
from agents.base import BaseAgent
from graphs.state import AgentState
from llms.factory import get_default_llm
from tools.base import tools_container
from agents.employee.state import EmployeeState

SYSTEM_PROMPT = """
你是一个智能助手，已绑定一组可用的外部工具。当用户的问题需要实时数据、计算、外部知识或执行操作时，你应主动调用相应的工具。

**重要**：
- 如果对话历史中已经包含用户所需的信息（例如之前查询过的员工资料），请直接引用这些信息，**不要重复调用工具**。
- 只有在历史中没有答案，且确实需要外部数据时，才考虑调用工具。
- 不调用工具时，请在回复中明确说明原因，并基于已有信息回答问题。

当前用户问题：{question}
"""


class EmployeeDataAgent(BaseAgent):

    def get_tools(self):
        return tools_container.get_tools("employee_info")

    @classmethod
    def get_description(cls) -> str:
        return "员工个人数据查询（工资/考勤/报销）"

    def get_state(self):
        return EmployeeState

    @classmethod
    def get_key(cls) -> str:
        return "employee_agent"

    def register_nodes(self, builder: StateGraph):
        builder.add_node("init_node", self.init_node)
        builder.add_node("load_tool", self.load_tool)
        builder.add_node("router", self.router)
        builder.add_node(
            "tool",
            ToolNode(self.get_tools(), messages_key=self.get_sub_messages_key()),
        )
        builder.add_node("completed", self.completed_node)

    def edge_nodes(self, builder: StateGraph):
        builder.set_entry_point("init_node")
        builder.add_edge("init_node", "load_tool")
        builder.add_conditional_edges("load_tool", self.router)
        builder.add_edge("tool", "completed")
        builder.add_edge("completed", END)

    async def completed_node(self, state: EmployeeState):
        # 多轮对话
        messages = self.get_sub_messages(state)
        aimessage = await get_default_llm().ainvoke(
            [
                SystemMessage(
                    content="你是一个对话总结助手。请根据以往的对话的完整历史，生成一份客观、基于事实的总结。"
                ),
            ]
            + messages
        )
        return self.set_agent_answer(state, aimessage.content)

    async def init_node(self, state: EmployeeState):
        # 用户问题
        question = state.get("question", "")
        return self.set_sub_messages(state, [HumanMessage(content=question)])

    async def load_tool(self, state: EmployeeState):
        llm = get_default_llm().bind_tools(self.get_tools(), strict=True)
        content = SYSTEM_PROMPT.format(question=state.get("question", ""))
        message = await llm.ainvoke(
            [
                SystemMessage(content=content),
            ]
            + state.get("messages", [])
        )

        return self.set_sub_messages(state, [message])

    def router(self, state: EmployeeState):
        messages = self.get_sub_messages(state)

        if hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
            print("调用工具")
            return "tool"
        return "completed"
