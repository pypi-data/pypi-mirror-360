from typing import (
    TypedDict,
    Callable,
    Any,
    Awaitable,
    Sequence,
    Type,
)

from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from langgraph.store.base import BaseStore
from langgraph.types import Checkpointer, All
from langgraph.utils.runnable import RunnableLike

from rain_ai.core.graph.default import MessagesState


def get_graph_builder(state: Type[TypedDict] | None = MessagesState) -> StateGraph:
    """
    创建一个 StateGraph 构建器实例

    Args:
        state (Type[TypedDict] | None): 图的状态类型定义，默认为 MessagesState

    Returns:
        StateGraph: 一个新的 StateGraph 实例
    """
    return StateGraph(state)


def add_graph_node(
    graph: StateGraph, node_name: str, node: RunnableLike | CompiledStateGraph
) -> StateGraph:
    """
    向图中添加一个节点

    Args:
        graph (StateGraph): 要添加节点的目标图
        node_name (str): 节点的名称
        node (RunnableLike | CompiledStateGraph): 执行的函数（节点）或者已编译的状态图

        RunnableLike 示例:
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


def get_graph_tool_node(tools: Sequence[BaseTool | Callable]) -> ToolNode:
    """
    获取图中指定名称的节点的可运行对象

    Args:
        tools (Sequence[BaseTool | Callable]): 工具列表或可调用对象列表

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


def add_graph_conditional_edge(
    graph: StateGraph,
    from_node: str,
    condition: Callable[..., Any],
    conditional_mapping: dict[str, str],
) -> StateGraph:
    """
    在图中的一个节点后添加一条条件边

    Args:
        graph (StateGraph): 要添加边的目标图
        from_node (str): 边的起始节点名称
        condition (Callable[..., Any]): 条件函数，用于决定边的目标节点
        conditional_mapping (dict[str, str]): 条件映射，用于将条件结果映射到目标节点名称

        condition 示例：
                def condition(state: State):
                    return "one" if state["condition"] else "two"
        conditional_mapping 示例：
                {
                    "one": "next_node",
                    "two": "fallback_node"
                }

    Returns:
        StateGraph: 添加条件边后的图实例
    """
    return graph.add_conditional_edges(from_node, condition, conditional_mapping)


def set_graph_entry_point(graph: StateGraph, node_name: str) -> StateGraph:
    """
    设置图的入口节点

    Args:
        graph (StateGraph): 目标图
        node_name (str): 要设置为入口节点的节点名称

    Returns:
        StateGraph: 设置入口节点后的图实例
    """
    return graph.set_entry_point(node_name)


def set_graph_finish_point(graph: StateGraph, node_name: str) -> StateGraph:
    """
    设置图的结束节点

    Args:
        graph (StateGraph): 目标图
        node_name (str): 要设置为结束节点的节点名称

    Returns:
        StateGraph: 设置结束节点后的图实例
    """
    return graph.set_finish_point(node_name)


def compile_graph(
    graph: StateGraph,
    checkpointer: Checkpointer | None = None,
    interrupt_before: All | list[str] | None = None,
    interrupt_after: All | list[str] | None = None,
    debug: bool | None = None,
    store: BaseStore | None = None,
) -> CompiledStateGraph:
    """
    编译状态图

    Args:
        graph (StateGraph): 要编译的图
        checkpointer (Checkpointer | None): 可选的检查点对象，用于保存和恢复图状态
        interrupt_before (All | list[str] | None): 可选的中断前节点列表，默认为 None
        interrupt_after (All | list[str] | None): 可选的中断后节点列表，默认为 None
        debug (bool | None): 是否启用调试模式，默认为 False
        store (BaseStore | None): 可选的存储对象，用于持久化图状态

    Returns:
        CompiledStateGraph: 编译后的可执行状态图
    """
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before,
        interrupt_after=interrupt_after,
        debug=debug,
        store=store,
    )


def stream_graph(
    graph: CompiledStateGraph, state: dict, config: dict | None = None
) -> Awaitable[Any]:
    """
    流式执行图，返回一个可等待的结果

    Args:
        graph (CompiledStateGraph): 已编译的状态图
        state (dict): 初始状态
        config (dict | None): 可选的配置参数

    Returns:
        Awaitable[Any]: 可等待的执行结果
    """
    return graph.arun(state, config)
