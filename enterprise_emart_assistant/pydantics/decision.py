from pydantic import BaseModel, Field


class AIDecision(BaseModel):
    node: str = Field(description="下一步节点")
    reason: str = Field(description="判断理由")
