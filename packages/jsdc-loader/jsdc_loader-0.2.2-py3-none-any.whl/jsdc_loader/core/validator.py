"""杂鱼♡～这是本喵的验证工具喵～本喵可是非常严格的，不会让杂鱼传入错误的类型呢～"""

import inspect
from dataclasses import is_dataclass
from enum import Enum
from typing import Any, Dict, List, Set, Tuple, Type, Union, get_args, get_origin

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from .types import _TYPE_HINTS_CACHE, _GET_ORIGIN_CACHE, _GET_ARGS_CACHE


# 杂鱼♡～本喵添加了缓存版本的 get_origin 和 get_args 喵～
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


def get_cached_type_hints(cls: Type) -> Dict[str, Any]:
    """杂鱼♡～本喵用缓存来获取类型提示，这样速度更快喵～"""
    if cls not in _TYPE_HINTS_CACHE:
        from typing import get_type_hints
        
        try:
            # 杂鱼♡～尝试正常获取类型提示喵～
            _TYPE_HINTS_CACHE[cls] = get_type_hints(cls)
        except (NameError, AttributeError) as e:
            # 杂鱼♡～如果前向引用失败，使用原始注解作为后备喵～
            # 这通常发生在函数内部定义的类有前向引用时喵～
            try:
                # 杂鱼♡～尝试从调用栈中获取正确的命名空间喵～
                frame = inspect.currentframe()
                # 向上查找几层栈帧，寻找包含所需类定义的作用域
                for _ in range(10):  # 最多查找10层
                    frame = frame.f_back
                    if frame is None:
                        break
                    
                    # 杂鱼♡～尝试在当前帧的局部和全局命名空间中解析类型提示喵～
                    try:
                        _TYPE_HINTS_CACHE[cls] = get_type_hints(cls, frame.f_globals, frame.f_locals)
                        break
                    except (NameError, AttributeError):
                        continue
                else:
                    # 杂鱼♡～如果所有尝试都失败，使用原始注解喵～
                    _TYPE_HINTS_CACHE[cls] = getattr(cls, '__annotations__', {})
            except Exception:
                # 杂鱼♡～最后的后备方案喵～
                _TYPE_HINTS_CACHE[cls] = getattr(cls, '__annotations__', {})
    
    return _TYPE_HINTS_CACHE[cls]


def validate_dataclass(cls: Any) -> None:
    """杂鱼♡～本喵帮你验证提供的类是否为dataclass或BaseModel喵～杂鱼总是分不清这些～"""
    if not cls:
        raise TypeError("data_class cannot be None")
    if not (is_dataclass(cls)):
        raise TypeError("data_class must be a dataclass")


def validate_type(key: str, value: Any, e_type: Any) -> None:
    """杂鱼♡～本喵帮你验证值是否匹配预期类型喵～本喵很擅长发现杂鱼的类型错误哦～"""
    # 杂鱼♡～对于Any类型，本喵不做任何检查喵～它可以是任何类型～
    if e_type is Any:
        return

    # 杂鱼♡～先做快速的简单类型检查，这是最常见的情况喵～
    # 但是要特别小心bool和int的关系，因为bool是int的子类喵～
    value_type = type(value)
    if e_type in (int, float, str, bool, list, dict, set, tuple) and e_type is value_type:
        return
    
    # 杂鱼♡～特别处理bool和int的混淆问题喵～
    # 如果期望类型是int但值是bool，或者期望类型是bool但值是int，都要报错喵～
    if e_type is int and value_type is bool:
        raise TypeError(
            f"Invalid type for key {key}: expected <class 'int'>, got <class 'bool'> - bool cannot be used as int"
        )
    elif e_type is bool and value_type is int:
        raise TypeError(
            f"Invalid type for key {key}: expected <class 'bool'>, got <class 'int'> - int cannot be used as bool"
        )

    o_type = cached_get_origin(e_type)

    # 杂鱼♡～对于Union类型，本喵需要特殊处理喵～
    if o_type is Union:
        # 如果值是None且Union包含Optional（即None类型），那么就是合法的喵～
        if value is None and type(None) in cached_get_args(e_type):
            return

        # 对于非None值，我们需要检查它是否匹配Union中的任何类型喵～
        args = cached_get_args(e_type)
        # 杂鱼♡～这里不使用isinstance检查，而是尝试递归验证每种可能的类型喵～
        valid = False
        for arg in args:
            if arg is type(None) and value is None:
                valid = True
                break
            try:
                # 递归验证，如果没有抛出异常就是有效的喵～
                validate_type(key, value, arg)
                valid = True
                break
            except (TypeError, ValueError):
                # 继续尝试下一个类型喵～
                continue

        if not valid:
            raise TypeError(
                f"Invalid type for key {key}: expected {e_type}, got {type(value)} - you cannot even tell the type"
            )

    # 杂鱼♡～对于列表类型，本喵需要检查容器类型和内容类型喵～
    elif o_type is list or o_type is List:
        if not isinstance(value, list):
            raise TypeError(
                f"Invalid type for key {key}: expected list, got {type(value)} - you are a fool"
            )

        # 杂鱼♡～检查列表元素类型喵～
        args = cached_get_args(e_type)
        if args:
            element_type = args[0]
            for i, item in enumerate(value):
                try:
                    validate_type(f"{key}[{i}]", item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Invalid type for list {key} at index {i}: {str(e)}"
                    )

    # 杂鱼♡～对于集合类型，本喵也需要检查内容类型喵～
    elif o_type is set or o_type is Set:
        if not isinstance(value, set):
            raise TypeError(
                f"Invalid type for key {key}: expected set, got {type(value)} - you are a fool"
            )

        # 杂鱼♡～检查集合元素类型喵～
        args = cached_get_args(e_type)
        if args:
            element_type = args[0]
            for i, item in enumerate(value):
                try:
                    validate_type(f"{key}[{i}]", item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(f"Invalid type for set {key}: {str(e)}")

    # 杂鱼♡～对于字典类型，本喵需要检查键和值的类型喵～
    elif o_type is dict:
        if not isinstance(value, dict):
            raise TypeError(
                f"Invalid type for key {key}: expected dict, got {type(value)} - you are a fool"
            )

        # 杂鱼♡～检查字典键和值的类型喵～
        args = cached_get_args(e_type)
        if len(args) == 2:
            key_type, val_type = args
            for k, v in value.items():
                try:
                    validate_type(f"{key}.key", k, key_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(f"Invalid type for dictionary {key} key: {str(e)}")

                try:
                    validate_type(f"{key}[{k}]", v, val_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(f"Invalid type for dictionary {key} value: {str(e)}")

    # 杂鱼♡～对于元组类型，本喵也需要特殊处理喵～
    elif o_type is tuple or o_type is Tuple:
        if not isinstance(value, tuple):
            raise TypeError(
                f"Invalid type for key {key}: expected tuple, got {type(value)}"
            )

        args = cached_get_args(e_type)
        if not args:
            # 无类型参数的元组，只检查是否为元组类型
            pass
        elif len(args) == 2 and args[1] is Ellipsis:
            # Tuple[X, ...] 形式，所有元素都应该是同一类型
            element_type = args[0]
            for i, item in enumerate(value):
                try:
                    validate_type(f"{key}[{i}]", item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Invalid type for tuple {key} at index {i}: {str(e)}"
                    )
        else:
            # Tuple[X, Y, Z] 形式，长度和类型都固定
            if len(value) != len(args):
                raise TypeError(
                    f"Invalid length for tuple {key}: expected {len(args)}, got {len(value)}"
                )

            for i, (item, arg_type) in enumerate(zip(value, args)):
                try:
                    validate_type(f"{key}[{i}]", item, arg_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Invalid type for tuple {key} at index {i}: {str(e)}"
                    )

    # 杂鱼♡～对于Literal类型，需要特殊处理喵～
    elif o_type is Literal:
        # 杂鱼♡～检查值是否在Literal允许的值中喵～
        args = cached_get_args(e_type)
        if value not in args:
            raise TypeError(
                f"Invalid value for key {key}: expected one of {args}, got {value}"
            )
        return

    # 杂鱼♡～对于其他复杂类型，如List、Dict等，本喵需要检查origin喵～
    elif o_type is not None:
        # 杂鱼♡～对于列表、字典等容器类型，只需检查容器类型，不检查内容类型喵～
        # 杂鱼♡～但要排除不能用于isinstance的类型喵～
        try:
            if not isinstance(value, o_type):
                raise TypeError(
                    f"Invalid type for key {key}: expected {o_type}, got {type(value)}"
                )
        except TypeError as e:
            # 杂鱼♡～如果isinstance失败，可能是特殊类型，跳过检查喵～
            if "cannot be used with isinstance()" in str(e):
                return
            else:
                raise

    # 杂鱼♡～对于简单类型，直接使用isinstance喵～
    else:
        # 对于Enum类型，我们需要特殊处理喵～
        if isinstance(e_type, type) and issubclass(e_type, Enum):
            if not isinstance(value, e_type):
                # 对于已经是枚举实例的验证喵～
                if isinstance(value, str) and hasattr(e_type, value):
                    # 字符串值匹配枚举名，可以接受喵～
                    return
                raise TypeError(
                    f"Invalid type for key {key}: expected {e_type}, got {type(value)}"
                )
        elif e_type is not Any:
            # 杂鱼♡～对于可能不支持isinstance的类型，使用try-except处理喵～
            try:
                if not isinstance(value, e_type):
                    raise TypeError(
                        f"Invalid type for key {key}: expected {e_type}, got {type(value)}"
                    )
            except TypeError as e:
                # 杂鱼♡～如果isinstance失败，可能是特殊的类型注解喵～
                if "isinstance()" in str(e) and ("must be a type" in str(e) or "cannot be used with isinstance" in str(e)):
                    # 杂鱼♡～对于不支持isinstance的类型，跳过检查喵～
                    return
                else:
                    raise
