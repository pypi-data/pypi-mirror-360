import base64

import httpx
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    ToolCall,
)


def create_system_message(content: str | list[str | dict]) -> SystemMessage:
    """
    创建系统消息实例

    Args:
        content (str | list[str | dict]): 消息内容，可以是字符串或包含字符串和字典的列表

    Returns:
        SystemMessage: 创建的系统消息实例
    """
    return SystemMessage(content=content)


def create_user_message(content: str | list[str | dict]) -> HumanMessage:
    """
    创建用户消息实例

    Args:
        content (str | list[str | dict]): 消息内容，可以是字符串或包含字符串和字典的列表

    Returns:
        HumanMessage: 创建的用户消息实例
    """
    return HumanMessage(content=content)


def create_user_base64_image_message(
    text: str, image_base64_list: list[str]
) -> HumanMessage:
    """
    创建用户消息实例，包含Base64编码的图片

    Args:
        text (str): 消息内容，可以是字符串或包含字符串和字典的列表
        image_base64_list (list[str]): Base64编码的图片列表

    Returns:
        HumanMessage: 创建的用户消息实例，包含Base64编码的图片
    """
    content = [{"type": "text", "text": text}]

    for image_base64 in image_base64_list:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            }
        )

    return HumanMessage(content=content)


def create_user_url_image_message(
    text: str, image_url_list: list[str], is_base64: bool = False
) -> HumanMessage:
    """
    创建用户消息实例，包含图片

    Args:
        text (str): 消息内容，可以是字符串或包含字符串和字典的列表
        image_url_list (list[str]): 图片URL列表
        is_base64 (bool): 是否将图片URL转换为Base64编码的图片，默认为False

    Returns:
        HumanMessage: 创建的用户消息实例，包含图片
    """

    content = [{"type": "text", "text": text}]

    for image_url in image_url_list:
        if is_base64:
            image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                }
            )
        else:
            content.append({"type": "image_url", "image_url": {"url": image_url}})

    return HumanMessage(content=content)


def create_assistant_message(
    content: str | list[str | dict],
    tool_calls: list[ToolCall] | None = None,
) -> AIMessage:
    """
    创建助手消息实例

    Args:
        content (str | list[str | dict]): 消息内容，可以是字符串或包含字符串和字典的列表
        tool_calls (list[ToolCall] | None): 工具调用列表，默认为空

    Returns:
        AIMessage: 创建的助手消息实例
    """
    return AIMessage(
        content=content, tool_calls=tool_calls if tool_calls is not None else []
    )


def create_tool_message(
    content: str | list[str | dict], tool_call_id: str
) -> ToolMessage:
    """
    创建工具消息实例

    Args:
        content (str | list[str | dict]): 消息内容，可以是字符串或包含字符串和字典的列表
        tool_call_id (str): 此消息响应的工具调用ID

    Returns:
        ToolMessage: 创建的工具消息实例
    """
    return ToolMessage(content=content, tool_call_id=tool_call_id)


__all__ = [
    "create_system_message",
    "create_user_message",
    "create_user_base64_image_message",
    "create_user_url_image_message",
    "create_assistant_message",
    "create_tool_message",
]
