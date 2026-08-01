from abc import ABC
from dataclasses import dataclass

@dataclass
class LLMConfig():
    """LLM 配置数据类"""
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.7
    timeout: int = 60

class BaseLLM(ABC):
    pass