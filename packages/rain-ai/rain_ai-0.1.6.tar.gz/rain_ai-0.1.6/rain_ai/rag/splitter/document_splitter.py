from typing import Callable

from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    Language,
    TokenTextSplitter,
    TextSplitter,
)


def get_text_splitter(
    separator: str = "\n\n",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    length_function: Callable[[str], int] = len,
    is_separator_regex: bool = False,
) -> TextSplitter:
    """
    创建字符文本分割器实例

    Args:
        separator (str, optional): 用于分割文本的分隔符。默认为 "\n\n"（双换行符）
        chunk_size (int, optional): 每个文本块的最大字符数。默认为 1000
        chunk_overlap (int, optional): 相邻文本块之间重叠的字符数。默认为 200
        length_function (Callable[[str], int], optional): 用于计算文本长度的函数。默认为 len
        is_separator_regex (bool, optional): 分隔符是否为正则表达式。默认为 False

    Returns:
        CharacterTextSplitter: 字符文本分割器实例，可用于将长文本分割成指定大小的文本块
    """
    return CharacterTextSplitter(
        separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function,
        is_separator_regex=is_separator_regex,
    )


def get_text_splitter_separator_list(
    separators: list[str] = ("\n\n", "\n", " ", ".", ","),
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    length_function: Callable[[str], int] = len,
    is_separator_regex: bool = False,
) -> TextSplitter:
    """
    创建递归字符文本分割器实例（支持多个分隔符）

    Args:
        separators (list[str], optional): 分隔符列表，按优先级顺序排列。默认为 ("\n\n", "\n", " ", ".", ",")
        chunk_size (int, optional): 每个文本块的最大字符数。默认为 1000
        chunk_overlap (int, optional): 相邻文本块之间重叠的字符数。默认为 200
        length_function (Callable[[str], int], optional): 用于计算文本长度的函数。默认为 len
        is_separator_regex (bool, optional): 分隔符是否为正则表达式。默认为 False

    Returns:
        RecursiveCharacterTextSplitter: 递归字符文本分割器实例，可用于按多个分隔符优先级分割文本
    """
    return RecursiveCharacterTextSplitter(
        separators,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function,
        is_separator_regex=is_separator_regex,
    )


def get_code_splitter(
    language: Language, chunk_size: int = 1000, chunk_overlap: int = 200
) -> TextSplitter:
    """
    创建代码文本分割器实例

    Args:
        language (Language): 编程语言类型，用于选择合适的代码分割规则
        chunk_size (int, optional): 每个代码块的最大字符数。默认为 1000
        chunk_overlap (int, optional): 相邻代码块之间重叠的字符数。默认为 200

    Returns:
        RecursiveCharacterTextSplitter: 专门针对指定编程语言优化的递归字符文本分割器实例
    """
    return RecursiveCharacterTextSplitter.from_language(
        language, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )


def get_markdown_splitter(
    chunk_size: int = 1000, chunk_overlap: int = 200
) -> TextSplitter:
    """
    创建 Markdown 文本分割器实例

    Args:
        chunk_size (int, optional): 每个 Markdown 块的最大字符数。默认为 1000
        chunk_overlap (int, optional): 相邻 Markdown 块之间重叠的字符数。默认为 200

    Returns:
        RecursiveCharacterTextSplitter: 专门针对 Markdown 格式优化的递归字符文本分割器实例
    """
    return RecursiveCharacterTextSplitter.from_language(
        Language.MARKDOWN, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )


def get_token_text_splitter(
    chunk_size: int = 1000, chunk_overlap: int = 200
) -> TextSplitter:
    """
    创建 Token 文本分割器实例

    Args:
        chunk_size (int, optional): 每个文本块的最大 Token 数量。默认为 1000
        chunk_overlap (int, optional): 相邻文本块之间重叠的 Token 数量。默认为 200

    Returns:
        TokenTextSplitter: Token 文本分割器实例，基于 Token 计数而非字符数进行文本分割
    """
    return TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


__all__ = [
    "get_text_splitter",
    "get_text_splitter_separator_list",
    "get_code_splitter",
    "get_markdown_splitter",
    "get_token_text_splitter",
]
