"""杂鱼♡～这是本喵全新设计的类型处理器系统喵～采用插件式架构，再也不怕混乱了～"""

import abc
import datetime
import uuid
from collections import defaultdict, deque
from dataclasses import is_dataclass
from decimal import Decimal
from enum import Enum, IntEnum, Flag, IntFlag
from typing import Any, Union, get_args, get_origin, Literal, List

from .types import T
from .validator import get_cached_type_hints, validate_type


class TypeHandler(abc.ABC):
    """杂鱼♡～类型处理器基类，所有类型处理器都要继承这个喵～"""
    
    @abc.abstractmethod
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        """杂鱼♡～检查是否能处理这个类型喵～"""
        pass
    
    @abc.abstractmethod
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        """杂鱼♡～序列化对象喵～"""
        pass
    
    @abc.abstractmethod
    def deserialize(self, data: Any, target_type: Any) -> Any:
        """杂鱼♡～反序列化数据喵～"""
        pass


class BasicTypeHandler(TypeHandler):
    """杂鱼♡～处理基本类型的处理器喵～"""
    
    BASIC_TYPES = (int, float, str, bool, type(None))
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        return isinstance(obj, self.BASIC_TYPES) or target_type in self.BASIC_TYPES
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        return obj
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        if target_type is type(None) or data is None:
            return None
        
        # 杂鱼♡～进行严格的类型验证，不允许任何自动转换喵～
        if target_type in self.BASIC_TYPES:
            # 杂鱼♡～只接受完全匹配的类型，不进行任何转换喵～
            if not isinstance(data, target_type):
                raise TypeError(f"Expected {target_type.__name__} type, but got {type(data).__name__} type with value '{data}'")
            return data
        
        return data


class EnumHandler(TypeHandler):
    """杂鱼♡～处理所有枚举类型的处理器喵～包括Enum、IntEnum、Flag、IntFlag～"""
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        return (isinstance(obj, (Enum, IntEnum, Flag, IntFlag)) or 
                (isinstance(target_type, type) and issubclass(target_type, (Enum, IntEnum, Flag, IntFlag))))
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        if isinstance(obj, (Flag, IntFlag)):
            # 杂鱼♡～Flag和IntFlag序列化为整数值喵～
            return obj.value
        elif isinstance(obj, (Enum, IntEnum)):
            # 杂鱼♡～普通枚举序列化为名称喵～
            return obj.name
        return obj
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        if not isinstance(target_type, type) or not issubclass(target_type, (Enum, IntEnum, Flag, IntFlag)):
            return data
            
        if issubclass(target_type, (Flag, IntFlag)):
            # 杂鱼♡～Flag和IntFlag从整数值创建喵～
            if isinstance(data, int):
                return target_type(data)
            elif isinstance(data, str) and data.isdigit():
                return target_type(int(data))
        elif issubclass(target_type, (Enum, IntEnum)):
            # 杂鱼♡～普通枚举从名称创建喵～
            if isinstance(data, str):
                try:
                    return target_type[data]
                except KeyError:
                    # 杂鱼♡～尝试从值创建喵～
                    for enum_member in target_type:
                        if enum_member.value == data:
                            return enum_member
                    raise ValueError(f"Cannot find enum value {data} corresponding to {target_type} member")
            else:
                # 杂鱼♡～尝试从值创建喵～
                return target_type(data)
        
        return data


class DateTimeHandler(TypeHandler):
    """杂鱼♡～处理日期时间类型的处理器喵～"""
    
    DATETIME_TYPES = (datetime.datetime, datetime.date, datetime.time, datetime.timedelta)
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        return isinstance(obj, self.DATETIME_TYPES) or target_type in self.DATETIME_TYPES
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()  
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        return obj
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        if target_type == datetime.datetime and isinstance(data, str):
            try:
                return datetime.datetime.fromisoformat(data)
            except ValueError as e:
                raise ValueError(f"Cannot parse datetime string '{data}': {str(e)}")
        elif target_type == datetime.date and isinstance(data, str):
            try:
                return datetime.date.fromisoformat(data)
            except ValueError as e:
                raise ValueError(f"Cannot parse date string '{data}': {str(e)}")
        elif target_type == datetime.time and isinstance(data, str):
            try:
                return datetime.time.fromisoformat(data)
            except ValueError as e:
                raise ValueError(f"Cannot parse time string '{data}': {str(e)}")
        elif target_type == datetime.timedelta and isinstance(data, (int, float)):
            return datetime.timedelta(seconds=data)
        elif target_type == datetime.timedelta and isinstance(data, dict):
            return datetime.timedelta(**data)
        return data


class SpecialTypeHandler(TypeHandler):
    """杂鱼♡～处理UUID、Decimal等特殊类型的处理器喵～"""
    
    SPECIAL_TYPES = (uuid.UUID, Decimal)
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        return isinstance(obj, self.SPECIAL_TYPES) or target_type in self.SPECIAL_TYPES
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, Decimal):
            return str(obj)
        return obj
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        if target_type == uuid.UUID and isinstance(data, str):
            return uuid.UUID(data)
        elif target_type == Decimal and isinstance(data, (str, int, float)):
            return Decimal(str(data))
        return data


class CollectionHandler(TypeHandler):
    """杂鱼♡～处理集合类型的处理器喵～包括list、set、frozenset、deque、tuple～"""
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        if isinstance(obj, (list, set, frozenset, deque, tuple)):
            return True
        
        origin = get_origin(target_type)
        if origin in (list, set, frozenset, tuple) or target_type in (list, set, frozenset, tuple):
            return True
        
        # 杂鱼♡～检查deque类型喵～
        if hasattr(target_type, '__origin__') and target_type.__origin__ is deque:
            return True
        if target_type is deque:
            return True
        
        return False
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        if isinstance(obj, (set, frozenset)):
            # 杂鱼♡～集合序列化为带标记的格式喵～
            serialized_items = []
            for item in obj:
                serialized_items.append(TypeHandlerRegistry.serialize(item))
            return {
                "__type__": "frozenset" if isinstance(obj, frozenset) else "set",
                "__data__": serialized_items
            }
        elif isinstance(obj, tuple):
            # 杂鱼♡～元组序列化为带标记的格式喵～
            serialized_items = []
            for item in obj:
                serialized_items.append(TypeHandlerRegistry.serialize(item))
            return {
                "__type__": "tuple",
                "__data__": serialized_items
            }
        elif isinstance(obj, deque):
            # 杂鱼♡～deque序列化为带标记的格式喵～
            serialized_items = []
            for item in obj:
                serialized_items.append(TypeHandlerRegistry.serialize(item))
            return {
                "__type__": "deque",
                "__data__": serialized_items,
                "__maxlen__": obj.maxlen
            }
        elif isinstance(obj, list):
            return [TypeHandlerRegistry.serialize(item) for item in obj]
        
        return obj
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        # 杂鱼♡～首先验证数据格式是否与目标类型匹配喵～
        origin = get_origin(target_type)
        
        # 杂鱼♡～如果目标类型是集合类型，但数据不是合适的格式，抛出异常喵～
        if origin in (list, set, frozenset, tuple) or target_type in (list, set, frozenset, tuple):
            # 杂鱼♡～对于集合类型，数据应该是列表或带__type__标记的字典喵～
            if not isinstance(data, list) and not (isinstance(data, dict) and "__type__" in data):
                raise TypeError(f"Expected {target_type} type, but got {type(data).__name__} type with value '{data}'")
        
        # 杂鱼♡～处理带类型标记的数据喵～
        if isinstance(data, dict) and "__type__" in data:
            collection_type = data["__type__"]
            items_data = data["__data__"]
            
            # 杂鱼♡～获取类型参数喵～
            args = get_args(target_type)
            
            # 杂鱼♡～转换每个元素喵～
            converted_items = []
            
            if collection_type == "tuple" and args:
                # 杂鱼♡～对于tuple，每个位置可能有不同的类型喵～
                for i, item_data in enumerate(items_data):
                    if i < len(args):
                        # 杂鱼♡～使用对应位置的类型喵～
                        element_type = args[i]
                    else:
                        # 杂鱼♡～如果索引超出，使用最后一个类型（通常是...）或Any喵～
                        element_type = args[-1] if args else Any
                    converted_items.append(TypeHandlerRegistry.deserialize(item_data, element_type))
            else:
                # 杂鱼♡～对于其他集合类型，所有元素使用相同类型喵～
                element_type = args[0] if args else Any
                for item_data in items_data:
                    converted_items.append(TypeHandlerRegistry.deserialize(item_data, element_type))
            
            # 杂鱼♡～根据类型创建相应的集合喵～
            if collection_type == "set":
                return set(converted_items)
            elif collection_type == "frozenset":
                return frozenset(converted_items)
            elif collection_type == "tuple":
                return tuple(converted_items)
            elif collection_type == "deque":
                maxlen = data.get("__maxlen__")
                return deque(converted_items, maxlen=maxlen)
        
        # 杂鱼♡～处理普通列表数据喵～
        elif isinstance(data, list):
            origin = get_origin(target_type)
            args = get_args(target_type)
            
            # 杂鱼♡～转换每个元素喵～
            converted_items = []
            
            if (origin is tuple or target_type is tuple) and args:
                # 杂鱼♡～对于tuple，每个位置可能有不同的类型喵～
                for i, item_data in enumerate(data):
                    if i < len(args):
                        # 杂鱼♡～使用对应位置的类型喵～
                        element_type = args[i]
                    else:
                        # 杂鱼♡～如果索引超出，使用最后一个类型（通常是...）或Any喵～
                        element_type = args[-1] if args else Any
                    converted_items.append(TypeHandlerRegistry.deserialize(item_data, element_type))
            else:
                # 杂鱼♡～对于其他集合类型，所有元素使用相同类型喵～
                element_type = args[0] if args else Any
                for item_data in data:
                    converted_items.append(TypeHandlerRegistry.deserialize(item_data, element_type))
            
            # 杂鱼♡～根据目标类型创建相应的集合喵～
            if origin is set or target_type is set:
                return set(converted_items)
            elif origin is frozenset or target_type is frozenset:
                return frozenset(converted_items)
            elif origin is tuple or target_type is tuple:
                return tuple(converted_items)
            elif origin is deque or target_type is deque:
                return deque(converted_items)
            elif origin is list or target_type is list:
                return converted_items
        
        return data


class DictHandler(TypeHandler):
    """杂鱼♡～处理字典类型的处理器喵～包括dict和defaultdict～"""
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        # 杂鱼♡～只有当目标类型真的是字典类型时才处理喵～
        origin = get_origin(target_type)
        if origin is dict or target_type is dict:
            return True
        
        # 杂鱼♡～检查defaultdict类型喵～
        if hasattr(target_type, '__origin__') and target_type.__origin__ is defaultdict:
            return True
        if target_type is defaultdict:
            return True
        
        # 杂鱼♡～对于序列化，可以处理字典对象喵～
        if isinstance(obj, (dict, defaultdict)) and target_type is None:
            return True
        
        return False
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        if isinstance(obj, defaultdict):
            # 杂鱼♡～defaultdict需要特殊处理喵～
            result = {}
            for key, value in obj.items():
                str_key = str(key)
                result[str_key] = TypeHandlerRegistry.serialize(value)
            
            # 杂鱼♡～保存default_factory信息喵～
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
        elif isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                str_key = str(key)
                result[str_key] = TypeHandlerRegistry.serialize(value)
            return result
        
        return obj
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        if not isinstance(data, dict):
            return data
        
        # 杂鱼♡～处理defaultdict喵～
        if isinstance(data, dict) and data.get("__type__") == "defaultdict":
            default_factory_name = data.get("__default_factory__")
            items_data = data["__data__"]
            
            # 杂鱼♡～重建默认工厂喵～
            default_factory = None
            if default_factory_name == "list":
                default_factory = list
            elif default_factory_name == "dict":
                default_factory = dict
            elif default_factory_name == "set":
                default_factory = set
            elif default_factory_name == "int":
                default_factory = int
            
            # 杂鱼♡～获取键值类型喵～
            origin = get_origin(target_type)
            args = get_args(target_type)
            key_type = args[0] if len(args) > 0 else str
            value_type = args[1] if len(args) > 1 else Any
            
            # 杂鱼♡～重建defaultdict喵～
            result = defaultdict(default_factory)
            for str_key, value_data in items_data.items():
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
                
                converted_value = TypeHandlerRegistry.deserialize(value_data, value_type)
                result[converted_key] = converted_value
            
            # 杂鱼♡～关键修复：如果目标类型是普通Dict，返回普通dict；否则返回defaultdict喵～
            if origin is dict or target_type is dict:
                return dict(result)  # 杂鱼♡～转换为普通字典喵～
            else:
                return result  # 杂鱼♡～保持为defaultdict喵～
        
        # 杂鱼♡～处理普通字典喵～
        origin = get_origin(target_type)
        args = get_args(target_type)
        
        # 杂鱼♡～获取键和值的类型喵～
        key_type = args[0] if len(args) > 0 else str
        value_type = args[1] if len(args) > 1 else Any
        
        result = {}
        for str_key, value in data.items():
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
            converted_value = TypeHandlerRegistry.deserialize(value, value_type)
            result[converted_key] = converted_value
        
        return result


class DataclassHandler(TypeHandler):
    """杂鱼♡～处理dataclass类型的处理器喵～"""
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        return is_dataclass(obj) or is_dataclass(target_type)
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        if not is_dataclass(obj):
            return obj
        
        result = {}
        type_hints = get_cached_type_hints(type(obj))
        
        for field_name, field_value in vars(obj).items():
            field_type = type_hints.get(field_name)
            
            # 杂鱼♡～序列化前进行类型验证喵～
            if field_type:
                try:
                    self._validate_field_type(field_name, field_value, field_type)
                except TypeError as e:
                    raise TypeError(f"Field '{field_name}' type validation failed: {str(e)}")
            
            result[field_name] = TypeHandlerRegistry.serialize(field_value, field_type)
        
        return result
    
    def _validate_field_type(self, field_name: str, value: Any, expected_type: Any) -> None:
        """杂鱼♡～验证字段类型是否匹配喵～"""
        try:
            validate_type(field_name, value, expected_type)
        except TypeError as e:
            # 杂鱼♡～重新抛出TypeError以便上层捕获喵～
            raise e
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        if not isinstance(data, dict) or not is_dataclass(target_type):
            return data
        
        type_hints = get_cached_type_hints(target_type)
        init_kwargs = {}
        
        for field_name, field_value in data.items():
            if field_name in type_hints:
                field_type = type_hints[field_name]
                init_kwargs[field_name] = TypeHandlerRegistry.deserialize(field_value, field_type)
            else:
                init_kwargs[field_name] = field_value
        
        return target_type(**init_kwargs)


class LiteralHandler(TypeHandler):
    """杂鱼♡～处理Literal类型的处理器喵～"""
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        origin = get_origin(target_type)
        return origin is Literal
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        return obj
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        # 杂鱼♡～验证值是否在Literal允许的值中喵～
        args = get_args(target_type)
        if data in args:
            return data
        else:
            raise ValueError(f"Value {data} is not in the allowed values of Literal {args}")


class UnionHandler(TypeHandler):
    """杂鱼♡～处理Union类型的处理器喵～"""
    
    def can_handle(self, obj: Any, target_type: Any) -> bool:
        origin = get_origin(target_type)
        return origin is Union
    
    def serialize(self, obj: Any, target_type: Any = None) -> Any:
        return TypeHandlerRegistry.serialize(obj)
    
    def deserialize(self, data: Any, target_type: Any) -> Any:
        args = get_args(target_type)
        
        # 杂鱼♡～处理None值喵～
        if data is None and type(None) in args:
            return None
        
        # 杂鱼♡～尝试每种可能的类型喵～
        # 杂鱼♡～优先尝试非None类型，这样可以更好地处理Optional[DataClass]喵～
        non_none_types = [arg for arg in args if arg is not type(None)]
        
        for arg_type in non_none_types:
            try:
                # 杂鱼♡～现在Registry级别有递归保护，可以安全地调用喵～
                result = TypeHandlerRegistry.deserialize(data, arg_type)
                return result
            except Exception as e:
                # 杂鱼♡～继续尝试下一个类型喵～
                continue
        
        # 杂鱼♡～如果都失败了，返回原始数据喵～
        return data


class TypeHandlerRegistry:
    """杂鱼♡～类型处理器注册表，管理所有类型处理器喵～"""
    
    _handlers: List[TypeHandler] = []
    _initialized = False
    
    @classmethod
    def _initialize(cls):
        """杂鱼♡～初始化默认处理器喵～"""
        if cls._initialized:
            return
        
        # 杂鱼♡～注册顺序很重要，越具体的处理器越靠前喵～
        cls._handlers = [
            EnumHandler(),
            DateTimeHandler(),
            SpecialTypeHandler(),
            LiteralHandler(),
            DataclassHandler(),
            CollectionHandler(),
            DictHandler(),
            UnionHandler(),
            BasicTypeHandler(),  # 杂鱼♡～基本类型处理器放最后喵～
        ]
        cls._initialized = True
    
    @classmethod
    def register_handler(cls, handler: TypeHandler):
        """杂鱼♡～注册新的类型处理器喵～"""
        cls._initialize()
        cls._handlers.insert(0, handler)  # 杂鱼♡～新处理器优先级更高喵～
    
    @classmethod
    def serialize(cls, obj: Any, target_type: Any = None) -> Any:
        """杂鱼♡～序列化对象喵～"""
        cls._initialize()
        
        for handler in cls._handlers:
            if handler.can_handle(obj, target_type):
                return handler.serialize(obj, target_type)
        
        # 杂鱼♡～没有处理器能处理，返回原始对象喵～
        return obj
    
    @classmethod
    def deserialize(cls, data: Any, target_type: Any) -> Any:
        """杂鱼♡～反序列化数据喵～"""
        cls._initialize()
        
        for handler in cls._handlers:
            if handler.can_handle(data, target_type):
                return handler.deserialize(data, target_type)
        
        # 杂鱼♡～没有处理器能处理，返回原始数据喵～
        return data 