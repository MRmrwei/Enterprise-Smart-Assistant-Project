import json
from turtle import st
from typing import Optional
from starlette.requests import ClientDisconnect
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel
from collections.abc import AsyncIterable
import logging
from pydantics.sse import SSEContent
from core.context import context
from services.agent import AgentService

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    question: str | None
    thread_id: str | None = ""


router = APIRouter()


@router.post("/chat", response_class=EventSourceResponse)
async def chat(
    chatRequest: ChatRequest, request: Request
) -> AsyncIterable[ServerSentEvent]:

    uid = context.get().uid
    thread_id = chatRequest.thread_id or AgentService.get_thread_id(uid)

    if chatRequest.thread_id == "" or chatRequest.thread_id is None:
        yield ServerSentEvent(
            data={"thread_id": thread_id},
            event="init",
        )

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    state = {
        "state": "employee",
        "question": chatRequest.question,
        "role": "employee",
        "uid": uid,
        "answer": "",
    }

    async for result in AgentService().Chat(state, config):
        yield ServerSentEvent(data=result.data, event=result.event)
