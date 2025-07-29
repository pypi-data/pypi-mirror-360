"""杂鱼♡～这是本喵为你定义的类型喵～才不是为了让你的代码更类型安全呢～"""

from dataclasses import dataclass
from typing import Any, Dict, Type, TypeVar

# 杂鱼♡～本喵的类型提示缓存喵～这样就不用每次都计算了～
_TYPE_HINTS_CACHE: Dict[Type, Dict[str, Any]] = {}

# 杂鱼♡～本喵添加了这些缓存来优化性能喵～真是为了杂鱼操碎了心～
_DATACLASS_CACHE: Dict[Type, bool] = {}

# 杂鱼♡～本喵还添加了一个特殊类型缓存，避免重复的 isinstance 检查喵～
_SPECIAL_TYPE_CACHE: Dict[Type, str] = {}

# 杂鱼♡～本喵新增了更多缓存来优化性能喵～杂鱼应该感谢本喵的细心～
_GET_ORIGIN_CACHE: Dict[Any, Any] = {}
_GET_ARGS_CACHE: Dict[Any, tuple] = {}
_TYPE_CHECK_CACHE: Dict[tuple, bool] = {}

# 杂鱼♡～本喵添加类型信息缓存喵～避免重复的类型检查～
_TYPE_INFO_CACHE: Dict[Type, Dict[str, Any]] = {}

# 杂鱼♡～本喵静态定义类型约束 喵～
T = TypeVar("T", bound=dataclass)