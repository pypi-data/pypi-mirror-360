"""杂鱼♡～这是本喵为你写的文件操作辅助函数喵～才不是因为担心杂鱼不会处理文件呢～"""

import datetime
import json
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Union


def ensure_directory_exists(directory_path: Union[str, Path]) -> None:
    """
    杂鱼♡～本喵帮你确保目录存在喵～如果不存在就创建它～

    :param directory_path: 要确保存在的目录路径喵～杂鱼现在可以用字符串或Path对象了♡～
    :raises: OSError 如果创建目录失败喵～杂鱼的权限是不是有问题？～
    """
    # 杂鱼♡～本喵现在支持Path对象了喵～
    path = Path(directory_path)

    if path and not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory: {path}, error: {str(e)}")


# 杂鱼♡～本喵创建了一个支持复杂类型的JSON编码器喵～
class ComplexJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，支持datetime、UUID、Decimal等类型喵～"""

    def default(self, obj):
        """处理非标准类型的JSON序列化喵～"""
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
        return super().default(obj)


def save_json_file(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    encoding: str = "utf-8",
    indent: int = 4,
) -> None:
    """
    杂鱼♡～本喵帮你把数据保存为JSON文件喵～

    :param file_path: 要保存的文件路径喵～杂鱼现在可以用字符串或Path对象了♡～
    :param data: 要保存的数据（字典形式）喵～
    :param encoding: 文件编码，默认utf-8喵～杂鱼应该不需要改这个～
    :param indent: JSON缩进空格数，默认4喵～看起来整齐一点～
    :raises: OSError 如果写入文件失败喵～
    :raises: TypeError 如果数据无法序列化成JSON喵～杂鱼提供的数据有问题！～
    """
    # 杂鱼♡～本喵现在支持Path对象了喵～
    path = Path(file_path)

    try:
        with path.open("w", encoding=encoding) as f:
            json.dump(
                data, f, ensure_ascii=False, indent=indent, cls=ComplexJSONEncoder
            )
    except OSError as e:
        raise OSError(f"Failed to write to file: {path}, error: {str(e)}")
    except TypeError as e:
        raise TypeError(f"Failed to serialize data to JSON: {str(e)}")
    except UnicodeEncodeError as e:
        raise UnicodeEncodeError(
            f"Failed to encode data with {encoding} encoding: {str(e)}",
            e.object,
            e.start,
            e.end,
            e.reason,
        )
    except Exception as e:
        raise ValueError(f"JSON serialization error: {str(e)}")


def check_file_size(file_path: Union[str, Path], max_size: int) -> None:
    """
    杂鱼♡～本喵帮你检查文件大小是否超过限制喵～

    如果文件大小超过max_size字节，本喵会生气地抛出ValueError喵！～
    如果文件不存在，本喵会抛出FileNotFoundError喵～杂鱼一定是路径搞错了～

    :param file_path: 要检查的文件路径喵～杂鱼现在可以用字符串或Path对象了♡～
    :param max_size: 允许的最大文件大小（字节）喵～
    :raises: ValueError 如果文件太大喵～
    :raises: FileNotFoundError 如果文件不存在喵～
    :raises: PermissionError 如果没有权限访问文件喵～杂鱼是不是忘记提升权限了？～
    """
    # 杂鱼♡～本喵现在支持Path对象了喵～
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    try:
        file_size = path.stat().st_size
        if file_size > max_size:
            raise ValueError(
                f"File size exceeds limit: {file_size} bytes, maximum allowed: {max_size} bytes"
            )
    except PermissionError:
        raise PermissionError(f"No permission to check file size: {path}")
