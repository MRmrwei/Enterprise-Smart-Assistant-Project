from dataclasses import dataclass
from contextvars import ContextVar
from typing import Optional


@dataclass
class Context:
    token: str
    uid: int


context: ContextVar[Optional[Context]] = ContextVar("current_context", default=None)
