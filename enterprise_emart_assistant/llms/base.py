from abc import ABC
from dataclasses import dataclass

@dataclass
class LLMConfig():
    """LLM 配置数据类"""
    api_key: str
    base_url: str
    
    # 默认模型用于通用任务
    default_model: str
    # 旗舰模型用于复杂，高智商的任务
    opus_model: str
    temperature: float = 0.7
    timeout: int = 60
