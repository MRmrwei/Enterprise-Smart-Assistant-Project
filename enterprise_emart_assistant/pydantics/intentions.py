from typing import Literal, Optional

from pydantic import BaseModel, Field


class Intention(BaseModel):
    type: Literal["fill_form", "knowledge_ingest", "qa", "data_query", "unknown"] = (
        Field(description="意图类型")
    )

    description: str = Field(description="意图描述")
    vital_content: str = Field(description="重要信息")
    file_path: Optional[str] = Field(description="文件路径")
    origin_input: Optional[str] = Field(default="")  # 设为可选，默认空字符串
