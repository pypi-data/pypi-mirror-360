from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter


def split_content(splitter: TextSplitter, text: str) -> list[Document]:
    """
    使用文本分割器分割单个文本内容

    Args:
        splitter (TextSplitter): 文本分割器实例，用于执行文本分割操作
        text (str): 要分割的单个文本字符串

    Returns:
        list[Document]: 分割后的文档对象列表，每个文档包含一个文本块和相应的元数据
    """

    return splitter.create_documents([text])


def split_content_to_list(splitter: TextSplitter, texts: list[str]) -> list[Document]:
    """
    使用文本分割器批量分割多个文本内容

    Args:
        splitter (TextSplitter): 文本分割器实例，用于执行文本分割操作
        texts (list[str]): 要分割的文本字符串列表

    Returns:
        list[Document]: 分割后的文档对象列表，包含所有输入文本分割后的文本块和相应的元数据
    """

    return splitter.create_documents(texts)


__all__ = ["split_content", "split_content_to_list"]
