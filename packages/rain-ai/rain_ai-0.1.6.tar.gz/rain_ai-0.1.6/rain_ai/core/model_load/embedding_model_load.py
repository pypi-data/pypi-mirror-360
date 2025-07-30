from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr


def load_open_ai_api_embedding_model(
    base_url: str,
    api_key: str,
    model_name: str,
    dimensions: int = 1024,
    timeout: float | None = None,
    max_retries: int | None = None,
) -> Embeddings:
    """
    加载OpenAI API的嵌入模型

    此函数创建并返回一个OpenAIEmbeddings实例，用于生成文本嵌入向量

    Args:
        base_url (str): OpenAI API的基础URL，可以是官方API或兼容API的端点
        api_key (str): 用于认证的API密钥
        model_name (str): 要使用的嵌入模型名称，例如'text-embedding-ada-002'
        dimensions (int, 可选): 嵌入向量的维度，默认为1024
        timeout (float, 可选): API请求的超时时间(秒)，None表示使用默认值
        max_retries (int, 可选): 请求失败时的最大重试次数，None表示使用默认值

    Returns:
        Embeddings: 配置好的OpenAIEmbeddings实例，可用于生成文本嵌入
    """
    return OpenAIEmbeddings(
        base_url=base_url,
        api_key=SecretStr(api_key),
        model=model_name,
        dimensions=dimensions,
        timeout=timeout,
        max_retries=max_retries,
    )


def load_ollama_localhost_embedding_model(
    api_key: str,
    model_name: str,
    dimensions: int = 1024,
    timeout: float | None = None,
    max_retries: int | None = None,
) -> Embeddings:
    """
     加载本地Ollama服务的嵌入模型

     此函数创建并返回一个OllamaEmbeddings实例，用于通过本地运行的Ollama服务，生成文本嵌入向量

    Args:
        api_key (str): 用于认证的API密钥
        model_name (str): 要使用的嵌入模型名称，例如'text-embedding-ada-002'
        dimensions (int, 可选): 嵌入向量的维度，默认为1024
        timeout (float, 可选): API请求的超时时间(秒)，None表示使用默认值
        max_retries (int, 可选): 请求失败时的最大重试次数，None表示使用默认值

     Returns:
         Embeddings: 配置好的OllamaEmbeddings实例，可用于生成文本嵌入
    """
    return load_open_ai_api_embedding_model(
        base_url="http://127.0.0.1:11434/v1",
        api_key=api_key,
        model_name=model_name,
        dimensions=dimensions,
        timeout=timeout,
        max_retries=max_retries,
    )


__all__ = ["load_open_ai_api_embedding_model", "load_ollama_localhost_embedding_model"]
