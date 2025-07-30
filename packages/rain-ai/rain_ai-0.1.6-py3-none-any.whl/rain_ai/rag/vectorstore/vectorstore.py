import chromadb
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore, VectorStore


def get_in_memory_vectorstore(embedding: Embeddings) -> VectorStore:
    """
    创建一个基于内存的向量存储
    Args:
        embedding (Embeddings): 用于向量化的嵌入模型

    Returns:
        InMemoryVectorStore: 返回一个基于内存的向量存储实例

    """

    return InMemoryVectorStore(embedding)


def get_chroma_vectorstore(
    collection_name: str,
    embedding: Embeddings | None = None,
    persist_directory: str | None = "./chroma_db",
    client_settings: chromadb.config.Settings | None = None,
    collection_metadata: dict | None = None,
    client: chromadb.ClientAPI | None = None,
    create_collection_if_not_exists: bool | None = True,
) -> VectorStore:
    """
    创建一个 Chroma 向量存储实例

    Args:
        collection_name (str): 要创建或加载的集合的名称
        embedding (Embeddings): 用于向量化的嵌入模型
        persist_directory (str | None): 持久化目录的路径如果为 None，则在内存中创建
        client_settings (chromadb.config.Settings | None): Chroma 客户端的配置
        collection_metadata (dict | None): 集合的元数据
        client (chromadb.ClientAPI | None): 一个已有的 Chroma 客户端实例
        create_collection_if_not_exists (bool | None): 如果集合不存在，是否创建它默认为 True

    Returns:
        VectorStore: 返回一个 Chroma 向量存储实例

    """

    return Chroma(
        collection_name,
        embedding_function=embedding,
        persist_directory=persist_directory,
        client_settings=client_settings,
        collection_metadata=collection_metadata,
        client=client,
        create_collection_if_not_exists=create_collection_if_not_exists,
    )


def get_http_chroma_vectorstore(
    host: str,
    port: int,
    collection_name: str,
    embedding: Embeddings | None = None,
    collection_metadata: dict | None = None,
    create_collection_if_not_exists: bool | None = True,
) -> VectorStore:
    """
    通过 HTTP 连接到远程 Chroma 数据库并创建向量存储实例

    这是一个便捷函数，它会创建一个 HttpClient 并调用 get_chroma_vectorstore

    Args:
        host (str): Chroma 数据库服务器的主机名或 IP 地址
        port (int): Chroma 数据库服务器的端口号
        collection_name (str): 要创建或加载的集合的名称
        embedding (Embeddings): 用于向量化的嵌入模型
        collection_metadata (dict | None): 集合的元数据
        create_collection_if_not_exists (bool | None): 如果集合不存在，是否创建它默认为 True

    Returns:
        VectorStore: 返回一个连接到远程 Chroma 数据库的向量存储实例

    """

    client = chromadb.HttpClient(host, port)
    return get_chroma_vectorstore(
        collection_name,
        embedding,
        collection_metadata=collection_metadata,
        client=client,
        create_collection_if_not_exists=create_collection_if_not_exists,
    )


__all__ = [
    "get_in_memory_vectorstore",
    "get_chroma_vectorstore",
    "get_http_chroma_vectorstore",
]
