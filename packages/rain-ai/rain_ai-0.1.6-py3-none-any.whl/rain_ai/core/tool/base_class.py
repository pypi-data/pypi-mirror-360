from abc import ABC, abstractmethod
from typing import Protocol, Any

from langchain_core.tools import BaseTool


class ToolProtocol(Protocol):
    """工具协议，定义了工具类的基本接口。"""

    _is_tool_class: bool

    def to_tool_list(self) -> list[BaseTool]:
        """返回所有被@tool_method装饰的方法的工具实例列表"""
        ...

    def to_json_schema_list(self) -> list[dict[str, Any]]:
        """返回所有工具方法的JSON Schema列表"""
        ...

    def invoke(
        self, method_name: str, args: dict[str, Any] | None = None, **kwargs
    ) -> Any:
        """
        通过名称调用工具方法

        支持两种调用方式:
        1. invoke("method_name", {"param1": "value1", "param2": "value2"})
        2. invoke("method_name", param1="value1", param2="value2")

        参数:
            method_name: 工具方法的名称
            args: 可选的参数字典
            **kwargs: 关键字参数

        返回:
            工具方法的执行结果

        抛出:
            ValueError: 如果找不到指定名称的工具方法
        """
        ...


class ToolDecoratorClass:
    """专门读取 @tool_class 装饰器装饰的类。作用是让 ide 能读取到装饰器添加的方法和未来扩展功能。"""

    def __init__(self, tool_class: ToolProtocol):
        self.__tool_class = tool_class

    def to_tool_list(self) -> list[BaseTool]:
        """返回所有被@tool_method装饰的方法的工具实例列表"""
        return self.__tool_class.to_tool_list()

    def to_json_schema_list(self) -> list[dict[str, Any]]:
        """返回所有工具方法的JSON Schema列表"""
        return self.__tool_class.to_json_schema_list()

    def invoke(
        self, method_name: str, args: dict[str, Any] | None = None, **kwargs
    ) -> Any:
        """
        通过名称调用工具方法

        支持两种调用方式:
        1. invoke("method_name", {"param1": "value1", "param2": "value2"})
        2. invoke("method_name", param1="value1", param2="value2")

        参数:
            method_name: 工具方法的名称
            args: 可选的参数字典
            **kwargs: 关键字参数

        返回:
            工具方法的执行结果

        抛出:
            ValueError: 如果找不到指定名称的工具方法
        """
        return self.__tool_class.invoke(method_name, args, **kwargs)


class ToolAbstractClass(ABC):
    """
    工具抽象类，实现此抽象类就效果和 @tool_class 装饰器一样。
    _create_tool_list 方法需要子类实现，返回一个 BaseTool 的列表，也就是 @tool_method 装饰器装饰的方法列表。
    """

    _is_tool_class: bool = True

    def __init__(self):
        self.__tool_methods: list[BaseTool] = self._create_tool_list()
        self.__tool_methods_map: dict[str, BaseTool] = {
            tool.json_schema["title"]: tool for tool in self.__tool_methods
        }

    @abstractmethod
    def _create_tool_list(self) -> list[BaseTool]:
        """创建工具列表，子类需要实现此方法。"""

    def to_tool_list(self) -> list[BaseTool]:
        """返回所有被@tool_method装饰的方法的工具实例列表"""
        return self.__tool_methods

    def to_json_schema_list(self) -> list[dict[str, Any]]:
        """返回所有工具方法的JSON Schema列表"""
        schemas = []
        for _tool in self.__tool_methods:
            # 确保工具有json_schema属性
            if hasattr(_tool, "json_schema"):
                schemas.append(_tool.json_schema)
            else:
                # 尝试从args_schema获取
                if hasattr(_tool, "args_schema") and _tool.args_schema is not None:
                    schemas.append(_tool.args_schema.model_json_schema())
                else:
                    # 没有参数模式的情况
                    schemas.append({"type": "object", "properties": {}})
        return schemas

    def invoke(
        self, method_name: str, args: dict[str, Any] | None = None, **kwargs
    ) -> Any:
        """
        通过名称调用工具方法

        支持两种调用方式:
        1. invoke("method_name", {"param1": "value1", "param2": "value2"})
        2. invoke("method_name", param1="value1", param2="value2")

        参数:
            method_name: 工具方法的名称
            args: 可选的参数字典
            **kwargs: 关键字参数

        返回:
            工具方法的执行结果

        抛出:
            ValueError: 如果找不到指定名称的工具方法
        """
        if method_name not in self.__tool_methods_map:
            # 构建可用工具列表用于错误信息
            available_tools = list(self.__tool_methods_map.keys())
            raise ValueError(
                f"找不到名为 '{method_name}' 的工具方法。可用的工具: {available_tools}"
            )

        # 合并参数
        params = {}
        if args is not None:
            params.update(args)
        if kwargs:
            params.update(kwargs)

        # 获取工具并调用
        __tool = self.__tool_methods_map[method_name]
        return __tool.invoke(params)


__all__ = ["ToolAbstractClass", "ToolDecoratorClass", "ToolProtocol"]
