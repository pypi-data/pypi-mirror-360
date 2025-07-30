import inspect
from functools import wraps
from typing import Callable, Literal, Any

from langchain_core.runnables import Runnable
from langchain_core.tools import tool, BaseTool, ArgsSchema


def _add_json_schema(tool_instance) -> BaseTool:
    """为工具实例添加json_schema属性"""

    @property
    def json_schema(self):
        if hasattr(self, "args_schema") and self.args_schema is not None:
            return self.args_schema.model_json_schema()
        return {"title": "EmptyInput", "type": "object", "properties": {}}

    tool_instance.__class__.json_schema = json_schema
    return tool_instance


def tool_class(cls: type) -> type:
    """
    类装饰器，用于增强类以便更好地管理工具方法

    装饰后的类将具有：
    - to_tool_list(): 返回所有被@tool_method装饰的方法的工具实例列表
    - to_json_schema_list(): 返回所有工具方法的JSON Schema列表
    - invoke(method_name, args=None, **kwargs): 通过名称调用工具方法

    用法:
    @tool_class
    class MyTools:
        @tool_method
        def method1(self):
            ...
    """
    # 保存原始的__init__方法
    original_init = cls.__init__

    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        # 调用原始的__init__
        original_init(self, *args, **kwargs)

        # 存储工具方法引用，用于后续访问
        self._tool_methods = []
        self._tool_methods_map = {}  # 名称到工具的映射

        # 查找所有带有@tool_method装饰的方法
        for name, method in inspect.getmembers(self):
            # 检查方法是否是工具实例
            if isinstance(method, BaseTool):
                self._tool_methods.append(method)
                # 保存工具名称到工具的映射
                tool_name = getattr(method, "name", name)
                self._tool_methods_map[tool_name] = method

    # 替换__init__方法
    cls.__init__ = new_init

    def to_tool_list(self) -> list[BaseTool]:
        """返回所有被@tool_method装饰的方法的工具实例列表"""
        return self._tool_methods

    def to_json_schema_list(self) -> list[dict[str, Any]]:
        """返回所有工具方法的JSON Schema列表"""
        schemas = []
        for _tool in self._tool_methods:
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
        if method_name not in self._tool_methods_map:
            # 构建可用工具列表用于错误信息
            available_tools = list(self._tool_methods_map.keys())
            raise ValueError(
                f"找不到名为 '{method_name}' 的工具方法可用的工具: {available_tools}"
            )

        # 合并参数
        params = {}
        if args is not None:
            params.update(args)
        if kwargs:
            params.update(kwargs)

        # 获取工具并调用
        _tool = self._tool_methods_map[method_name]
        return _tool.invoke(params)

    # 添加新方法到类
    cls.to_tool_list = to_tool_list
    cls.to_json_schema_list = to_json_schema_list
    cls.invoke = invoke
    # 标记为工具类
    cls._is_tool_class = True

    return cls


def tool_method(
    name_or_callable: str,
    description: str | None = None,
    return_direct: bool = False,
    infer_schema: bool = True,
    args_schema: ArgsSchema | None = None,
    response_format: Literal["content", "content_and_artifact"] = "content",
    parse_docstring: bool = False,
    error_on_invalid_docstring: bool = True,
) -> BaseTool | Callable[[Callable | Runnable], BaseTool]:
    """
    对langchain_core.tools.tool的增强封装，在此基础上添加自定义属性

    参数标记请使用：xx: Annotated[str, "描述信息"] 的形式

    Args:
        name_or_callable: 工具的名称或要装饰的函数
        description: 工具的描述
        return_direct: 是否直接返回输出或包装它
        infer_schema: 是否从函数签名推断模式
        args_schema: 可选的ArgsSchema实例，用于定义参数模式，进行参数验证
        response_format: 响应的格式
        parse_docstring: 是否解析文档字符串
        error_on_invalid_docstring: 文档字符串无效时是否引发错误

    Returns:
        BaseTool实例或返回BaseTool的装饰器函数，增加了json_schema属性
    """

    # 处理 @tool_method 形式调用
    if callable(name_or_callable):
        return _add_json_schema(tool(name_or_callable))

    # 处理 @tool_method(参数) 形式调用
    def decorator(func):
        return _add_json_schema(
            tool(
                name_or_callable=name_or_callable,
                description=description,
                return_direct=return_direct,
                infer_schema=infer_schema,
                args_schema=args_schema,
                response_format=response_format,
                parse_docstring=parse_docstring,
                error_on_invalid_docstring=error_on_invalid_docstring,
            )(func)
        )

    return decorator


__all__ = ["tool_class", "tool_method"]
