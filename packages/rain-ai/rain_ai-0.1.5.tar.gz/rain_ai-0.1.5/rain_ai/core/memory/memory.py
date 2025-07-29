from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore


def get_in_memory_saver() -> BaseCheckpointSaver[str]:
    """
    创建一个基于内存的检查点保存器

    Returns:
        InMemorySaver: 用于在内存中保存检查点的对象
    """
    return InMemorySaver()


def get_in_memory_store() -> BaseStore:
    """
    创建一个基于内存的存储对象

    Returns:
        InMemoryStore: 用于在内存中存储数据的对象
    """
    return InMemoryStore()


__all__ = ["get_in_memory_saver", "get_in_memory_store"]
