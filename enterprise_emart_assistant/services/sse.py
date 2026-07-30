def SSEContent(data: str | None = "", type: str | None = "message"):
    return f"event: {type}\n data: {data}\n\n"
