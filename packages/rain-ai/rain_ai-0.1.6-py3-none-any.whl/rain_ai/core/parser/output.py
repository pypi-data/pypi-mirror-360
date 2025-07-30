from enum import Enum

from langchain.output_parsers import (
    YamlOutputParser,
    BooleanOutputParser,
    EnumOutputParser,
)
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    XMLOutputParser,
)
from pydantic import BaseModel, Field, create_model


def create_dynamic_model(
    class_name: str, field_descriptions: dict[str, str]
) -> type[BaseModel]:
    """
    动态创建一个 Pydantic 模型类，类型默认为 str

    Args:
        class_name: 类的名称
        field_descriptions: 字典，键为字段名，值为字段描述

    Returns:
        动态创建的 Pydantic 模型类
    """
    fields = {}
    for field_name, description in field_descriptions.items():
        fields[field_name] = (str, Field(description=description))

    return create_model(class_name, **fields)


def create_dynamic_typed_model(
    class_name: str, field_descriptions: list[tuple[str, type, str]]
) -> type[BaseModel]:
    """
    动态创建一个 Pydantic 模型类，支持指定字段类型

    Args:
        class_name: 类的名称
        field_descriptions: 列表，包含元组 (字段名, 字段类型, 字段描述)

    Returns:
        动态创建的 Pydantic 模型类
    """
    fields = {}
    for field_name, field_type, description in field_descriptions:
        fields[field_name] = (field_type, Field(description=description))

    return create_model(class_name, **fields)


def create_str_output_parser() -> StrOutputParser:
    """
    创建一个字符串输出解析器

    Returns:
        StrOutputParser 实例
    """
    return StrOutputParser()


def create_bool_output_parser() -> BooleanOutputParser:
    """
    创建一个布尔输出解析器

    Returns:
        BooleanOutputParser 实例
    """
    return BooleanOutputParser()


def create_json_output_parser(pydantic_object: type[BaseModel]) -> JsonOutputParser:
    """
    创建一个 JSON 输出解析器

    Args:
        pydantic_object: Pydantic 模型类

    Returns:
        StrOutputParser 实例
    """
    return JsonOutputParser(pydantic_object=pydantic_object)


def create_xml_output_parser() -> XMLOutputParser:
    """
    创建一个 XML 输出解析器

    Returns:
        XMLOutputParser 实例
    """
    return XMLOutputParser()


def create_yaml_output_parser(pydantic_object: type[BaseModel]) -> YamlOutputParser:
    """
    创建一个 YAML 输出解析器

    Args:
        pydantic_object: Pydantic 模型类

    Returns:
        YamlOutputParser 实例
    """
    return YamlOutputParser(pydantic_object=pydantic_object)


def create_enum_output_parser(enum: type[Enum]) -> EnumOutputParser:
    """
    创建一个枚举输出解析器

    Args:
        enum: 枚举类，必须是 Enum 的子类

    Returns:
        EnumOutputParser 实例

    """
    return EnumOutputParser(enum=enum)


__all__ = [
    "create_dynamic_model",
    "create_dynamic_typed_model",
    "create_str_output_parser",
    "create_bool_output_parser",
    "create_json_output_parser",
    "create_xml_output_parser",
    "create_yaml_output_parser",
    "create_enum_output_parser",
]
