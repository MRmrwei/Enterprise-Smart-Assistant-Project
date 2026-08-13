from typing import Literal
from configs.config import config
from llms.base import LLMConfig
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models.chat_models import BaseChatModel
from langfuse.langchain import CallbackHandler

ProviderType = Literal["deepseek"]



def _load_config_from_env(provider: str) -> LLMConfig:
    return LLMConfig(
        api_key=config.get(f"{provider}_API_KEY", ""),
        base_url=config.get(f"{provider}_BASE_URL", ""),
        default_model=config.get(f"{provider}_DEFAULT_MODEL", ""),
        opus_model=config.get(
            f"{provider}_OPUS_MODEL", config.get(f"{provider}_DEFAULT_MODEL", "")
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
    if model_level == "opus":
        model = llm_config.opus_model

    # response_format = {"type": "text"}
    # if overrides.get("response_format", None) is not None:
    #     response_format = overrides["response_format"]

    llm = None
    if provider == "deepseek":
        llm = ChatDeepSeek(
            model=model,
            api_key=llm_config.api_key,
            temperature=llm_config.temperature,
            timeout=llm_config.timeout,
        )
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")

    # return llm.with_config(callbacks=[LANGFUSE_HANDLER])
    return llm


_default_llm: BaseChatModel = None
_opus_llm: BaseChatModel = None


def get_default_llm(**overrides) -> BaseChatModel:
    """
    默认模型
    """

    if _default_llm is None:
        _default_llm = create_llm(None)

    return _default_llm.bind(**overrides)


def get_opus_llm(**overrides) -> BaseChatModel:
    """
    旗舰模型
    """

    if _opus_llm is None:
        _opus_llm = create_llm(None, "opus")
    return _opus_llm.bind(**overrides)
