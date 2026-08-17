import asyncio
from datetime import datetime

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.types import Command, interrupt
from langgraph.prebuilt import ToolNode
from sqlalchemy import True_
import stamina
from agents.base import BaseAgent
from llms.factory import get_default_llm, get_master_llm
from agents.form.state import FormState
from langchain.tools import BaseTool
from pydantics.decision import AIDecision
from pydantics.intentions import Intention
from tools.base import tools_container
from tools.forms import leave_skills
from langchain_core.language_models.chat_models import BaseChatModel
from db.savers.saver import get_saver
from langgraph.config import get_stream_writer


class FormDataAgent(BaseAgent):

    def get_tools(self) -> list[BaseTool]:
        tools = tools_container.get_tools([leave_skills, "leave_request"])
        return tools

    def get_tools_llm(self, opus: bool = False, **overrides) -> BaseChatModel:
        return (
            get_master_llm(**overrides) if opus else get_default_llm(**overrides)
        ).bind_tools(self.get_tools(), strict=True)

    async def get_checkpointer(self) -> None:
        return await get_saver()

    @classmethod
    def get_description(cls) -> str:
        return "负责用户的请假、报销申请工作"

    def get_state(self):
        return FormState

    @classmethod
    def get_key(cls) -> str:
        return "form_data"

    def register_nodes(self, builder: StateGraph):
        builder.add_node("load_skill", self.load_skill_node)
        builder.add_node(
            "tool", ToolNode(self.get_tools(), messages_key=self.get_sub_messages_key())
        )
        builder.add_node("ai_router", self.ai_router_node)
        builder.add_node("end", self.end)
        builder.add_node("interrupt", self.interrupt_node)
        builder.add_node("load_tool", self.load_tool_node)

    def edge_nodes(self, builder: StateGraph):
        builder.set_entry_point("load_skill")

        builder.add_conditional_edges("load_skill", self.tool_rotuer)
        builder.add_conditional_edges("load_tool", self.tool_rotuer)
        builder.add_edge("tool", "ai_router")
        builder.add_edge("interrupt", "ai_router")
        # builder.add_edge("ai_router", "end")
        builder.set_finish_point("end")

    async def end(self, state: FormState):
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

    async def interrupt_node(self, state: FormState):
        aimessage = await self.get_tools_llm().ainvoke(
            [
                SystemMessage(
                    content=f"{self.get_interrupt_system_prompt()}\n 用户问题：{state.get('question', '')} "
                )
            ]
            + self.get_sub_messages(state)
        )

        confirm_message = HumanMessage(content=interrupt(aimessage.content))
        # 重新加载子agent上下文
        return self.set_sub_messages(state, [aimessage, confirm_message])

    async def ai_router_node(self, state: FormState):
        messages = self.get_sub_messages(state)

        # 使用干净的 opus LLM + json_mode 获取结构化决策
        # 不绑表单工具，避免与 structured output 冲突
        system_prompt = (
            "你是一个智能决策路由器。请根据对话历史输出 JSON 格式的决策。\n"
            f"用户问题：{state.get('question', '')}\n"
            + self.get_decisio_system_prompt()
        )

        llm = get_master_llm(response_format={"type": "json_object"})
        structured_llm = llm.with_structured_output(AIDecision, method="json_mode")

        try:
            for attempt in stamina.retry_context(on=Exception, attempts=3):
                with attempt:
                    result: AIDecision = await structured_llm.ainvoke(
                        [SystemMessage(content=system_prompt)] + messages
                    )
        except Exception as e:
            raise Exception(f"AI 决策 JSON 解析失败（已重试 {attempt.num} 次）: {e}")

        print(f"AI决策： {result}")
        writer = get_stream_writer()
        writer({"type": "reasoning", "content": result.reason})

        if result.node == "parent":
            return Command(
                graph=Command.PARENT,
                goto="init_node",
                update={"question": messages[-1].content},
            )
        elif result.node == "interrupt":
            return Command(goto="interrupt", update=state)
        elif result.node == "tool":
            return Command(goto="load_tool", update=state)
        elif result.node == "completed":
            return Command(goto="end", update=state)
        else:
            raise Exception(f"未知的节点：{result.node}")

    async def load_tool_node(self, state: FormState):
        print("加载工具")
        messags = self.get_sub_messages(state)
        aimessage = await self.get_tools_llm().ainvoke(
            [SystemMessage(content="结合上下文，给出一个**最合适的**工具调用。")]
            + messags
        )

        return self.set_sub_messages(state, [aimessage])

    def tool_rotuer(self, state: FormState):
        messages = self.get_sub_messages(state)
        if hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
            print("调用工具 or skill")
            return "tool"
        return "ai_router"

    async def load_skill_node(self, state: FormState):
        question = HumanMessage(state.get("question", ""))
        aimessage = await self.get_tools_llm().ainvoke(
            [
                SystemMessage(
                    content="你是一个智能调度员（Dispatcher）。你的唯一职责是：阅读用户的自然语言问题，从预定义的技能库中，选出**最匹配**的一项技能。"
                ),
                question,
            ]
        )
        return self.set_sub_messages(state, [aimessage])

    def get_decisio_system_prompt(self) -> str:
        return """
            ## 决策规则（按优先级从高到低）

            ### 1. 决策为 "completed"（任务终结）
            - 工具返回了"提交成功"、"创建成功"、"已取消"、"已放弃"等明确终结性结果。
            - 用户明确表达了结束意图（如"好的，就这样"），且系统已响应。
            - 用户明确表达放弃当前流程（如"算了，不请了"、"取消"）。

            ### 2. 决策为 "parent"（任务切换）
            - **用户的最新消息与当前正在执行的子任务完全无关**。
            - 例如：用户要求跳转到其他功能（如"我要查考勤"）。
            - **注意**：如果用户只是对当前表单字段进行修改或补充（如"改成明天"、"请3天"），应走 interrupt，而非 parent。

            ### 3. 决策为 "interrupt"（需要用户交互）
            - 需要用户补充当前表单的缺失字段。
            - 需要用户对已填信息进行确认或修改。

            ### 4. 决策为 "tool"（需要工具执行）
            - 需要调用工具来完成操作。

            ## is_interrupt 字段规则
            - **true**：需要人工干预（确认、修改、补全数据）。
            - **false**：无需人工干预（自动工具调用、信息返回）。
            - **重要**：当 node 为 parent 时，is_interrupt 必须为 false。

            请严格按照以下 JSON 结构输出决策：
            {"node": "节点名", "reason": "判断理由", "is_interrupt": false}
            """

    def get_interrupt_system_prompt(self) -> str:
        return f"""
            你是善于用友好语言表达的引导流程专家。结合上下文和skill的规则来生成友好语言来引导用户或直接调用工具。
            ## 背景信息：
                - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
                
            """

    def extract_info(self, state: FormState) -> str:

        intentions: Intention = state.get("intentions", None)
        """
        从意图中提取信息
        """
        if intentions is None:
            return ""
        description = intentions.description
        vital_content = intentions.vital_content
        info = f"\n意图描述：{description}\n重要信息：{vital_content}"
        return info
