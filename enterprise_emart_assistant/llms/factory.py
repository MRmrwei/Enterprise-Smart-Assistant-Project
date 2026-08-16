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
        default_model=config.get(f"{provider}_DEFAULT_MODEL", ""),
        master_model=config.get(
            f"{provider}_MASTER_MODEL", config.get(f"{provider}_DEFAULT_MODEL", "")
        ),
        temperature=float(config.get(f"{provider}_TEMPERATURE", 0.7)),
        timeout=int(config.get(f"{provider}_TIMEOUT", 60)),
    )


def create_llm(
    provider: ProviderType | None = None, model_level: str | None = None
) -> BaseChatModel:
    """
    LLM 工厂函数，根据 provider 创建对应的 LLM 实例。

    Args:
        provider: 模型提供商，默认从环境变量 LLM_PROVIDER 读取，否则使用 deepseek
        **overrides: 覆盖默认配置参数

    Returns:
        BaseLLM 实例
    """
    if provider is None:
        provider = config.get("LLM_PROVIDER", "DEEPSEEK")

    llm_config = _load_config_from_env(provider)

    model = llm_config.default_model
    if model_level == "master":
        model = llm_config.master_model

    llm = None
    if provider.lower() == "deepseek":
        llm = ChatDeepSeek(
            model=model,
            api_key=llm_config.api_key,
            temperature=llm_config.temperature,
            timeout=llm_config.timeout,
        )
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")

    return llm


DEFAULT_LLM: BaseChatModel = None
MASTER_LLM: BaseChatModel = None


def get_default_llm(**overrides) -> BaseChatModel:
    """
    默认模型
    """
    global DEFAULT_LLM
    if DEFAULT_LLM is None:
        DEFAULT_LLM = create_llm(None)

    return DEFAULT_LLM.bind(**overrides)


def get_master_llm(**overrides) -> BaseChatModel:
    """
    旗舰模型
    """
    global MASTER_LLM
    if MASTER_LLM is None:
        MASTER_LLM = create_llm(None, "master")
    return MASTER_LLM.bind(**overrides)
