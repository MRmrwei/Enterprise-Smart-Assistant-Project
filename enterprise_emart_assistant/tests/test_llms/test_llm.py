from operator import le

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from llms.factory import get_default_llm, get_llm
from nodes.intention import intention_llm
from prompts.intention import get_intention_system_prompt
from pydantics.decision import AIDecision
from pydantics.intentions import Intention
from tools.base import ToolContainer
from tools.forms import leave_request


def test_llm():
    llm = get_default_llm()
    print(
        llm.invoke(
            [
                SystemMessage(
                    content="你是知性的大姐姐，回答用户所提出的问题。根据事实回答。"
                ),
                HumanMessage(content="你是男生女生"),
            ]
        ).content
    )


class TestObject(BaseModel):
    decision: str
    reason: str


def test_to_json():
    llm = get_default_llm().with_structured_output(TestObject, method="json_mode")
    # llm = get_default_llm(response_format={"type":"json_object"})
    try:
        res: TestObject = llm.invoke(
            "json格式输出以下内容：decision输出你好，reason输出我很好"
        )
        print(f"res: {res}")
    except Exception as e:
        print(f"Exception: {e}")


def test_ai_decision():

    prompt = """
    你是智能流程决策器。根据上下文和工具执行结果，判断当前任务是否已经彻底结束
    ##决策规则（必须二选一）：
        1. 决策为 "completed" 的情况：
        - 工具返回了"提交成功"、"创建成功"、"已取消"、"已放弃"等终结性结果或者完成的意图。
        - 用户明确表达了结束意图且系统已响应（如"好的，已提交"）。
        2. 决策为 "confirm" 的情况：
        - 工具返回了"校验失败"、"缺少字段"、"格式错误"等需要修改的信息。
        - 用户在提出修改意见、补充数据，或系统正在等待用户输入。
        - 任何不确定的情况，都优先选择 "confirm"（安全优先）。

        请只做判断，不要额外解释，你的输出会被自动解析。
    ## Json 输出格式：
        {
            "node": completed|confirm,
            "reason": 判断理由
        }
    ## 注意：
        - 必须json格式返回
    """

    llm = get_default_llm().with_structured_output(AIDecision, method="json_mode")
    res: AIDecision = llm.invoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(content="工具返回了\"提交成功\"，用户明确表达了结束意图且系统已响应（如\"好的，已提交\"）。"),
        ]
    )
    print(res)


def test_message():
    arr = [
        HumanMessage(content="你是男生女生"),
        HumanMessage(content="你是男生女生"),
        HumanMessage(content="你是男生女生"),
        HumanMessage(content="你是男生女生"),
    ]

    msg = "\n".join([m.content for m in arr])
    llm = get_default_llm().invoke(
        [
            SystemMessage(
                content=f"你叫小鹅是个上下文总结专家，请热情的回答。给出上下文所表达的意思。\n上下文：{msg}"
            ),
        ]
    )
    print(llm)


def test_intention():
    res:Intention = intention_llm().invoke(
        [SystemMessage(get_intention_system_prompt()), HumanMessage(content="我出差去了北京谈客户用了3600，帮我报销")]
    )
    print(res)
    
    
def test_call_tool():
    
    # tools = ToolContainer
    
    print(leave_request.__name__)
    
    # tools.register_tool(leave_request)
    # llm = get_default_llm().bind_tools(tools.get_tool("leave_request"))