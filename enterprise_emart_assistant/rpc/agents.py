import asyncio
import grpc.aio
from langchain.messages import AIMessage
import ai_pb2
import ai_pb2_grpc
from graphs.main_graph import main_graph
from services.agent import AgentService
from services.sse import SSEContent


class AgentRpc(ai_pb2_grpc.aiServicer):

    agentService: AgentService

    def __init__(self, agentService: AgentService):
        self.agentService = agentService

    async def Chat(
        self, request: ai_pb2.ChatRequest, context: grpc.aio.ServicerContext
    ):
        config = {"configurable": {"thread_id": "user1"}}
        state = {
            "messages": [{"role": "user", "content": request.question}],
            "state": "employee",
            "role": "employee",
            "user_id": "user1",
            "answer": "",
        }
        try:
            async for result in self.agentService.Chat(request.question, state, config):
                yield ai_pb2.ChatResponse(data=result)
        except Exception as e:

            print(f"Error: {e}")
            yield ai_pb2.ChatResponse(data=SSEContent({"error": "未知错误"}, "error"))
