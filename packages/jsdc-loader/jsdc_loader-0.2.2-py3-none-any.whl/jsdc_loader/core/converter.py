"""Conversion utilities for JSDC Loader."""

import datetime
import uuid
from dataclasses import is_dataclass
from decimal import Decimal
from enum import Enum, Flag, IntFlag
from typing import Any, Type, Union, get_args, get_origin
from collections import defaultdict, deque

from .types import T, _DATACLASS_CACHE, _SPECIAL_TYPE_CACHE, _GET_ORIGIN_CACHE, _GET_ARGS_CACHE, _TYPE_CHECK_CACHE
from .validator import get_cached_type_hints, validate_type


# 杂鱼♡～本喵添加了缓存版本的 get_origin 和 get_args 喵～这样就不用重复计算了～
def cached_get_origin(tp: Any) -> Any:
    """杂鱼♡～本喵的缓存版本 get_origin 喵～"""
    if tp not in _GET_ORIGIN_CACHE:
        _GET_ORIGIN_CACHE[tp] = get_origin(tp)
    return _GET_ORIGIN_CACHE[tp]


def cached_get_args(tp: Any) -> tuple:
    """杂鱼♡～本喵的缓存版本 get_args 喵～"""
    if tp not in _GET_ARGS_CACHE:
        _GET_ARGS_CACHE[tp] = get_args(tp)
    return _GET_ARGS_CACHE[tp]


# 杂鱼♡～本喵添加了一个快速类型检查缓存喵～
def cached_isinstance(obj: Any, cls: Type) -> bool:
    """杂鱼♡～本喵的缓存版本 isinstance 检查喵～"""
    obj_type = type(obj)
    cache_key = (obj_type, cls)
    
    if cache_key not in _TYPE_CHECK_CACHE:
        _TYPE_CHECK_CACHE[cache_key] = isinstance(obj, cls)
    return _TYPE_CHECK_CACHE[cache_key]


def convert_enum(key: str, value: Any, enum_type: Type[Enum]) -> Enum:
    """Convert a string value to an Enum member."""
    try:        
        # 杂鱼♡～处理 Flag/IntFlag 枚举喵～
        if issubclass(enum_type, (Flag, IntFlag)):
            # 杂鱼♡～Flag/IntFlag 使用数值进行反序列化喵～
            if isinstance(value, int):
                return enum_type(value)
            else:
                raise ValueError(f"Flag/IntFlag type {enum_type} needs int value, got {type(value)}")
        else:
            # 杂鱼♡～普通枚举使用名称进行反序列化喵～
            return enum_type[value]
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid Enum value for key {key}: {value}")


def convert_union_type(key: str, value: Any, union_type: Any) -> Any:
    """Convert a value to one of the Union types."""
    args = cached_get_args(union_type)

    # 杂鱼♡～处理None值喵～
    if value is None and type(None) in args:
        return None

    # 杂鱼♡～首先尝试精确类型匹配，这样可以避免不必要的类型转换喵～
    for arg_type in args:
        if arg_type is type(None):
            continue

        # 杂鱼♡～检查是否是精确的类型匹配喵～
        if _is_exact_type_match(value, arg_type):
            try:
                return convert_value(key, value, arg_type)
            except (ValueError, TypeError):
                continue

    # 杂鱼♡～如果没有精确匹配，再尝试类型转换喵～
    for arg_type in args:
        if arg_type is type(None):
            continue

        # 杂鱼♡～跳过已经尝试过的精确匹配喵～
        if _is_exact_type_match(value, arg_type):
            continue

        try:
            return convert_value(key, value, arg_type)
        except (ValueError, TypeError):
            continue

    # 如果所有转换都失败，则抛出错误喵～
    raise TypeError(f"Cannot convert value for key {key} to {union_type}")


def _is_exact_type_match(value: Any, expected_type: Any) -> bool:
    """杂鱼♡～检查值是否与期望类型精确匹配喵～"""
    # 杂鱼♡～处理基本类型喵～
    if expected_type in (int, float, str, bool):
        return type(value) is expected_type

    # 杂鱼♡～处理容器类型喵～
    origin = cached_get_origin(expected_type)
    if origin is list:
        return isinstance(value, list)
    elif origin is dict:
        return isinstance(value, dict)
    elif origin is set:
        return isinstance(value, set)
    elif origin is frozenset:
        return isinstance(value, frozenset)
    elif origin is tuple:
        return isinstance(value, tuple)
    elif expected_type is list:
        return isinstance(value, list)
    elif expected_type is dict:
        return isinstance(value, dict)
    elif expected_type is set:
        return isinstance(value, set)
    elif expected_type is frozenset:
        return isinstance(value, frozenset)
    elif expected_type is tuple:
        return isinstance(value, tuple)

    # 杂鱼♡～处理dataclass类型喵～
    if is_dataclass(expected_type):
        return isinstance(value, expected_type)

    # 杂鱼♡～处理Enum类型喵～
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return isinstance(value, expected_type)

    # 杂鱼♡～其他情况返回False，让转换逻辑处理喵～
    return False


def convert_simple_type(key: str, value: Any, e_type: Any) -> Any:
    """Convert a value to a simple type."""
    # 杂鱼♡～处理特殊类型喵～
    if e_type is Any:
        return value
    elif isinstance(e_type, type) and issubclass(e_type, Enum):        
        # 杂鱼♡～处理 Flag/IntFlag 枚举喵～
        if issubclass(e_type, (Flag, IntFlag)):
            # 杂鱼♡～Flag/IntFlag 使用数值进行反序列化喵～
            if isinstance(value, int):
                return e_type(value)
            else:
                raise ValueError(f"Flag/IntFlag type {e_type} needs int value, got {type(value)}")
        else:
            # 杂鱼♡～普通枚举使用名称进行反序列化喵～
            return e_type[value]
    elif e_type == dict or cached_get_origin(e_type) == dict:
        # Handle dict type properly
        return value
    elif e_type == list or cached_get_origin(e_type) == list:
        # Handle list type properly
        return value
    # 杂鱼♡～优先使用映射表处理常见类型转换喵～
    else:
        # 杂鱼♡～尝试使用反序列化映射表喵～
        deserializer = _TYPE_DESERIALIZERS.get(e_type)
        if deserializer is not None:
            result = deserializer(value)
            if result is not None:
                return result
        
        # 杂鱼♡～处理特殊的timedelta情况喵～
        if e_type == datetime.timedelta:
            if isinstance(value, (int, float)):
                return datetime.timedelta(seconds=value)
            elif isinstance(value, dict):
                return datetime.timedelta(**value)
        elif e_type == Decimal and isinstance(value, (str, int, float)):
            return Decimal(str(value))
        
        # 杂鱼♡～对于基本类型，本喵需要先验证类型匹配喵～
        if e_type in (int, float, str, bool):
            if not isinstance(value, e_type):
                raise TypeError(
                    f"Key {key} has invalid type: expected {e_type}, got {type(value)}"
                )
            return value
        
        try:
            return e_type(value)
        except TypeError:
            # If it's a typing.Dict or typing.List, just return the value
            if str(e_type).startswith("typing."):
                return value
            raise


def convert_dict_type(key: str, value: dict, e_type: Any) -> dict:
    """Convert a dictionary based on its type annotation."""
    # 杂鱼♡～首先检查是否为序列化的defaultdict数据喵～
    if isinstance(value, dict) and value.get("__type__") == "defaultdict":
        # 杂鱼♡～处理序列化的defaultdict数据，但返回普通dict（因为目标类型是Dict）喵～
        data = value["__data__"]
        factory_name = value.get("__default_factory__")
        
        # 杂鱼♡～重建默认工厂喵～
        if factory_name == "list":
            factory = list
        elif factory_name == "dict":
            factory = dict
        elif factory_name == "set":
            factory = set
        elif factory_name == "int":
            factory = int
        else:
            factory = None
        
        # 杂鱼♡～获取键值类型喵～
        key_type, val_type = cached_get_args(e_type) if cached_get_args(e_type) else (str, Any)
        
        # 杂鱼♡～转换为普通字典（因为目标类型是Dict不是defaultdict）喵～
        result = {}
        for str_key, value_data in data.items():
            # 杂鱼♡～转换键类型喵～
            if key_type == str:
                converted_key = str_key
            elif key_type == int:
                converted_key = int(str_key)
            elif key_type == float:
                converted_key = float(str_key)
            elif key_type == bool:
                converted_key = str_key.lower() in ("true", "1")
            else:
                converted_key = str_key
            
            # 杂鱼♡～转换值类型喵～
            converted_value = convert_value(f"{key}[{str_key}]", value_data, val_type)
            result[converted_key] = converted_value
        
        return result
    
    if cached_get_origin(e_type) is dict:
        key_type, val_type = cached_get_args(e_type)

        # 杂鱼♡～本喵扩展支持更多键类型了喵～
        # 支持字符串、整数、浮点数、UUID、Literal等基本类型作为键
        
        # 杂鱼♡～检查是否为 Literal 类型喵～
        is_literal_key = False
        if hasattr(key_type, '__origin__'):
            # 杂鱼♡～对于 Python 3.8+ 的 Literal 类型喵～
            if str(key_type).startswith('typing.Literal'):
                is_literal_key = True
        elif str(key_type).startswith('typing_extensions.Literal'):
            # 杂鱼♡～对于较老版本的 typing_extensions 喵～
            is_literal_key = True
        
        supported_key_types = (str, int, float, bool, uuid.UUID)
        
        # 杂鱼♡～检查是否为 Enum/Flag 类型键喵～
        is_enum_key = False
        if isinstance(key_type, type) and issubclass(key_type, Enum):
            is_enum_key = True
        
        if not is_literal_key and not is_enum_key and key_type not in supported_key_types:
            raise ValueError(
                f"Dictionary key type {key_type} is not supported. Supported types: {supported_key_types}, Literal and Enum types"
            )

        # 杂鱼♡～如果键类型不是字符串，需要转换JSON中的字符串键为目标类型喵～
        converted_dict = {}
        for k, v in value.items():
            # 杂鱼♡～JSON中的键总是字符串，需要转换为目标键类型喵～
            if is_literal_key:
                # 杂鱼♡～Literal 类型的键保持为字符串喵～
                converted_key = k
            elif is_enum_key:
                # 杂鱼♡～Enum/Flag 类型的键需要反序列化喵～
                try:
                    if issubclass(key_type, (Flag, IntFlag)):
                        # 杂鱼♡～Flag/IntFlag 使用数值喵～
                        converted_key = key_type(int(k))
                    else:
                        # 杂鱼♡～普通枚举使用名称喵～
                        converted_key = key_type[k]
                except (ValueError, KeyError):
                    raise ValueError(f"Cannot convert key '{k}' to {key_type}")
            elif key_type == str:
                converted_key = k
            elif key_type == int:
                try:
                    converted_key = int(k)
                except ValueError:
                    raise ValueError(f"Cannot convert key '{k}' to int")
            elif key_type == float:
                try:
                    converted_key = float(k)
                except ValueError:
                    raise ValueError(f"Cannot convert key '{k}' to float")
            elif key_type == bool:
                if k.lower() in ("true", "1"):
                    converted_key = True
                elif k.lower() in ("false", "0"):
                    converted_key = False
                else:
                    raise ValueError(f"Cannot convert key '{k}' to bool")
            elif key_type == uuid.UUID:
                try:
                    converted_key = uuid.UUID(k)
                except ValueError:
                    raise ValueError(f"Cannot convert key '{k}' to UUID")
            else:
                converted_key = k  # 杂鱼♡～其他情况保持原样喵～

            # 杂鱼♡～转换值喵～
            if is_dataclass(val_type) or cached_get_origin(val_type) is Union:
                converted_dict[converted_key] = convert_value(f"{key}.{k}", v, val_type)
            else:
                converted_dict[converted_key] = v

        return converted_dict

    # Default case, just return the dict
    return value


def convert_tuple_type(key: str, value: list, e_type: Any) -> tuple:
    """杂鱼♡～本喵帮你把列表转换成元组喵～"""
    if cached_get_origin(e_type) is tuple:
        args = cached_get_args(e_type)
        if len(args) == 2 and args[1] is Ellipsis:  # Tuple[X, ...]
            element_type = args[0]
            return tuple(
                convert_value(f"{key}[{i}]", item, element_type)
                for i, item in enumerate(value)
            )
        elif args:  # Tuple[X, Y, Z]
            if len(value) != len(args):
                raise ValueError(
                    f"Tuple {key} length mismatch. Expected {len(args)}, got {len(value)}"
                )
            return tuple(
                convert_value(f"{key}[{i}]", item, arg_type)
                for i, (item, arg_type) in enumerate(zip(value, args))
            )

    # 如果没有参数类型或者其他情况，直接转换为元组喵～
    return tuple(value)


def convert_value(key: str, value: Any, e_type: Any) -> Any:
    """Convert a value to the expected type."""
    # 杂鱼♡～处理None值和Any类型喵～早期返回可以提高性能～
    if e_type is Any:
        return value
    
    if value is None:
        origin = cached_get_origin(e_type)
        if origin is Union and type(None) in cached_get_args(e_type):
            return None
        # 如果不是Union类型但值是None，让它继续处理以抛出适当的错误
    
    # 杂鱼♡～先检查常见的简单类型，提早返回喵～
    value_type = type(value)
    if e_type is value_type or (e_type in (int, float, str, bool) and value_type is e_type):
        return value

    # 杂鱼♡～缓存origin和args避免重复计算喵～
    origin = cached_get_origin(e_type)
    args = cached_get_args(e_type) if origin else None

    # 杂鱼♡～处理容器类型喵～优化顺序以处理最常见的类型～
    if origin is list or e_type == list:
        if args and is_dataclass(args[0]):
            return [
                convert_dict_to_dataclass(item, args[0])
                for item in value
            ]
        elif args:
            return [
                convert_value(f"{key}[{i}]", item, args[0])
                for i, item in enumerate(value)
            ]
        return value
    elif origin is dict or e_type == dict:
        return convert_dict_type(key, value, e_type)
    elif origin is set or e_type is set:
        if isinstance(value, list):
            if args:
                element_type = args[0]
                return {convert_value(f"{key}[*]", item, element_type) for item in value}
            else:
                return set(value)
        return value
    elif origin is frozenset or e_type is frozenset:
        # 杂鱼♡～处理 frozenset 类型喵～
        if isinstance(value, dict) and value.get("__type__") == "frozenset":
            # 杂鱼♡～从序列化的字典恢复 frozenset 喵～
            items_data = value["__data__"]
            if args:
                element_type = args[0]
                return frozenset(convert_value(f"{key}[*]", item, element_type) for item in items_data)
            else:
                return frozenset(items_data)
        elif isinstance(value, list):
            if args:
                element_type = args[0]
                return frozenset(convert_value(f"{key}[*]", item, element_type) for item in value)
            else:
                return frozenset(value)
        return value
    elif origin is tuple or e_type is tuple:
        if isinstance(value, dict) and value.get("__type__") == "tuple":
            # 杂鱼♡～处理从JSON反序列化的特殊tuple格式喵～
            tuple_data = value["__data__"]
            return convert_tuple_type(key, tuple_data, e_type)
        elif isinstance(value, list):
            return convert_tuple_type(key, value, e_type)
        return value
    elif origin is Union:
        return convert_union_type(key, value, e_type)
    elif isinstance(e_type, type) and issubclass(e_type, Enum):
        return convert_enum(key, value, e_type)
    elif is_dataclass(e_type):
        return convert_dict_to_dataclass(value, e_type)
    else:
        # 杂鱼♡～处理其他复杂类型喵～
        # 杂鱼♡～处理 deque 类型喵～
        if hasattr(e_type, '__origin__') and e_type.__origin__ is deque:
            if isinstance(value, dict) and value.get("__type__") == "deque":
                # 杂鱼♡～从序列化的字典恢复 deque 喵～
                items_data = value["__data__"]
                maxlen = value.get("__maxlen__")
                args = cached_get_args(e_type)
                if args:
                    element_type = args[0]
                    converted_items = [convert_value(f"{key}[{i}]", item, element_type) for i, item in enumerate(items_data)]
                else:
                    converted_items = items_data
                return deque(converted_items, maxlen=maxlen)
            elif isinstance(value, list):
                args = cached_get_args(e_type)
                if args:
                    element_type = args[0]
                    converted_items = [convert_value(f"{key}[{i}]", item, element_type) for i, item in enumerate(value)]
                else:
                    converted_items = value
                return deque(converted_items)
            return value
        elif e_type is deque:
            if isinstance(value, dict) and value.get("__type__") == "deque":
                items_data = value["__data__"]
                maxlen = value.get("__maxlen__")
                return deque(items_data, maxlen=maxlen)
            elif isinstance(value, list):
                return deque(value)
            return value
        
        # 杂鱼♡～处理 defaultdict 类型喵～
        elif hasattr(e_type, '__origin__') and e_type.__origin__ is defaultdict:
            if isinstance(value, dict) and value.get("__type__") == "defaultdict":
                # 杂鱼♡～从序列化的字典恢复 defaultdict 喵～
                data = value["__data__"]
                factory_name = value.get("__default_factory__")
                
                # 杂鱼♡～重建默认工厂喵～
                if factory_name == "list":
                    factory = list
                elif factory_name == "dict":
                    factory = dict
                elif factory_name == "set":
                    factory = set
                elif factory_name == "int":
                    factory = int
                else:
                    factory = None
                
                result = defaultdict(factory)
                args = cached_get_args(e_type)
                if len(args) >= 2:
                    key_type, val_type = args[0], args[1]
                    for k, v in data.items():
                        # 杂鱼♡～转换键和值的类型喵～
                        converted_key = convert_value(f"{key}.key", k, key_type) if key_type != str else k
                        converted_val = convert_value(f"{key}[{k}]", v, val_type)
                        result[converted_key] = converted_val
                else:
                    result.update(data)
                return result
            elif isinstance(value, dict):
                args = cached_get_args(e_type)
                if len(args) >= 2:
                    key_type, val_type = args[0], args[1]
                    result = defaultdict()
                    for k, v in value.items():
                        converted_key = convert_value(f"{key}.key", k, key_type) if key_type != str else k
                        converted_val = convert_value(f"{key}[{k}]", v, val_type)
                        result[converted_key] = converted_val
                    return result
                else:
                    return defaultdict(lambda: None, value)
            return value
        elif e_type is defaultdict:
            if isinstance(value, dict) and value.get("__type__") == "defaultdict":
                data = value["__data__"]
                factory_name = value.get("__default_factory__")
                
                if factory_name == "list":
                    factory = list
                elif factory_name == "dict":
                    factory = dict
                elif factory_name == "set":
                    factory = set
                elif factory_name == "int":
                    factory = int
                else:
                    factory = None
                
                result = defaultdict(factory)
                result.update(data)
                return result
            elif isinstance(value, dict):
                return defaultdict(lambda: None, value)
            return value
        
        return convert_simple_type(key, value, e_type)


# // 杂鱼♡～本喵添加了这个函数来检查一个dataclass是否是frozen的喵～
def is_frozen_dataclass(cls):
    """Check if a dataclass is frozen."""
    return (
        is_dataclass(cls)
        and hasattr(cls, "__dataclass_params__")
        and getattr(cls.__dataclass_params__, "frozen", False)
    )


def convert_dict_to_dataclass(data: dict, cls: T) -> T:
    """Convert a dictionary to a dataclass instance."""
    if not data:
        raise ValueError("Empty data dictionary")

    # 杂鱼♡～无论是否为frozen dataclass，都使用构造函数方式创建实例喵～这样更安全～
    init_kwargs = {}
    t_hints = get_cached_type_hints(cls)

    for key, value in data.items():
        if key in t_hints:
            e_type = t_hints.get(key)
            if e_type is not None:
                init_kwargs[key] = convert_value(key, value, e_type)
        else:
            raise ValueError(f"Unknown data key: {key}")

    return cls(**init_kwargs)


# 杂鱼♡～本喵添加了一个快速的 dataclass 检查函数喵～
def fast_is_dataclass(obj) -> bool:
    """杂鱼♡～本喵的快速 dataclass 检查，带缓存喵～"""
    obj_type = type(obj)
    
    # 杂鱼♡～检查缓存喵～
    if obj_type in _DATACLASS_CACHE:
        return _DATACLASS_CACHE[obj_type]
    
    # 杂鱼♡～计算并缓存结果喵～
    result = is_dataclass(obj)
    _DATACLASS_CACHE[obj_type] = result
    return result


# 杂鱼♡～本喵创建了类型映射表，避免长长的if-elif链条喵～
_TYPE_TO_STRING_MAP = {
    datetime.datetime: "datetime",
    datetime.date: "date",
    datetime.time: "time", 
    datetime.timedelta: "timedelta",
    uuid.UUID: "uuid",
    Decimal: "decimal",
    tuple: "tuple",
    set: "set",
    frozenset: "frozenset",
    list: "list",
    dict: "dict",
    deque: "deque",
    defaultdict: "defaultdict",
}

# 杂鱼♡～本喵创建了简单序列化处理器映射表喵～
_SIMPLE_SERIALIZERS = {
    "datetime": lambda obj: obj.isoformat(),
    "date": lambda obj: obj.isoformat(),
    "time": lambda obj: obj.isoformat(),
    "timedelta": lambda obj: obj.total_seconds(),
    "uuid": lambda obj: str(obj),
    "decimal": lambda obj: str(obj),
    "enum": lambda obj: obj.name,
    "flag": lambda obj: obj.value,
}

# 杂鱼♡～本喵创建了反序列化转换器映射表喵～
_TYPE_DESERIALIZERS = {
    datetime.datetime: lambda value: datetime.datetime.fromisoformat(value) if isinstance(value, str) else None,
    datetime.date: lambda value: datetime.date.fromisoformat(value) if isinstance(value, str) else None,
    datetime.time: lambda value: datetime.time.fromisoformat(value) if isinstance(value, str) else None,
    uuid.UUID: lambda value: uuid.UUID(value) if isinstance(value, str) else None,
}

# 杂鱼♡～本喵添加了一个快速类型检查函数喵～
def get_special_type(obj) -> str:
    """杂鱼♡～本喵快速检查对象的特殊类型喵～返回类型字符串或空字符串～"""
    obj_type = type(obj)
    
    # 杂鱼♡～检查缓存喵～
    if obj_type in _SPECIAL_TYPE_CACHE:
        return _SPECIAL_TYPE_CACHE[obj_type]
    
    # 杂鱼♡～首先检查映射表，比if-elif更快喵～
    result = _TYPE_TO_STRING_MAP.get(obj_type)
    if result is not None:
        _SPECIAL_TYPE_CACHE[obj_type] = result
        return result
    
    # 杂鱼♡～处理需要继承检查的特殊情况喵～
    if issubclass(obj_type, (Flag, IntFlag)):
        result = "flag"  # 杂鱼♡～专门为Flag/IntFlag类型添加支持喵～
    elif issubclass(obj_type, Enum):
        result = "enum"
    else:
        result = ""
    
    _SPECIAL_TYPE_CACHE[obj_type] = result
    return result


def convert_dataclass_to_dict(
    obj: Any, parent_key: str = "", parent_type: Any = None
) -> Any:
    """Convert a dataclass instance to a dictionary."""
    if obj is None:
        return None

    # 杂鱼♡～快速检查基本类型，直接返回喵～
    obj_type = type(obj)
    if obj_type in (int, float, str, bool):
        return obj

    # 杂鱼♡～本喵用快速类型检查来减少 isinstance 调用喵～
    special_type = get_special_type(obj)
    
    # 杂鱼♡～优先使用映射表处理简单序列化，比if-elif更高效喵～
    simple_serializer = _SIMPLE_SERIALIZERS.get(special_type)
    if simple_serializer is not None:
        return simple_serializer(obj)
    
    if special_type == "tuple":
        # 杂鱼♡～对于元组，转换为列表返回喵～
        return [
            convert_dataclass_to_dict(
                item,
                f"{parent_key}[]",
                (
                    cached_get_args(parent_type)[0]
                    if parent_type and cached_get_args(parent_type)
                    else None
                ),
            )
            for item in obj
        ]
    elif special_type == "frozenset":
        # 杂鱼♡～frozenset 需要特殊处理，转换为带类型标记的字典喵～
        element_type = None
        if parent_type and cached_get_origin(parent_type) is frozenset and cached_get_args(parent_type):
            element_type = cached_get_args(parent_type)[0]

        result = []
        for i, item in enumerate(obj):
            # 杂鱼♡～验证元素类型喵～
            if element_type:
                item_key = f"{parent_key or 'frozenset'}[{i}]"
                try:
                    validate_type(item_key, item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for frozenset element type: {item_key} {str(e)}"
                    )

            result.append(
                convert_dataclass_to_dict(item, f"{parent_key}[{i}]", element_type)
            )

        # 杂鱼♡～返回带类型标记的字典，方便反序列化时恢复喵～
        return {
            "__type__": "frozenset",
            "__data__": result
        }
    elif special_type == "deque":
        # 杂鱼♡～deque 需要保存 maxlen 信息喵～
        element_type = None
        if parent_type and hasattr(parent_type, '__origin__') and parent_type.__origin__ is deque:
            args = cached_get_args(parent_type)
            if args:
                element_type = args[0]

        result = []
        for i, item in enumerate(obj):
            result.append(
                convert_dataclass_to_dict(item, f"{parent_key}[{i}]", element_type)
            )

        return {
            "__type__": "deque",
            "__data__": result,
            "__maxlen__": obj.maxlen
        }
    elif special_type == "defaultdict":        
        key_type, val_type = None, None
        if parent_type and hasattr(parent_type, '__origin__') and parent_type.__origin__ is defaultdict:
            args = cached_get_args(parent_type)
            if len(args) >= 2:
                key_type, val_type = args[0], args[1]

        result = {}
        for k, v in obj.items():
            # 杂鱼♡～首先验证键和值的类型喵～
            if key_type:
                key_validation_name = f"{parent_key or 'defaultdict'}.key"
                try:
                    validate_type(key_validation_name, k, key_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for defaultdict key type: {key_validation_name} {str(e)}"
                    )
            
            if val_type:
                val_validation_name = f"{parent_key or 'defaultdict'}[{k}]"
                try:
                    validate_type(val_validation_name, v, val_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for defaultdict value type: {val_validation_name} {str(e)}"
                    )
            
            # 杂鱼♡～将键转换为字符串以支持JSON序列化喵～
            # JSON只支持字符串键，所以本喵需要将其他类型的键转换为字符串～
            if isinstance(k, Enum):
                # 杂鱼♡～枚举键需要特殊处理喵～
                if isinstance(k, (Flag, IntFlag)):
                    # 杂鱼♡～Flag/IntFlag 使用数值作为键喵～
                    json_key = str(k.value)
                else:
                    # 杂鱼♡～普通枚举使用名称作为键喵～
                    json_key = k.name
            else:
                json_key = str(k)
            result[json_key] = convert_dataclass_to_dict(
                v, f"{parent_key}[{k}]", val_type
            )

        # 杂鱼♡～尝试获取默认工厂类型喵～
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
            "__data__": result,
            "__default_factory__": default_factory_name
        }
    elif special_type == "set":
        # 杂鱼♡～需要检查集合中元素的类型喵～
        element_type = None
        if parent_type and cached_get_origin(parent_type) is set and cached_get_args(parent_type):
            element_type = cached_get_args(parent_type)[0]

        result = []
        for i, item in enumerate(obj):
            # 杂鱼♡～为了测试能通过，本喵还是要验证元素类型喵～
            if element_type:
                item_key = f"{parent_key or 'set'}[{i}]"
                try:
                    validate_type(item_key, item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for set element type: {item_key} {str(e)}"
                    )

            result.append(
                convert_dataclass_to_dict(item, f"{parent_key}[{i}]", element_type)
            )

        return result
    elif special_type == "list":
        # 杂鱼♡～需要检查列表中元素的类型喵～
        element_type = None
        if parent_type and cached_get_origin(parent_type) is list and cached_get_args(parent_type):
            element_type = cached_get_args(parent_type)[0]

        result = []
        for i, item in enumerate(obj):
            # 杂鱼♡～为了测试能通过，本喵还是要验证元素类型喵～
            if element_type:
                item_key = f"{parent_key or 'list'}[{i}]"
                try:
                    validate_type(item_key, item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for list element type: {item_key} {str(e)}"
                    )

            result.append(
                convert_dataclass_to_dict(item, f"{parent_key}[{i}]", element_type)
            )

        return result
    elif special_type == "dict":
        # 杂鱼♡～需要检查字典中键和值的类型喵～
        key_type, val_type = None, None
        if (
            parent_type
            and cached_get_origin(parent_type) is dict
            and len(cached_get_args(parent_type)) == 2
        ):
            key_type, val_type = cached_get_args(parent_type)

        result = {}
        for k, v in obj.items():
            # 杂鱼♡～为了测试能通过，本喵还是要验证键值类型喵～
            if key_type:
                key_name = f"{parent_key or 'dict'}.key"
                try:
                    validate_type(key_name, k, key_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for dict key type: {key_name} {str(e)}"
                    )

            if val_type:
                val_key = f"{parent_key or 'dict'}[{k}]"
                try:
                    validate_type(val_key, v, val_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for dict value type: {val_key} {str(e)}"
                    )

            # 杂鱼♡～将键转换为字符串以支持JSON序列化喵～
            # JSON只支持字符串键，所以本喵需要将其他类型的键转换为字符串～
            if isinstance(k, Enum):
                # 杂鱼♡～枚举键需要特殊处理喵～
                if isinstance(k, (Flag, IntFlag)):
                    # 杂鱼♡～Flag/IntFlag 使用数值作为键喵～
                    json_key = str(k.value)
                else:
                    # 杂鱼♡～普通枚举使用名称作为键喵～
                    json_key = k.name
            else:
                json_key = str(k)
            result[json_key] = convert_dataclass_to_dict(
                v, f"{parent_key}[{k}]", val_type
            )

        return result

    # 杂鱼♡～检查 dataclass，但用缓存版本喵～
    if fast_is_dataclass(obj):
        result = {}
        t_hints = get_cached_type_hints(type(obj))
        for key, value in vars(obj).items():
            e_type = t_hints.get(key)

            # 杂鱼♡～为了测试能通过，本喵还是要验证字段类型喵～
            if e_type is not None:
                field_key = f"{parent_key}.{key}" if parent_key else key
                try:
                    validate_type(field_key, value, e_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Serialization failed for field type: {field_key} {str(e)}"
                    )

            # 杂鱼♡～转换值为字典喵～递归时传递字段类型～
            result[key] = convert_dataclass_to_dict(
                value, f"{parent_key}.{key}" if parent_key else key, e_type
            )
        return result
    return obj
