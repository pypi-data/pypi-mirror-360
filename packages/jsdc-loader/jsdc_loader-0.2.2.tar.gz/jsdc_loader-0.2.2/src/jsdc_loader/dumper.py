"""杂鱼♡～这是本喵的序列化工具喵～本喵可以把你的dataclass变成JSON喵～"""

import datetime
import json
import os
import tempfile
import uuid
from dataclasses import is_dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Union
from collections import defaultdict, deque
from enum import Flag, IntFlag

from .core.converter import convert_dataclass_to_dict
from .core.types import T
from .file_ops import ensure_directory_exists


# 杂鱼♡～本喵创建了一个自定义JSON编码器，这样就可以处理各种复杂类型喵～
class JSDCJSONEncoder(json.JSONEncoder):
    """杂鱼♡～这是本喵为你特制的JSON编码器喵～可以处理各种特殊类型哦～"""

    def default(self, obj: Any) -> Any:
        """杂鱼♡～本喵会把这些特殊类型转换成JSON兼容的格式喵～"""
        # 杂鱼♡～导入需要的类型喵～
        
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, frozenset):
            # 杂鱼♡～frozenset 需要特殊标记以便反序列化喵～
            return {
                "__type__": "frozenset",
                "__data__": list(obj)
            }
        elif isinstance(obj, deque):
            # 杂鱼♡～deque 需要保存 maxlen 信息喵～
            return {
                "__type__": "deque",
                "__data__": list(obj),
                "__maxlen__": obj.maxlen
            }
        elif isinstance(obj, defaultdict):
            # 杂鱼♡～defaultdict 需要保存 default_factory 信息喵～
            default_factory_name = None
            if obj.default_factory is not None:
                if obj.default_factory is list:
                    default_factory_name = "list"
                elif obj.default_factory is dict:
                    default_factory_name = "dict"
                elif obj.default_factory is set:
                    default_factory_name = "set"
                elif obj.default_factory is int:
                    default_factory_name = "int"
                else:
                    default_factory_name = str(obj.default_factory)
            
            return {
                "__type__": "defaultdict",
                "__data__": dict(obj),
                "__default_factory__": default_factory_name
            }
        elif isinstance(obj, (Flag, IntFlag)):
            # 杂鱼♡～Flag/IntFlag 使用数值序列化喵～
            return obj.value
        elif is_dataclass(obj):
            return convert_dataclass_to_dict(obj)
        # 杂鱼♡～其他类型就交给父类处理喵～
        return super().default(obj)


def jsdc_dumps(obj: T, indent: int = 4) -> str:
    """杂鱼♡～本喵帮你把dataclass实例序列化成JSON字符串喵～

    这个函数接收一个dataclass实例，并将其序列化为JSON字符串喵～
    JSON输出可以使用指定的缩进级别格式化喵～杂鱼是不是太懒了，连文件都不想写呢♡～

    Args:
        obj (T): 要序列化的dataclass实例喵～
        indent (int, optional): JSON输出中使用的缩进空格数喵～默认是4～看起来整齐一点～

    Returns:
        str: 序列化后的JSON字符串喵～杂鱼可以好好利用它哦～

    Raises:
        TypeError: 如果obj不是dataclass或BaseModel，杂鱼肯定传错参数了～
        ValueError: 如果序列化过程中出错，本喵会生气地抛出错误喵！～
    """
    if indent < 0:
        raise ValueError("Indent must be non-negative")

    try:
        if isinstance(obj, type):
            raise TypeError("obj must be an instance, not a class")

        if not is_dataclass(obj):
            raise TypeError("obj must be a dataclass instance")

        # 获取对象的类型提示
        obj_type = type(obj)

        # 杂鱼♡～本喵把类型信息也传递给转换函数，这样就能进行完整的类型验证了喵～
        data_dict = convert_dataclass_to_dict(
            obj, parent_key="root", parent_type=obj_type
        )
        return json.dumps(
            data_dict, ensure_ascii=False, indent=indent, cls=JSDCJSONEncoder
        )
    except TypeError as e:
        raise TypeError(f"Type validation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Serialization error: {str(e)}")


def jsdc_dump(
    obj: T, output_path: Union[str, Path], encoding: str = "utf-8", indent: int = 4
) -> None:
    """杂鱼♡～本喵帮你把dataclass实例序列化成JSON文件喵～

    这个函数接收一个dataclass实例，并将其序列化表示写入到指定文件中，
    格式为JSON喵～输出文件可以使用指定的字符编码，JSON输出可以
    使用指定的缩进级别格式化喵～杂鱼一定会感激本喵的帮助的吧♡～

    本喵会使用临时文件进行安全写入，防止在写入过程中出错导致文件损坏喵～

    Args:
        obj (T): 要序列化的dataclass实例喵～
        output_path (Union[str, Path]): 要保存JSON数据的输出文件路径喵～杂鱼现在可以用字符串或Path对象了♡～
        encoding (str, optional): 输出文件使用的字符编码喵～默认是'utf-8'～
        indent (int, optional): JSON输出中使用的缩进空格数喵～默认是4～看起来整齐一点～

    Raises:
        ValueError: 如果提供的对象不是dataclass或路径无效，本喵会生气地抛出错误喵！～
        TypeError: 如果obj不是dataclass或BaseModel，杂鱼肯定传错参数了～
        OSError: 如果遇到文件系统相关错误，杂鱼的硬盘可能有问题喵～
        UnicodeEncodeError: 如果编码失败，杂鱼选的编码有问题喵！～
    """
    # 杂鱼♡～本喵现在支持Path对象了喵～
    path = Path(output_path)

    if not path or not str(path):
        raise ValueError("Invalid output path")

    if indent < 0:
        raise ValueError("Indent must be non-negative")

    # 获取输出文件的绝对路径喵～
    abs_path = path.absolute()
    directory = abs_path.parent

    try:
        # 确保目录存在且可写喵～
        ensure_directory_exists(str(directory))

        if isinstance(obj, type):
            raise TypeError("obj must be an instance, not a class")

        if not is_dataclass(obj):
            raise TypeError("obj must be a dataclass instance")

        # 杂鱼♡～先序列化为字符串喵～
        json_str = jsdc_dumps(obj, indent)

        # 杂鱼♡～使用临时文件进行安全写入喵～
        # 在同一目录创建临时文件，确保重命名操作在同一文件系统内执行喵～
        temp_file = tempfile.NamedTemporaryFile(
            prefix=f".{abs_path.name}.",
            dir=str(directory),
            suffix=".tmp",
            delete=False,
            mode="w",
            encoding=encoding,
        )

        temp_path = temp_file.name
        try:
            # 杂鱼♡～写入临时文件喵～
            temp_file.write(json_str)
            # 必须先刷新缓冲区喵～
            temp_file.flush()
            # 确保文件内容已完全写入磁盘喵～然后再关闭文件～
            os.fsync(temp_file.fileno())
            temp_file.close()

            # 杂鱼♡～使用原子操作将临时文件重命名为目标文件喵～
            # 在Windows上，如果目标文件已存在，可能会失败，所以先尝试删除喵～
            if abs_path.exists():
                abs_path.unlink()

            # 杂鱼♡～安全地重命名文件喵～
            os.rename(temp_path, str(abs_path))
        except Exception as e:
            # 杂鱼♡～如果出错，清理临时文件喵～
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass  # 杂鱼♡～如果连临时文件都删不掉，本喵也无能为力了喵～
            raise e  # 杂鱼♡～重新抛出原始异常喵～

    except OSError as e:
        raise OSError(f"Failed to create directory or access file: {str(e)}")
    except (ValueError, TypeError) as e:
        # 杂鱼♡～让类型和值错误直接传播，这是期望的行为喵～
        raise e
    except Exception as e:
        raise ValueError(f"Serialization error: {str(e)}")
