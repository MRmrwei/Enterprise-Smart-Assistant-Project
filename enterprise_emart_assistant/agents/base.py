from datetime import datetime
from email.policy import strict
from langgraph.graph.state import END, CompiledStateGraph, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.language_models.chat_models import BaseChatModel
from regex import T
from enums.intentions import Intentions
from graphs.state import AgentState
from llms.factory import get_default_llm
from pydantics.decision import AIDecision
from pydantics.intentions import Intention
from tools.base import tools_container
from tools.forms import leave_skills
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_core.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.types import Command, interrupt
from tools.knowledges import skills, analysis_word, upload_knowledge


class BaseExecutorAgent:
    """
    ## 流程：
        1. 识别意图选择Skill
        2. 加载Skill
        3. Ai决策

    ## AI决策规则：
        - 用call_toll直接调用工具
        - 是否需要用户干预（中断）
        - 意图qa 直接调用工具并返回

    """

    _graph: CompiledStateGraph | None
    llm: BaseChatModel | None
    tools: list[BaseTool] | None

    def __init__(self):
        self._graph = None
        self.tools = []
        self.llm = get_default_llm()

    def with_tools_llm(self):
        return self.llm.bind_tools(self.get_tools(), strict=True)

    def get_skills(self) -> list[BaseTool]:
        return tools_container.get_tools(leave_skills, skills)

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AgentState)

        builder.add_node("init_node", self._init_node)
        builder.add_node("change_skill", self._change_skill_node)
        builder.add_node(
            "init_skills", ToolNode(self.get_skills(), messages_key="sub_messages")
        )
        builder.add_node(
            "tools", ToolNode(self.get_tools(), messages_key="sub_messages")
        )
        builder.add_node("load_skills", self._load_skills_node)
        builder.add_node("ai_decision", self._ai_decision_node)
        builder.add_node("confirm", self._confirm_node)
        builder.add_node("completed", self._completed_node)
        # builder.add_node("load_tools", self._load_tools_node)

        builder.set_entry_point("init_node")

        builder.add_edge("init_node", "change_skill")
        builder.add_edge("change_skill", "init_skills")
        builder.add_edge("init_skills", "load_skills")

        builder.add_edge("load_skills", "ai_decision")
        builder.add_edge("confirm", "ai_decision")
        builder.add_edge("tools", "ai_decision")

        # builder.add_edge("load_tools", "tools")
        builder.add_edge("completed", END)
        return builder

    async def _load_tools_node(self, state: AgentState):
        sub_messages = state.get("sub_messages", [])
        content = "\n".join([m.content for m in sub_messages])

        res = await self.with_tools_llm().ainvoke(
            [
                SystemMessage(
                    content=f"{self.get_load_tools_system_prompt()}\n上下文：{content}"
                ),
            ]
        )
        if hasattr(res, "tool_calls") and res.tool_calls:
            return {"sub_messages": [res]}

        return Command(name="completed", update={"sub_messages": [res]})

    def _completed_node(self, state: AgentState):
        messages = state.get("sub_messages", [])
        message = messages[-1]
        return {"answer": message.content}

    async def _load_skills_node(self, state: AgentState):
        """
        初始化skill节点
        第一次交互需要返回友好语言或直接调用工具
        """

        intentions: Intention = state.get("intentions", None)
        sub_messages = state.get("sub_messages", [])
        messages = [
            SystemMessage(
                content=f"{self.get_confirm_system_prompt()}{self.extract_info(intentions)}"
            )
        ] + sub_messages

        res = await self.with_tools_llm().ainvoke(messages)
        # print(f"res ======== {res.content}")
        return {"sub_messages": [res]}

    def get_confirm_system_prompt(self) -> str:

        return f"""
        你是善于用友好语言表达的引导流程专家。结合上下文和skill的规则来生成友好语言来引导用户或直接调用工具。
        ## 背景信息：
            - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
            
        """

    def get_tools(self) -> list[BaseTool]:
        return self.tools

    def set_tools(self, tools: list[BaseTool]):
        self.tools = tools
        return self

    def _init_node(self, state: AgentState):
        return {
            "sub_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
            "agent_attributes": {"is_interrupt": False},
        }

    def get_is_interrupt(self, intentions: Intention) -> bool:
        if intentions.type == Intentions.QA.value:
            return False
        return True

    async def _ai_decision_node(self, state: AgentState):
        """
        AI决策节点
        """
        intentions: Intention = state.get("intentions", None)
        sub_messages = state.get("sub_messages", [])

        if isinstance(sub_messages[-1], ToolMessage):
            if sub_messages[-1].status == "error":
                print(f"工具调用错误：{sub_messages[-1].content}")
                return {"answer": "内部错误！"}

        if hasattr(sub_messages[-1], "tool_calls") and sub_messages[-1].tool_calls:
            return Command(goto="tools")

        if len(sub_messages) < 1:
            return Command(goto="confirm")

        content = "\n".join(
            [f"{i +1}. {m.content}\n" for i, m in enumerate(sub_messages)]
        )

        messages = [
            SystemMessage(
                content=f"{self.get_decisio_system_prompt()}\n 本次流程的基本情况：\n{self.extract_info(intentions)} "
            ),
            HumanMessage(content=f"上下文与工具结果：{content}"),
        ]

        try:
            result: AIDecision = await self.llm.with_structured_output(
                AIDecision, method="json_mode"
            ).ainvoke(messages)

            print(f"智能流程决策结果：{result}")

            return Command(
                goto=result.node,
                update={"agent_attributes": {"is_interrupt": result.is_interrupt}},
            )
        except Exception as e:
            return Command(goto=END, update={"answer": str(e)})

    async def _confirm_node(self, state: AgentState):
        """
        关键数据补全与确认节点
        """

        sub_messages = state.get("sub_messages", [])
        is_interrupt = state.get("agent_attributes", {}).get("is_interrupt", False)
        if is_interrupt:
            # content = "\n".join(
            #     [f"{i +1}. {m.content}\n" for i, m in enumerate(sub_messages)]
            # )
            confirm_msg = interrupt(sub_messages[-1].content)
            messages = (
                [SystemMessage(content=self.get_confirm_system_prompt())]
                + sub_messages
                + [HumanMessage(content=confirm_msg)]
            )

        else:
            messages = [
                SystemMessage(
                    content="你是上下文判断专家，结合上下文判断是否调用工具，如果不需要请返回友好语句"
                )
            ] + sub_messages

        res = await self.with_tools_llm().ainvoke(messages)

        return {"sub_messages": [res]}

    @property
    def graph(self) -> CompiledStateGraph:

        if self._graph is not None:
            return self._graph

        self._graph = self._build_graph().compile()

        return self._graph

    def extract_info(self, intentions: Intention | None = None) -> str:
        """
        从意图中提取信息
        """
        if intentions is None:
            return ""
        origin_input = intentions.origin_input
        description = intentions.description
        vital_content = intentions.vital_content
        info = f"\n意图描述：{description}\n用户原话：{origin_input}\n重要信息：{vital_content}"

        if intentions.file_path is not None or intentions.file_path != "":
            info += f"\n文件路径：{intentions.file_path}"
        return info

    async def _change_skill_node(self, state: AgentState):
        """
        从意图中提取信息
        """
        intentions: Intention = state.get("intentions", None)

        prompt = self.get_init_system_prompt() + self.extract_info(intentions)

        llm = self.llm.bind_tools(self.get_skills(), strict=True)

        # messages = state.get("sub_messages", [])[-1]

        res = await llm.ainvoke([SystemMessage(content=prompt)])

        return {"sub_messages": [res]}

    def get_init_system_prompt(self) -> str:
        return f"""
        你是意图识别专家。根据上下文，选择skill。
        背景信息：
        - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
        """

    def get_decisio_system_prompt(self) -> str:
        return """
        你是智能流程决策器。根据上下文和工具执行结果，判断当前任务是否已经彻底结束
        ## 决策规则：
            1. 决策为 "completed" 的情况：
            - 工具返回了"提交成功"、"创建成功"、"已取消"、"已放弃"等终结性结果或者完成的意图。
            - 用户明确表达了结束意图且系统已响应（如"好的，已提交"）。
            2. 决策为 "confirm" 的情况：
            - 工具返回了"校验失败"、"缺少字段"、"格式错误"等需要修改的信息。
            - 需要用户提出修改意见、补充数据，或系统正在等待用户输入。
            - 需要模型调用工具。
        ## is_interrupt字段规则：
            1. 值为 "true" 的情况：
                - 需要人工干预的流程。
                - 需要用确认，修改，补全数据的流程。
            2. 值为 "false" 的情况：
                - 不需要人工干预的流程。
                - 询问知识库，获取个人信息的流程
        ## Json 输出格式：
            {
                "node": completed|confirm,
                "reason": 判断理由
                "is_interrupt": true|false
            }
        ## 注意：
            - 必须json格式返回
    """

    def get_load_tools_system_prompt(self) -> str:
        return f"""
        你是工具选择助手，根据skill和上下文，选择工具。
    """
