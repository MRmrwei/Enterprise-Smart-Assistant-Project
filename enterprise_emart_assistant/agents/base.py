from abc import ABC, abstractmethod
from typing import Optional
from langgraph.graph.state import CompiledStateGraph, StateGraph
from graphs.state import AgentState
from langchain.messages import AnyMessage


class BaseAgent(ABC):
    _graph: Optional[CompiledStateGraph] = None

    @property
    def graph(self) -> CompiledStateGraph:

        if self._graph is not None:
            return self._graph
        checkpointer = self.get_checkpointer() if self.get_checkpointer() else None
        self._graph = self.build_graph().compile(checkpointer=checkpointer)

        return self._graph

    @abstractmethod
    def register_nodes(self, builder: StateGraph):
        pass

    @abstractmethod
    def edge_nodes(self, builder: StateGraph):
        pass

    def get_state(self) -> AgentState:
        """
        图状态
        """
        return AgentState

    def get_state_graph(self) -> StateGraph:
        return StateGraph(self.get_state())

    @classmethod
    @abstractmethod
    def get_key(cls) -> str:
        """
        智能体标识
        """
        pass

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """
        智能体使用场景描述
        """
        pass

    def build_graph(self) -> StateGraph:
        builder = self.get_state_graph()
        self.register_nodes(builder)
        self.edge_nodes(builder)
        return builder

    def get_checkpointer(self):
        return None

    def get_history_messages(self, state: AgentState) -> list[AnyMessage]:
        """
        获取子agent在寄存器的会话状态
        """

        return state.get("agent_messages", {}).get(self.get_key(), [])

    def set_history_messages(
        self, state: AgentState, messages: list[AnyMessage]
    ) -> AgentState:
        """
        设置子agent在寄存器的会话状态
        """

        state.update({"agent_messages": {self.get_key(): messages}})
        return state

    def set_agent_answer(self, state: AgentState, answer: str) -> AgentState:
        """
        设置子agent的答案
        """

        state.update({"agent_answer": {self.get_key(): answer}})
        return state

    def set_sub_messages(
        self, state: AgentState, messages: list[AnyMessage]
    ) -> AgentState:
        """
        设置子agent的会话状态
        """

        state.update({self.get_state().get_message_key(): messages})
        return state

    def get_sub_messages(self, state: AgentState) -> list[AnyMessage]:
        """
        获取子agent的会话状态
        """

        return state.get(self.get_state().get_message_key(), [])

    def load_sub_messages(self, state: AgentState) -> AgentState:
        """
        从寄存器中加载子agent的会话状态
        """
        self.set_sub_messages(state, self.get_history_messages(state))
        self.clear_history_messages(state)
        return state

    def get_sub_messages_key(self) -> str:
        return self.get_state().get_message_key()

    def clear_history_messages(self, state: AgentState) -> AgentState:
        """
        清空子agent的会话状态
        """
        state.update({"agent_messages": {self.get_key(): []}})
        return state
