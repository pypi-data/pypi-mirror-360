from typing import List, Union

from rain_ai.core.serialize.cloudpickle_serialize import deserialize_instance
from rain_ai.core.tool.base_class import ToolAbstractClass


def load_str_name_tool(
    code_str: str, tool_class_name: str = "tool_class"
) -> ToolAbstractClass:
    """
    该函数执行给定的代码字符串，然后通过指定的变量名从执行环境中提取 ToolAbstractClass 实例
    不手动设置 tool_class_name 参数时，默认查找名为 "tool_class" 的实例

    Args:
        code_str (str): 包含工具类定义和实例化代码的字符串。代码应该导入所有必要的依赖，
                        定义工具类（ToolAbstractClass 的子类），并创建这些类的实例
        tool_class_name (str): 要获取的工具类实例在代码中的变量名。默认为 "tool_class"

    Returns:
        ToolAbstractClass: 从代码字符串中通过变量名获取的 ToolAbstractClass 实例

    Example:
        code_str 示例:

        from core.tool.base_class import ToolAbstractClass
        from core.tool.decorator import tool_method
        import time

        class WeatherTool(ToolAbstractClass):
            def _create_tool_list(self):
                @tool_method
                def get_weather(city: str) -> str:
                    return city + '晴天'
                return [get_weather]

        weather_tool = WeatherTool()

        tool = load_str_name_tool(code, "weather_tool")
        # 返回名为 weather_tool 的 WeatherTool 实例

    Note:
        - 该函数执行任意代码，在处理不可信来源的代码时应谨慎使用
        - 确保代码字符串中包含所有必要的导入语句
        - 如果变量名不存在，函数将返回 None
    """
    # 创建空命名空间
    namespace = {}

    # 执行代码字符串
    exec(code_str, namespace)

    return namespace.get(tool_class_name)


def load_str_tool_list(code_str: str) -> List[ToolAbstractClass]:
    """
    从包含工具类定义的代码字符串中加载并返回 ToolAbstractClass 的实例列表。

    该函数执行给定的代码字符串，然后从执行环境中提取所有 ToolAbstractClass 的实例。
    这对于动态加载工具类定义非常有用，例如从配置或外部源获取工具定义。

    Args:
        code_str (str): 包含工具类定义和实例化代码的字符串。代码应该导入所有必要的依赖，
                 定义工具类（ToolAbstractClass 的子类），并创建这些类的实例。

    Returns:
        List[ToolAbstractClass]: 从代码字符串中获取的 ToolAbstractClass 实例列表。
        如果代码中没有创建任何实例，则返回空列表。

    Example:
        code_str 示例:

        from core.tool.base_class import ToolAbstractClass
        from core.tool.decorator import tool_method
        import time

        class WeatherTool(ToolAbstractClass):
            def _create_tool_list(self):
                @tool_method
                def get_weather(city: str) -> str:
                    return city + '晴天'
                return [get_weather]

        weather_tool = WeatherTool()

    Note:
        - 该函数执行任意代码，在处理不可信来源的代码时应谨慎使用
        - 确保代码字符串中包含所有必要的导入语句
        - 如果代码中没有创建任何 ToolAbstractClass 的实例，函数将返回空列表
    """
    # 创建空命名空间
    namespace = {}

    # 执行代码字符串
    exec(code_str, namespace)

    # 查找所有 ToolAbstractClass 的实例
    tool_instances = []
    for name, value in namespace.items():
        if isinstance(value, ToolAbstractClass):
            tool_instances.append({"name": name, "instance": value})

    return tool_instances


def load_pkl_tool(pkl_path: str) -> Union[ToolAbstractClass, None]:
    """
    从指定的 PKL 路径加载工具类定义，并返回 ToolAbstractClass 的实例。

    该函数读取 PKL 路径下的代码文件，执行其中的代码，并返回 ToolAbstractClass 的实例。
    这对于动态加载工具类定义非常有用，例如从配置或外部源获取工具定义。

    Args:
        pkl_path (str): 包含工具类定义的 PKI 路径。

    Returns:
        ToolAbstractClass: 从 PKI 路径中获取的 ToolAbstractClass 实例。
                           如果路径无效或没有创建实例，则返回 None。
    """
    return deserialize_instance(pkl_path)


__all__ = ["load_str_name_tool", "load_str_tool_list", "load_pkl_tool"]
