import asyncio
from typing import Optional
import grpc.aio
from langchain.messages import AIMessage
import ai_pb2
import ai_pb2_grpc
from services.agent import AgentService
from services.sse import SSEContent
import random
import string


class AgentRpc(ai_pb2_grpc.aiServicer):

    agentService: AgentService

    def __init__(self, agentService: AgentService):
        self.agentService = agentService

    async def Chat(
        self, request: ai_pb2.ChatRequest, context: grpc.aio.ServicerContext
    ):

        thread_id = (
            request.threadId
            or f"{generate_strong_id()}_{get_metadata_value(context, 'uid')}"
        )

        if request.threadId == "" or request.threadId is None:
            yield ai_pb2.ChatResponse(data=SSEContent({"thread_id": thread_id}, "init"))

       

        config = {"configurable": {"thread_id": thread_id}}
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


def get_metadata_value(
    context: grpc.aio.ServicerContext, key: str, default: Optional[str] = None
) -> Optional[str]:
    """
    从 gRPC 上下文中安全获取指定 metadata 键的值。

    Args:
        context: gRPC 异步服务上下文
        key: 要查找的键名（大小写不敏感）
        default: 找不到时返回的默认值，默认为 None

    Returns:
        对应的值，若不存在则返回 default
    """
    metadata = context.invocation_metadata()
    key_lower = key.lower()
    for k, v in metadata:
        if k.lower() == key_lower:
            return v
    return default


def generate_strong_id(length=12):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))
