def SSEContent(data: str | None = "", type: str | None = "message"):
    return f"event: {type}\ndata: {data}\n\n"
