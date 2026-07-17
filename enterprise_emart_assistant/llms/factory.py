from typing import Literal
from configs.config import config
from llms.base import LLMConfig
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models.chat_models import BaseChatModel

ProviderType = Literal["deepseek"]


def _load_config_from_env(provider: str) -> LLMConfig:
    return LLMConfig(
        api_key=config.get(f"{provider}_API_KEY", ""),
        base_url=config.get(f"{provider}_BASE_URL", ""),
        model=config.get(f"{provider}_MODEL", ""),
        temperature=float(config.get(f"{provider}_TEMPERATURE", 0.7)),
        timeout=int(config.get(f"{provider}_TIMEOUT", 60)),
    )


def create_llm(provider: ProviderType | None = None, **overrides) -> BaseChatModel:
    """
    LLM 工厂函数，根据 provider 创建对应的 LLM 实例。

    Args:
        provider: 模型提供商，默认从环境变量 LLM_PROVIDER 读取，否则使用 deepseek
        **overrides: 覆盖默认配置参数

    Returns:
        BaseLLM 实例
    """

    if provider is None:
        provider = config.get("LLM_PROVIDER", "deepseek")

    llm_config = _load_config_from_env(provider)

    model = llm_config.model
    if overrides.get("model", None) is not None:
        model = overrides["model"]

    response_format = {"type": "text"}
    if overrides.get("response_format", None) is not None:
        response_format = overrides["response_format"]

    if provider == "deepseek":
        return ChatDeepSeek(
            model=model,
            api_key=llm_config.api_key,
            temperature=llm_config.temperature,
            timeout=llm_config.timeout,
            model_kwargs={"response_format": response_format},
        )
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")


def get_default_llm(**overrides) -> BaseChatModel:
    return create_llm(None, **overrides)


def get_llm(provider: ProviderType | None = None, **overrides) -> BaseChatModel:
    return create_llm(provider=provider, **overrides)
