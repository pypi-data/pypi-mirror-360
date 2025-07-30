from os import PathLike
from pathlib import Path
from typing import Literal, Sequence

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    WebBaseLoader,
    CSVLoader,
    BSHTMLLoader,
    JSONLoader,
    TextLoader,
)
from langchain_community.document_loaders.parsers import BaseImageBlobParser
from langchain_core.document_loaders import BaseLoader

from rain_ai.rag.loader.custom_loader import WordLoader, ExcelLoader


def get_text_loader(
    file_path: str | Path,
    encoding: str | None = None,
    autodetect_encoding: bool = False,
) -> BaseLoader:
    """
    创建文本文件加载器实例

    Args:
        file_path (str | Path): 文本文件的路径，支持字符串路径或 Path 对象
        encoding (str | None, optional): 文本文件的字符编码格式，如 "utf-8"、"gbk" 等。默认为 None，使用系统默认编码
        autodetect_encoding (bool, optional): 是否自动检测文件编码。默认为 False，使用指定的 encoding 参数

    Returns:
        BaseLoader: 文本加载器实例，可用于加载和解析文本文件内容

    """
    return TextLoader(
        file_path, encoding=encoding, autodetect_encoding=autodetect_encoding
    )


def get_pdf_loader(
    file_path: str,
    password: str | None = None,
    extract_images: bool = False,
    mode: Literal["single", "page"] = "page",
    images_inner_format: Literal["text", "markdown-img", "html-img"] = "text",
    extract_tables: Literal["csv", "markdown", "html"] | None = None,
    images_parser: BaseImageBlobParser | None = None,
) -> BaseLoader:
    """
    创建 PyMuPDF 文档加载器实例

    Args:
        file_path (str): PDF 文件路径，支持本地文件路径或网络 URL
        password (str | None, optional): PDF 文件密码，用于解密加密的 PDF 文件。默认为 None
        extract_images (bool, optional): 是否提取 PDF 中的图像内容。默认为 False
        mode (Literal["single", "page"], optional): 提取模式，"single" 为整个文档作为一个对象，"page" 为按页分割。默认为 "page"
        images_inner_format (Literal["text", "markdown-img", "html-img"], optional): 图像内容格式化方式。默认为 "text"
            - "text": 返回原始内容
            - "markdown-img": 包装为 Markdown 图像链接格式
            - "html-img": 包装为 HTML img 标签格式
        extract_tables (Literal["csv", "markdown", "html"] | None, optional): 表格提取格式，支持 csv、markdown、html 格式或 None。默认为 None
        images_parser (BaseImageBlobParser | None, optional): 自定义图像解析器。默认为 None

    Returns:
        BaseLoader: PyMuPDFLoader 实例，可用于加载和解析 PDF 文档
    """

    return PyMuPDFLoader(
        file_path,
        password=password,
        extract_images=extract_images,
        mode=mode,
        images_inner_format=images_inner_format,
        images_parser=images_parser,
        extract_tables=extract_tables,
    )


def get_web_loader(
    web_path: str | Sequence[str],
    requests_per_second: int = 2,
    raise_for_status: bool = False,
    show_progress: bool = True,
) -> BaseLoader:
    """
    创建 网页 内容加载器实例

    Args:
        web_path (str | Sequence[str]): 要加载的网页URL，可以是单个URL字符串或URL列表
        requests_per_second (int, optional): 每秒最大并发请求数。默认为 2
        raise_for_status (bool, optional): 当HTTP状态码表示错误时是否抛出异常。默认为 False
        show_progress (bool, optional): 是否显示页面加载进度条。默认为 True

    Returns:
        BaseLoader: WebBaseLoader 实例，可用于加载和解析网页内容
    """

    return WebBaseLoader(
        web_path,
        requests_per_second=requests_per_second,
        raise_for_status=raise_for_status,
        show_progress=show_progress,
    )


def get_csv_loader(
    file_path: str | Path,
    source_column: str | None = None,
    csv_args: dict | None = None,
    encoding: str | None = None,
    metadata_columns: Sequence[str] = (),
    content_columns: Sequence[str] = (),
) -> BaseLoader:
    """
    创建 CSV 文件加载器实例

    Args:
        file_path (str | Path): CSV 文件的路径，支持字符串或 Path 对象
        source_column (str | None, optional): 指定作为文档来源标识的列名。默认为 None，使用文件路径作为来源
        csv_args (dict | None, optional): 传递给 csv.DictReader 的参数字典，如分隔符、引号字符等。默认为 None
        encoding (str | None, optional): CSV 文件的字符编码格式，如 "utf-8"、"gbk" 等。默认为 None，使用系统默认编码
        metadata_columns (Sequence[str], optional): 用作元数据的列名序列，这些列不会包含在文档内容中。默认为空元组
        content_columns (Sequence[str], optional): 用作文档内容的列名序列，如果为空则使用所有非元数据列。默认为空元组

    Returns:
        BaseLoader: CSVLoader 实例，可用于加载和解析 CSV 文件内容
    """

    return CSVLoader(
        file_path,
        source_column=source_column,
        csv_args=csv_args,
        encoding=encoding,
        metadata_columns=metadata_columns,
        content_columns=content_columns,
    )


def get_local_html_loader(
    file_path: str | Path, open_encoding: str | None = None
) -> BaseLoader:
    """
    创建本地 HTML 文件加载器实例

    Args:
        file_path (str | Path): 本地 HTML 文件的路径，支持字符串路径或 Path 对象
        open_encoding (str | None, optional): 打开文件时使用的字符编码格式，如 "utf-8"、"gbk" 等。默认为 None，使用系统默认编码

    Returns:
        BaseLoader: BeautifulSoup HTML 加载器实例，可用于加载和解析本地 HTML 文件内容
    """

    return BSHTMLLoader(file_path, open_encoding=open_encoding)


def get_json_loader(
    file_path: str | PathLike,
    jq_schema: str = ".",
    content_key: str | None = None,
    is_content_key_jq_parsable: bool | None = False,
    text_content: bool = True,
    json_lines: bool = False,
) -> BaseLoader:
    """
    创建 JSON 文件加载器实例

    Args:
        file_path (str | PathLike): JSON 或 JSON Lines 文件的路径
        jq_schema (str, optional): 用于从 JSON 中提取数据的 jq 查询语句。默认为 "." (整个JSON对象)
        content_key (str | None, optional): 从 jq_schema 结果中提取内容的键名。默认为 None
        is_content_key_jq_parsable (bool | None, optional): 标识 content_key 是否可以被 jq 解析。默认为 False
        text_content (bool, optional): 指示内容是否为字符串格式。默认为 True
        json_lines (bool, optional): 指示输入是否为 JSON Lines 格式（每行一个JSON对象）。默认为 False

    Returns:
        BaseLoader: JSON 加载器实例，可用于加载和解析 JSON 或 JSON Lines 文件内容
    """

    return JSONLoader(
        file_path,
        jq_schema=jq_schema,
        content_key=content_key,
        is_content_key_jq_parsable=is_content_key_jq_parsable,
        text_content=text_content,
        json_lines=json_lines,
    )


def get_word_loader(
    file_path: str | Path, mode: Literal["page", "single"] = "page"
) -> BaseLoader:
    """
    创建 Word 文档加载器实例

    Args:
        file_path (str | Path): Word 文档(.docx)的文件路径
        mode (Literal["page", "single"], optional): 加载模式，"page" 为按页加载，"single" 为整个文档作为一个对象。默认为 "page"

    Returns:
        BaseLoader: Word 加载器实例，可用于加载和解析 Word 文档内容
    """

    return WordLoader(file_path, mode=mode)


def get_excel_loader(
    file_path: str | Path,
    mode: Literal["elements", "single"] = "single",
) -> BaseLoader:
    """
    创建 Excel 文档加载器实例

    Args:
        file_path (str | Path): Excel 文档(.xlsx)的文件路径
        mode (Literal["elements", "single"], optional): 加载模式，"elements" 为按工作表加载，"single" 为整个文档作为一个对象。默认为 "single"

    Returns:
        BaseLoader: Excel 加载器实例，可用于加载和解析 Excel 文档内容
    """

    return ExcelLoader(file_path, mode=mode)


__all__ = [
    "get_pdf_loader",
    "get_web_loader",
    "get_csv_loader",
    "get_local_html_loader",
    "get_json_loader",
    "get_word_loader",
    "get_excel_loader",
]
