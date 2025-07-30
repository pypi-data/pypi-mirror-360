from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def load_open_ai_api_chat_model(
    base_url: str,
    api_key: str,
    model_name: str,
    temperature: Optional[float] = None,
    timeout: Optional[float] = None,
    streaming: Optional[bool] = False,
    max_tokens: Optional[int] = None,
    max_retries: Optional[int] = None,
    verbose: bool = False,
) -> BaseChatModel:
    """
    创建并配置OpenAI聊天模型实例

    Args:
        base_url (str): OpenAI API的基础URL，可用于自定义或代理端点
        api_key (str): 用于认证的OpenAI API密钥
        model_name (str): 要使用的OpenAI模型名称
        temperature (Optional[float]): 控制输出随机性的温度参数，较高值生成更多样化结果默认为None，使用API默认值
        timeout (Optional[float]): API请求超时时间（秒）默认为None，使用客户端默认值
        streaming (Optional[bool]): 是否启用流式响应默认为False
        max_tokens (Optional[int]): 响应中生成的最大令牌数默认为None，使用API默认值
        max_retries (Optional[int]): 请求失败时的最大重试次数默认为None，使用客户端默认值
        verbose (bool): 是否启用详细日志输出默认为False

    Returns:
        BaseChatModel: 配置好的OpenAI聊天模型实例，可用于生成对话响应
    """
    return ChatOpenAI(
        base_url=base_url,
        api_key=SecretStr(api_key),
        model=model_name,
        temperature=temperature,
        timeout=timeout,
        streaming=streaming,
        max_tokens=max_tokens,
        max_retries=max_retries,
        verbose=verbose,
    )


def load_deepseek_chat_model(
    api_key: str,
    model_name: str,
    temperature: Optional[float] = None,
    timeout: Optional[float] = None,
    streaming: Optional[bool] = False,
    max_tokens: Optional[int] = None,
    max_retries: Optional[int] = None,
    verbose: bool = False,
) -> BaseChatModel:
    """
    创建并配置DeepSeek聊天模型实例

    Args:
        api_key (str): 用于认证的DeepSeek API密钥
        model_name (str): 要使用的DeepSeek模型名称
        temperature (Optional[float]): 控制输出随机性的温度参数，较高值生成更多样化结果默认为None，使用API默认值
        timeout (Optional[float]): API请求超时时间（秒）默认为None，使用客户端默认值
        streaming (Optional[bool]): 是否启用流式响应默认为False
        max_tokens (Optional[int]): 响应中生成的最大令牌数默认为None，使用API默认值
        max_retries (Optional[int]): 请求失败时的最大重试次数默认为None，使用客户端默认值
        verbose (bool): 是否启用详细日志输出默认为False

    Returns:
        BaseChatModel: 配置好的DeepSeek聊天模型实例，可用于生成对话响应
    """
    return load_open_ai_api_chat_model(
        base_url="https://api.deepseek.com/v1",
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        timeout=timeout,
        streaming=streaming,
        max_tokens=max_tokens,
        max_retries=max_retries,
        verbose=verbose,
    )


def load_ollama_localhost_chat_model(
    api_key: str,
    model_name: str,
    temperature: Optional[float] = None,
    timeout: Optional[float] = None,
    streaming: Optional[bool] = False,
    max_tokens: Optional[int] = None,
    max_retries: Optional[int] = None,
    verbose: bool = False,
) -> BaseChatModel:
    """
    创建并配置Ollama本地聊天模型实例

    该函数连接到本地运行的Ollama服务，用于在本地环境中使用开源大语言模型

    Args:
         api_key (str): 用于认证的DeepSeek API密钥
         model_name (str): 要使用的DeepSeek模型名称
         temperature (Optional[float]): 控制输出随机性的温度参数，较高值生成更多样化结果默认为None，使用API默认值
         timeout (Optional[float]): API请求超时时间（秒）默认为None，使用客户端默认值
         streaming (Optional[bool]): 是否启用流式响应默认为False
         max_tokens (Optional[int]): 响应中生成的最大令牌数默认为None，使用API默认值
         max_retries (Optional[int]): 请求失败时的最大重试次数默认为None，使用客户端默认值
         verbose (bool): 是否启用详细日志输出默认为False

    Returns:
        BaseChatModel: 配置好的Ollama聊天模型实例，可用于生成对话响应
    """
    return load_open_ai_api_chat_model(
        base_url="http://127.0.0.1:11434/v1",
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        timeout=timeout,
        streaming=streaming,
        max_tokens=max_tokens,
        max_retries=max_retries,
        verbose=verbose,
    )


__all__ = [
    "load_open_ai_api_chat_model",
    "load_deepseek_chat_model",
    "load_ollama_localhost_chat_model",
]
