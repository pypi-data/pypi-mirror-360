from typing import Literal, Optional, List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server import FastMCP


def get_fast_mcp_server(
    server_name: str | None, instructions: str | None = None
) -> FastMCP:
    """
    获取 FastMCP 服务器实例
    Args:
        server_name (Optional[str]): 服务器名称，如果为 None，则使用默认服务器名称
        instructions (Optional[str]): 服务器说明，如果为 None，则使用默认说明

    Returns:
        FastMCP: FastMCP 服务器实例
    """
    return FastMCP(server_name, instructions=instructions)


def get_fast_mcp_server_tools_by_langchain(
    server_name: str | None,
    tools: list[BaseTool] | None = None,
    instructions: str | None = None,
) -> FastMCP:
    """
    获取 FastMCP 服务器实例，并注册 LangChain 工具
    Args:
        server_name (Optional[str]): 服务器名称，如果为 None，则使用默认服务器名称
        tools (List[BaseTool]): 工具列表
        instructions (Optional[str]): 服务器说明，如果为 None，则使用默认说明

    Returns:
        FastMCP: FastMCP 服务器实例
    """
    fast_mcp_tools = list(map(lambda tool: to_fastmcp(tool), tools))
    return FastMCP(server_name, tools=fast_mcp_tools, instructions=instructions)


def run_fast_mcp_server(
    mcp_server: FastMCP,
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
    mount_path: str | None = None,
) -> None:
    """
    运行 FastMCP 服务器
    Args:
        mcp_server (FastMCP): FastMCP 服务器实例
        transport (Literal["stdio", "sse", "streamable-http"]): mcp启动方式，默认为 "stdio"
            stdio: 标准输入输出
            sse: 服务器发送事件
            streamable-http: 可流式传输的 HTTP
        mount_path (Optional[str]): 挂载路径，如果为 None，则使用默认挂载路径

    Returns:
        None
    """
    mcp_server.run(transport=transport, mount_path=mount_path)


__all__ = [
    "get_fast_mcp_server",
    "get_fast_mcp_server_tools_by_langchain",
    "run_fast_mcp_server",
]
