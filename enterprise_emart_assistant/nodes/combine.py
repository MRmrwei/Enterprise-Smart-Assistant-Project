from re import S

from langchain.messages import HumanMessage, SystemMessage

from graphs.state import AgentState
from llms.factory import get_default_llm

SYSTEM_PROMPT = """
你是一个专业的答案合成器。用户提出了一个复杂问题，该问题被拆分为多个子任务，分别交由不同的专家Agent并行处理。你现在拿到的是一组**碎片化的回答片段**（agent_answers）。

你的核心任务不是简单的“总结”或“罗列”，而是将这些碎片**无缝拼接**成一份完整、连贯、逻辑通顺的最终答案，仿佛从头到尾由一位专家一气呵成写就。

### 合成原则
1. **挖掘逻辑脉络**：请先判断这些碎片分别对应问题的哪个维度（例如：背景原因、现状分析、解决方案、操作步骤、注意事项；或者：分论点A、B、C；或者：时间先后顺序）。**不要按输入顺序生硬拼接**，而应按**因果关系、重要性层级、时间顺序或认知逻辑**重新排列。

2. **消除冗余与填补断层**：
   - 如果多个碎片包含重复信息，只保留最清晰的一句。
   - 如果碎片之间存在逻辑跳跃（比如上一句讲原因，下一句直接讲结果而没有过渡），请用恰当的过渡词（如：“基于上述原因”、“具体实施时”、“此外”、“总而言之”）进行自然衔接。

3. **严格忠实于原文**：**严禁**添加任何外部知识、常识补充或主观推测。所有信息必须严格来源于给定的碎片内容。

4. **确保完整性**：最终答案必须覆盖**所有**碎片中的关键信息，不能遗漏任何一个子任务对应的答案点。

### 输入内容
- 用户原始问题：{question}
- 各Agent返回的碎片回答（按原始顺序给出，可能杂乱无序）：
{answers}

### 输出要求
只输出最终的完整答案，不要包含“以下是整合结果”等额外说明。最终文本必须读起来像是一个完整、自然、有逻辑层次的长句或段落集合。
"""


async def combine_node(state: AgentState):
    agent_answers = state.get("agent_answer")  # 这是一个列表，每个元素是一个子任务答案
    answer = state.get("answer")

    # 如果子答案为空但已有完整答案，直接返回
    if not agent_answers and answer != "":
        return state

    # 给碎片编号，帮助LLM识别"这是第几个碎片"，但Prompt里已强调不要按顺序拼接
    # 为了更清晰，可以保留编号，让LLM知道一共有几块
    formatted_answers = "\n---\n".join(
        [
            f"【碎片 {i+1}】\n{value}"
            for i, (key, value) in enumerate(agent_answers.items())
        ]
    )
    # 格式化System Prompt
    prompt = SYSTEM_PROMPT.format(
        question=state.get("question", ""), answers=formatted_answers
    )

    llm = get_default_llm()
    # 注意：原代码混用了 ainvoke / ainvoke，这里统一使用异步调用
    ai_msg = await llm.ainvoke([SystemMessage(content=prompt)])

    return {"answer": ai_msg.content}
