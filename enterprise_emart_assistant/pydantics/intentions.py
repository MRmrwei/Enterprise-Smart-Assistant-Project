from typing import Optional
from pydantic import BaseModel, Field


class Intention(BaseModel):
    type: Optional[str] | None = Field(description="意图类型")
    description: str = Field(description="意图描述")
    vital_content: str = Field(description="重要信息")
    file_path: Optional[str] = Field(description="文件路径")
