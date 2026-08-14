from langchain.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph
from agents.qa.state import QaState
from agents.base import BaseAgent
from graphs.state import AgentState
from llms.factory import get_default_llm
from services.rags.search import mixed_parent_search

SYSTEM_PROMPT = """
              你是一个基于私有知识库的问答机器人。
当前规则：请忽略通用常识，仅以【当前检索到的知识块】和为准。

知识块：
{context}

用户问题：
{question}

指令：如果知识块与最新问题无关，请礼貌地拒绝回答，并建议用户询问知识库内包含的相关内容。
"""

REVIEW_PROMPT = """
你是一个严格的答案审核员。请判断以下「答案」是否真正回答了「用户问题」，并且没有偏离主题。

用户问题：
{question}

答案：
{answer}

审核标准：
1. 答案是否直接回应用户的问题（不能答非所问）
2. 答案内容是否与问题相关（不能偏离主题）
3. 如果答案是拒绝回答或表示无法回答，且理由是知识库中确实没有相关信息，这属于合理的回答

请只回复一个 JSON：{{"pass": true/false, "reason": "审核理由（简短）"}}
"""

MAX_RETRY = 2


class QaAgent(BaseAgent):
    @classmethod
    def get_key(cls) -> str:
        return "qa"

    @classmethod
    def get_description(cls) -> str:
        return "用户查询公司内部信息或需要用到外部知识的时候调用"

    def get_state(self) -> AgentState:
        return QaState

    async def vector_store_node(self, state: QaState):
        question = state.get("question", "")
        messages = state.get("messages", [])
        docs = await mixed_parent_search(question)

        # 将检索到的文档暂存到 state，供 review 节点使用
        context = "\n".join([f"{doc.page_content}\n" for doc in docs])
        state["review_context"] = context

        system_prompt = SYSTEM_PROMPT.format(
            context=context,
            question=question,
        )
        print(f"rag system prompt: {system_prompt}")
        aimessage = await get_default_llm().ainvoke(
            [
                SystemMessage(content=system_prompt),
            ]
            + messages
        )
        print(f"rag answer: {aimessage.content}")

        return self.set_agent_answer(state, aimessage.content)

    async def review_node(self, state: QaState):
        """审核节点：判断答案是否与问题吻合"""
        question = state.get("question", "")
        answer = state.get("agent_answer", {}).get(self.get_key(), "")

        retry_count = state.get("review_retry_count", 0)

        review_prompt = REVIEW_PROMPT.format(question=question, answer=answer)
        print(f"[review] 第 {retry_count + 1} 次审核...")

        response = await get_default_llm().ainvoke(
            [HumanMessage(content=review_prompt)]
        )

        # 解析审核结果
        import json

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # 解析失败默认通过，避免死循环
            print(f"[review] JSON 解析失败，默认通过。原始返回: {response.content}")
            result = {"pass": True, "reason": "JSON解析失败"}

        print(f"[review] 审核结果: {result}")

        state["review_pass"] = result.get("pass", True)
        state["review_reason"] = result.get("reason", "")
        state["review_retry_count"] = retry_count + 1

        return state

    def should_retry(self, state: QaState) -> str:
        """条件路由：审核不通过且未超重试次数 → 重新检索，否则结束"""
        review_pass = state["review_pass"]
        retry_count = state.get("review_retry_count", 0)

        if not review_pass and retry_count <= MAX_RETRY:
            print(f"[review] 审核不通过，重新检索（第 {retry_count}/{MAX_RETRY} 次）")
            return "vector_store"

        print(f"[review] 审核通过或已达最大重试次数，结束")
        return "end"

    def summary(self, state: QaState):
        pass

    def end(self, state: QaState):
        return state

    def register_nodes(self, builder: StateGraph):
        builder.add_node("vector_store", self.vector_store_node)
        builder.add_node("review", self.review_node)
        builder.add_node("summary", self.summary)
        builder.add_node("end", self.end)

    def edge_nodes(self, builder: StateGraph):
        builder.set_entry_point("vector_store")
        builder.add_edge("vector_store", "review")
        builder.add_conditional_edges(
            "review",
            self.should_retry,
            {
                "vector_store": "vector_store",
                "end": "end",
            },
        )
        builder.set_finish_point("end")
