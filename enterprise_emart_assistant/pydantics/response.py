from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应"""

    data: Optional[T] = None
    message: str = "成功"
    success: bool = True


class SSEContent(BaseModel, Generic[T]):
    data: Optional[T] = None
    event: str | None = "message"
    id: str | None = ""
