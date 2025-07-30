import json
from typing import Literal

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


def get_stdio_mcp_server_config(
    server_name: str, command: str, args: list[str]
) -> dict:
    """
    返回一个标准输入输出的MCP服务器配置字典

    Args:
        server_name (str): 服务器名称
        command (str): 启动服务器的命令
        args (List[str]): 启动服务器的参数列表

    Returns:
        Dict: 包含服务器配置的字典

    """

    return {
        "server_name": server_name,
        "command": command,
        "args": args,
        "transport": "stdio",
    }


def get_http_mcp_server_config(
    server_name: str,
    url: str,
    transport: Literal["sse", "streamable-http"] = "sse",
    headers: dict | None = None,
) -> dict:
    """
    返回一个HTTP的MCP服务器配置字典

    Args:
        server_name (str): 服务器名称
        url (str): 服务器的URL地址
        transport (Literal["sse", "streamable-http"]): 传输方式，默认为"sse"
            sse: 服务器发送事件
            streamable-http: 可流式传输的 HTTP
        headers (Optional[Dict]): HTTP头信息

    Returns:
        Dict: 包含服务器配置的字典

    """

    return {
        "server_name": server_name,
        "url": url,
        "transport": transport,
        "headers": headers,
    }


def get_mcp_server_client(server_config_list: list[dict]) -> MultiServerMCPClient:
    """
    根据服务器配置列表创建一个MCP客户端实例

    Args:
        server_config_list (List[Dict]): 服务器配置字典列表

    Returns:
        MultiServerMCPClient: MCP客户端实例

    """

    server_config = {}

    for config in server_config_list:
        if config["transport"] == "stdio":
            server_config[config["server_name"]] = {
                "command": config["command"],
                "args": config["args"],
                "transport": config["transport"],
            }
        else:
            server_config[config["server_name"]] = {
                "url": config["url"],
                "transport": config["transport"],
                "headers": config.get("headers", {}),
            }

    return MultiServerMCPClient(server_config)


def get_mcp_server_client_mcp_json(server_config_dict: str) -> MultiServerMCPClient:
    """
    根据MCP JSON格式的服务器配置字符串创建一个MCP客户端实例

    Args:
        server_config_dict (str): MCP服务器配置的JSON字符串

    Returns:
        MultiServerMCPClient: MCP客户端实例

    """

    return MultiServerMCPClient(json.loads(server_config_dict))


async def get_mcp_server_tools(client: MultiServerMCPClient) -> list[BaseTool]:
    """
    获取MCP服务器工具列表，使用这个方法获取的工具在调用 大模型的时候 请使用异步 await

    Args:
        client (MultiServerMCPClient): MCP客户端实例

    """

    return await client.get_tools()


def get_mcp_tool_json_schema(tool: BaseTool) -> dict:
    """
    获取MCP工具的JSON Schema

    Args:
        tool (BaseTool): MCP工具实例

    Returns:
        Dict: 工具的JSON Schema字典

    """

    json_schema = {
        "description": tool.description,
        "properties": tool.args_schema["properties"],
        "required": tool.args_schema["required"]
        if "required" in tool.args_schema
        else [],
        "type": tool.args_schema["type"],
        "title": tool.name,
    }

    return json_schema


__all__ = [
    "get_stdio_mcp_server_config",
    "get_http_mcp_server_config",
    "get_mcp_server_client",
    "get_mcp_server_client_mcp_json",
    "get_mcp_server_tools",
    "get_mcp_tool_json_schema",
]
