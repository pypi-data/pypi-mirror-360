import importlib
import sys
from typing import Any, Callable

import cloudpickle


def serialize_code_file(file_path: str, output_path: str) -> None:
    """
    将Python代码文件序列化为二进制格式并保存到指定路径。

    Args:
        file_path (str): 要序列化的Python文件的路径(.py文件）
        output_path (str): 序列化数据的保存路径(通常为.pkl文件)

    Returns:
        None
    """
    # 动态导入模块
    module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # 序列化整个模块
    with open(output_path, "wb") as file:
        cloudpickle.dump(module, file)


def deserialize_code_file(pickle_path: str) -> Any:
    """
    从二进制文件中反序列化Python模块。

    Args:
        pickle_path (str): 二进制文件的路径，通常是.pkl文件

    Returns:
        Any: 反序列化后的Python模块对象
    """
    with open(pickle_path, "rb") as file:
        module = cloudpickle.load(file)

    return module


def serialize_function(func: Callable, output_path: str) -> None:
    """
    将Python函数序列化为二进制格式并保存到指定路径。

    Args:
        func (Callable): 要序列化的函数对象，可以是普通函数、方法、lambda表达式或闭包
        output_path (str): 序列化数据的保存路径

    Returns:
        None
    """
    with open(output_path, "wb") as file:
        cloudpickle.dump(func, file)


def deserialize_function(func_path: str) -> Any:
    """
    从二进制文件中反序列化Python函数。

    Args:
        func_path (str): 二进制文件的路径，通常是.pkl文件

    Returns:
        Any: 反序列化后的Python模块对象
    """
    with open(func_path, "rb") as file:
        func = cloudpickle.load(file)
    return func


def serialize_instance(instance: Any, output_path: str) -> None:
    """
    将Python对象实例序列化为二进制格式并保存到指定路径。

    Args:
        instance (Any): 要序列化的对象实例，可以是任何Python对象
        output_path (str): 序列化数据的保存路径

    Returns:
        None
    """
    with open(output_path, "wb") as file:
        cloudpickle.dump(instance, file)


# 反序列化实例
def deserialize_instance(instance_path: str) -> Any:
    """
    从二进制文件中反序列化Python实例。

    Args:
        instance_path (str): 二进制文件的路径，通常是.pkl文件

    Returns:
        Any: 反序列化后的Python模块对象
    """
    with open(instance_path, "rb") as file:
        return cloudpickle.load(file)


__all__ = [
    "serialize_code_file",
    "deserialize_code_file",
    "serialize_function",
    "deserialize_function",
    "serialize_instance",
    "deserialize_instance",
]
