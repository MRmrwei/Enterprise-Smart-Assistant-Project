from pydantic import BaseModel


class SSEContent(BaseModel):
    data: dict | None = {}
    event: str | None = "message"
    id: str | None = ""
