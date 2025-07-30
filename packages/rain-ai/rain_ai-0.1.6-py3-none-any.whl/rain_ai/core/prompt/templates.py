from typing import Sequence

from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.prompts.chat import MessageLikeRepresentation
from langchain_core.prompts.string import PromptTemplateFormat


def string_prompt_template(
    template: str, template_format: PromptTemplateFormat = "f-string"
) -> PromptTemplate:
    """
    创建一个字符串类型的提示模板

    此函数用于创建一个简单的字符串提示模板，可用于生成文本提示

    Args:
        template (str): 提示模板字符串，可以包含变量占位符
        template_format (PromptTemplateFormat, 可选): 模板格式，默认为"f-string"格式
            支持的格式包括"f-string"、"jinja2"等

    Returns:
        PromptTemplate: 配置好的提示模板对象，可用于生成最终提示文本
    """
    return PromptTemplate.from_template(
        template=template, template_format=template_format
    )


def chat_prompt_template(
    messages: Sequence[MessageLikeRepresentation],
    template_format: PromptTemplateFormat = "f-string",
) -> ChatPromptTemplate:
    """
    创建一个聊天提示模板

    此函数用于创建基于多条消息的聊天提示模板，适用于构建对话式AI的提示

    Args:
        messages (Sequence[MessageLikeRepresentation]): 消息序列，每条消息可以是系统消息、
            用户消息或AI助手消息等不同角色的消息
        template_format (PromptTemplateFormat, 可选): 模板格式，默认为"f-string"格式
            支持的格式包括"f-string"、"jinja2"等

    Returns:
        ChatPromptTemplate: 配置好的聊天提示模板对象，可用于生成结构化的对话提示
    """
    return ChatPromptTemplate(messages=messages, template_format=template_format)


def messages_placeholder(variable_name: str) -> MessagesPlaceholder:
    """
    创建一个消息占位符

    此函数用于在聊天提示模板中创建消息列表的占位符，通常用于引用聊天历史

    Args:
        variable_name (str): 变量名称，在提供实际值时用于引用此占位符

    Returns:
        MessagesPlaceholder: 消息占位符对象，可以插入到ChatPromptTemplate的消息列表中
    """
    return MessagesPlaceholder(variable_name=variable_name)


__all__ = ["string_prompt_template", "chat_prompt_template", "messages_placeholder"]
