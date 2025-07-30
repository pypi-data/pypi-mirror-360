from typing import Iterator, AsyncIterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter


def load_content(loader: BaseLoader) -> list[Document]:
    """
    同步加载文档内容

    Args:
        loader (BaseLoader): 文档加载器实例

    Returns:
        List[Document]: 加载的文档列表，包含所有页面或文档内容
    """

    return loader.load()


async def a_load_content(loader: BaseLoader) -> list[Document]:
    """
    异步加载文档内容

    Args:
        loader (BaseLoader): 文档加载器实例

    Returns:
        List[Document]: 异步加载的文档列表，包含所有页面或文档内容
    """

    return await loader.aload()


def lazy_load_content(loader: BaseLoader) -> Iterator[Document]:
    """
    懒加载文档内容（同步迭代器）

    Args:
        loader (BaseLoader): 文档加载器实例

    Returns:
        Iterator[Document]: 同步文档迭代器，按需加载文档内容以节省内存
    """

    return loader.lazy_load()


def a_lazy_load_content(loader: BaseLoader) -> AsyncIterator[Document]:
    """
    异步懒加载文档内容

    Args:
        loader (BaseLoader): 文档加载器实例

    Returns:
        AsyncIterator[Document]: 异步文档迭代器，按需异步加载文档内容以节省内存
    """

    return loader.alazy_load()


def load_content_and_split(
    loader: BaseLoader, text_splitter: Optional[TextSplitter] = None
) -> List[Document]:
    """
    加载文档内容并进行文本分割

    Args:
        loader (BaseLoader): 文档加载器实例
        text_splitter (Optional[TextSplitter], optional): 文本分割器，用于将文档分割成较小的块。默认为 None

    Returns:
        List[Document]: 加载并分割后的文档块列表
    """

    return loader.load_and_split(text_splitter=text_splitter)


__all__ = [
    "load_content",
    "a_load_content",
    "lazy_load_content",
    "a_lazy_load_content",
    "load_content_and_split",
]
