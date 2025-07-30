from typing import Any

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore


def get_document(page_content: str, metadata: dict[str, str]) -> Document:
    """
    创建一个 Document 实例

    Args:
        page_content (str): 文档的内容
        metadata (dict[str, str]): 文档的元数据，包含额外信息如标题、作者等

    Returns:
        Document: 创建的 Document 实例

    """

    return Document(page_content, metadata=metadata)


def get_document_by_ids(
    vector_store: VectorStore, ids: list[str] | None
) -> list[Document]:
    """
    根据 ID 从向量存储中获取文档

    Args:
        vector_store (VectorStore): 向量存储实例
        ids (list[str] | None): 文档的唯一标识符列表。如果未提供，将获取所有文档

    Returns:
        List[Document]: 获取的文档列表

    """

    return vector_store.get_by_ids(ids)


async def a_get_document_by_ids(
    vector_store: VectorStore, ids: list[str] | None
) -> list[Document]:
    """
    异步根据 ID 从向量存储中获取文档

    Args:
        vector_store (VectorStore): 向量存储实例
        ids (list[str] | None): 文档的唯一标识符列表。如果未提供，将获取所有文档

    Returns:
        List[Document]: 获取的文档列表

    """

    return await vector_store.aget_by_ids(ids)


def add_context(
    vector_store: VectorStore,
    context: list[Any],
    ids: list[str] | None = None,
) -> list[str]:
    """
    向向量存储中添加上下文

    Args:
        vector_store (VectorStore): 向量存储实例
        context (list[Any]): 要添加的上下文列表
        ids (list[str] | None): 上下文的唯一标识符列表。如果未提供，将自动生成

    Returns:
        List[str]: 添加的上下文 ID 列表

    """

    return vector_store.add_documents(
        list(map(lambda x: get_document(x, {}), context)), ids=ids
    )


async def a_add_context(
    vector_store: VectorStore,
    context: list[Any],
    ids: list[str] | None = None,
) -> list[str]:
    """
    异步向向量存储中添加上下文

    Args:
        vector_store (VectorStore): 向量存储实例
        context (list[Any]): 要添加的上下文列表
        ids (list[str] | None): 上下文的唯一标识符列表。如果未提供，将自动生成

    Returns:
        List[str]: 添加的上下文 ID 列表

    """

    return await vector_store.aadd_documents(
        list(map(lambda x: get_document(x, {}), context)), ids=ids
    )


def add_documents(
    vector_store: VectorStore,
    documents: list[Document],
    ids: list[str] | None = None,
) -> list[str]:
    """
    向向量存储中添加文档

    Args:
        vector_store (VectorStore): 向量存储实例。
        documents (List[Document]): 要添加的文档列表。
        ids (list[str] | None): 文档的唯一标识符列表。如果未提供，将自动生成。

    Returns:
        List[str]: 添加的文档 ID 列表。

    """
    return vector_store.add_documents(documents, ids=ids)


async def a_add_documents(
    vector_store: VectorStore,
    documents: list[Document],
    ids: list[str] | None = None,
) -> list[str]:
    """
    异步向向量存储中添加文档

    Args:
        vector_store (VectorStore): 向量存储实例。
        documents (List[Document]): 要添加的文档列表。
        ids (list[str] | None): 文档的唯一标识符列表。如果未提供，将自动生成。

    Returns:
        List[str]: 添加的文档 ID 列表。

    """
    return await vector_store.aadd_documents(documents, ids=ids)


def delete(vector_store: VectorStore, ids: list[str]) -> None:
    """
    从向量存储中删除指定的文档

    Args:
        vector_store (VectorStore): 向量存储实例。
        ids (List[str]): 要删除的文档 ID 列表。

    """

    vector_store.delete(ids)


async def a_delete(vector_store: VectorStore, ids: list[str]) -> None:
    """
    异步从向量存储中删除指定的文档

    Args:
        vector_store (VectorStore): 向量存储实例。
        ids (List[str]): 要删除的文档 ID 列表。

    """

    return await vector_store.adelete(ids)


def similarity_search(
    vector_store: VectorStore,
    query: str,
    k: int = 5,
    metadata_filter: dict[str, str] | None = None,
) -> list[Document]:
    """
    在向量存储中执行相似性搜索

    Args:
        vector_store (VectorStore): 向量存储实例
        query (str): 查询字符串
        k (int): 返回的最相似文档的数量，默认为 5
        metadata_filter (dict[str, str] | None): 可选的元数据过滤器，用于限制搜索结果

    Returns:
        List[Document]: 与查询最相似的文档列表

    """

    return vector_store.similarity_search(query, k=k, filter=metadata_filter)


__all__ = [
    "get_document",
    "get_document_by_ids",
    "a_get_document_by_ids",
    "add_context",
    "a_add_context",
    "add_documents",
    "a_add_documents",
    "delete",
    "a_delete",
    "similarity_search",
]
