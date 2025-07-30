from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class MessagesState(TypedDict):
    """
    消息状态类，继承自 TypedDict。

    Args:
        messages (Annotated[List[AnyMessage], add_messages]): 存储消息的列表， add_messages 合并两个list 基于id决定是否更新还是插入
        is_last_step (bool): 是否为最后一步，默认为 False
    """

    messages: Annotated[list[AnyMessage], add_messages]
    is_last_step: bool


__all__ = ["MessagesState"]
