import json


def SSEContent(data: str | None = "", type: str | None = "message"):
    return f"event: {type}\ndata: {json.dumps(data)}\n\n"
