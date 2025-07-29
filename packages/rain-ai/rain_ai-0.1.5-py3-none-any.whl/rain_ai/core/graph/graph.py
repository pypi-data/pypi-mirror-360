from typing import (
    TypedDict,
    Optional,
    Union,
    Callable,
    Any,
    Hashable,
    Awaitable,
    Sequence,
)

from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from langgraph.store.base import BaseStore
from langgraph.types import Checkpointer, All
from langgraph.utils.runnable import RunnableLike

from rain_ai.core.graph.default import MessagesState


def get_graph_builder(state: Optional[type[TypedDict]] = MessagesState) -> StateGraph:
    """
    创建一个 StateGraph 构建器实例

    Args:
        state (Optional[type[TypedDict]]): 图的状态类型定义，默认为 MessagesState

    Returns:
        StateGraph: 一个新的 StateGraph 实例
    """
    return StateGraph(state)


def add_graph_node(
    graph: StateGraph, node_name: str, node: Union[RunnableLike, CompiledStateGraph]
) -> StateGraph:
    """
    向图中添加一个节点

    Args:
        graph (StateGraph): 要添加节点的目标图
        node_name (str): 节点的名称
        node (Union[RunnableLike, CompiledStateGraph]): 执行的函数（节点）或者已编译的状态图

        RunnableLike 示例：
            def chatbot(state: State):
                return {"messages": [llm.invoke(state["messages"])]}

    Returns:
        StateGraph: 添加节点后的图实例
    """
    return graph.add_node(node_name, node)


def add_graph_nodes_from_dict(
    graph: StateGraph, nodes: dict[str, RunnableLike]
) -> StateGraph:
    """
    从字典中批量添加节点到图中

    Args:
        graph (StateGraph): 要添加节点的目标图
        nodes (dict[str, RunnableLike]): 一个字典，键是节点名称，值是节点要执行的函数或可运行对象

    RunnableLike 示例：
            def chatbot(state: State):
                return {"messages": [llm.invoke(state["messages"])]}

    Returns:
        StateGraph: 添加所有节点后的图实例
    """
    for node_name, node_function in nodes.items():
        graph = add_graph_node(graph, node_name, node_function)
    return graph


def get_graph_tool_node(tools: Sequence[Union[BaseTool, Callable]]) -> ToolNode:
    """
    获取图中指定名称的节点的可运行对象

    Args:
        tools (Sequence[Union[BaseTool, Callable]]): 工具列表或可调用对象列表

        注意：State 必须要有 "messages" 键，且传入的消息必须是 AIMessages 的数据，且必须有 tool_calls 值

    Returns:
        RunnableLike: 指定节点的可运行对象
    """
    return ToolNode(tools)


def add_graph_edge(graph: StateGraph, from_node: str, to_node: str) -> StateGraph:
    """
    在图中的两个节点之间添加一条边

    Args:
        graph (StateGraph): 要添加边的目标图
        from_node (str): 边的起始节点名称
        to_node (str): 边的结束节点名称

    Returns:
        StateGraph: 添加边后的图实例
    """
    return graph.add_edge(from_node, to_node)


def add_graph_edges_from_dict(graph: StateGraph, edges: dict[str, str]) -> StateGraph:
    """
    从字典中批量添加边到图中

    Args:
        graph (StateGraph): 要添加边的目标图
        edges (dict[str, str]): 一个字典，键是起始节点名称，值是目标节点名称

    Returns:
        StateGraph: 添加所有边后的图实例
    """
    for from_node, to_node in edges.items():
        graph = add_graph_edge(graph, from_node, to_node)
    return graph


def add_graph_conditional_edge(
    graph: StateGraph,
    from_node: str,
    path: Union[
        Callable[..., Union[Hashable, list[Hashable]]],
        Callable[..., Awaitable[Union[Hashable, list[Hashable]]]],
        Runnable[Any, Union[Hashable, list[Hashable]]],
    ],
    path_map: Optional[Union[dict[Hashable, str], list[str]]] = None,
) -> StateGraph:
    """
    在图中的一个节点后添加一条条件边

    Args:
        graph (StateGraph): 要添加边的目标图
        from_node (str): 边的起始节点名称
        path (Union[Callable[..., Union[Hashable, list[Hashable]]], Callable[..., Awaitable[Union[Hashable, list[Hashable]]]], Runnable[Any, Union[Hashable, list[Hashable]]]):
            条件函数或可运行对象，用于决定边的目标节点，可以直接返回 节点名称 或返回 path_map中定义的键
        path_map (Optional[Union[dict[Hashable, str], list[str]]]): 可选的路径映射，用于将条件结果映射到目标节点名称

        path 示例：
                def condition(state: State):
                    return "one" if state["condition"] else "two"
        path_map 示例：
                {
                    "one": "next_node",
                    "two": "fallback_node"
                }

    Returns:
        StateGraph: 添加条件边后的图实例
    """
    return graph.add_conditional_edges(source=from_node, path=path, path_map=path_map)


def set_graph_start(graph: StateGraph, start_node: str) -> StateGraph:
    """
    设置图的入口节点

    Args:
        graph (StateGraph): 目标图
        start_node (str): 要设置为入口节点的节点名称

    Returns:
        StateGraph: 设置入口节点后的图实例
    """
    return graph.set_entry_point(start_node)


def set_graph_end(graph: StateGraph, end_node: str) -> StateGraph:
    """
    设置图的结束节点

    Args:
        graph (StateGraph): 目标图
        end_node (str): 要设置为结束节点的节点名称

    Returns:
        StateGraph: 设置结束节点后的图实例
    """
    return graph.set_finish_point(end_node)


def validate_graph(graph: StateGraph) -> bool:
    """
    验证图的结构是否有效

    Args:
        graph (StateGraph): 要验证的图

    Returns:
        bool: 如果图已成功编译（通过验证），则返回 True，否则在验证失败时会抛出异常
    """
    graph.validate()
    return graph.compiled


def set_graph_compile(
    graph: StateGraph,
    name: Optional[str] = None,
    checkpointer: Checkpointer = None,
    store: Optional[BaseStore] = None,
    interrupt_before: Optional[Union[All, list[str]]] = None,
    interrupt_after: Optional[Union[All, list[str]]] = None,
    debug: bool = False,
) -> CompiledStateGraph:
    """
    编译状态图

    Args:
        graph (StateGraph): 要编译的图
        name (Optional[str]): 编译后图的名称，默认为 None
        checkpointer (Checkpointer): 可选的检查点对象，用于保存和恢复图状态
        store (Optional[BaseStore]): 可选的存储对象，用于持久化图状态
        interrupt_before (Optional[Union[All, list[str]]]): 可选的中断前节点列表，默认为 None
        interrupt_after (Optional[Union[All, list[str]]]): 可选的中断后节点列表，默认为 None
        debug (bool): 是否启用调试模式，默认为 False

    Returns:
        CompiledStateGraph: 编译后的可执行状态图
    """
    return graph.compile(
        name=name,
        checkpointer=checkpointer,
        store=store,
        interrupt_before=interrupt_before,
        interrupt_after=interrupt_after,
        debug=debug,
    )


__all__ = [
    "get_graph_builder",
    "add_graph_node",
    "add_graph_nodes_from_dict",
    "get_graph_tool_node",
    "add_graph_edge",
    "add_graph_edges_from_dict",
    "add_graph_conditional_edge",
    "set_graph_start",
    "set_graph_end",
    "validate_graph",
    "set_graph_compile",
]
