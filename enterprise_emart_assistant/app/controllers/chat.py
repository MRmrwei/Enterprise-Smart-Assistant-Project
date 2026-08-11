from fastapi import APIRouter, Request
from fastapi.sse import ServerSentEvent, EventSourceResponse
from pydantic import BaseModel
from collections.abc import AsyncIterable
from core.context import context
from services.agent import AgentService

router = APIRouter()


class ChatRequest(BaseModel):
    question: str | None
    thread_id: str | None = ""


@router.post("/chat", response_class=EventSourceResponse)
async def chat(
    chatRequest: ChatRequest, request: Request
) -> AsyncIterable[ServerSentEvent]:
    uid = context.get().uid
    thread_id = chatRequest.thread_id or AgentService.get_thread_id(uid)
    yield ServerSentEvent(data={"thread_id": thread_id}, event="start")

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    state = {
        "question": chatRequest.question,
        "uid": uid,
    }

    try:
        async for result in AgentService().Chat(state, config):
            yield ServerSentEvent(data=result.data, event=result.event)
    except Exception as e:
        yield ServerSentEvent(
            data={"content": "内部错误，请联系管理员！", "type": "answer"},
            event="error",
        )
        import traceback

        print(f"错误信息: {e}")
        print(f"完整堆栈:\n{traceback.format_exc()}")
